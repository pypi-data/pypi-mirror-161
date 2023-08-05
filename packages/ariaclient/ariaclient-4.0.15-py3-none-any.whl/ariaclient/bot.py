#!/usr/bin/env python3
# coding: utf8

import argparse
import pathlib
import re
import importlib
import sys
from time import sleep
from requests.exceptions import HTTPError, RequestException, ConnectionError

import ariaclient.api
from ariaclient import AriaError, AriaService, SymphonyMessageML
from sys import modules as MODULES
import json
import logging

from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

CONFIG_REQUIRED=frozenset(['url', 'session', 'cert'])
MESSAGE_REQUIRED=frozenset(['text', 'channel', 'from'])

logging.basicConfig(format="%(asctime)-15s %(levelname)s-%(message)s",
                    level=logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S')


class AriaBot:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.config = kwargs['config']
        if 'aria' not in self.config:
            raise AttributeError('Missing aria section in config')
        self.env = self.config['aria']
        self._populate_commands()
        self._populate_entity_handlers()
        self.session = None
        self.aria = None
        self._delta_token = ''
        self.read_token_file = pathlib.Path(self.env.get('read_token_file', 'read_token_file.dat'))
        if not self.read_token_file.exists():
            logging.warning('Token file {0} doesnt exist, creating new file'.format(self.read_token_file.name))
            self.read_token_file.write_text('')

    def _populate_commands(self):
        if 'commands' not in self.config:
            logging.warning("No commands configured")
        else:
            for _cmd in self.config['commands']:
                flags = 0
                if 'flags' in _cmd:
                    flags = eval(_cmd['flags'])
                _cmd['pattern'] = re.compile(_cmd['pattern'], flags)
                # push the full config to all commands
                _cmd['config'] = self.config
                _module = None
                try:
                    if 'module' in _cmd:
                        _module = importlib.import_module(_cmd['module'])
                    else:
                        _module = MODULES[__name__]
                    _class = getattr(_module, _cmd['class'])
                    _cmd['bot'] = self
                    _class(**_cmd)
                except AttributeError as ae:
                    logging.warning('{} - ignoring command'.format(ae.args[0], _cmd['class']))

    def _populate_entity_handlers(self):
        if 'entities' not in self.config:
            logging.warning("No entities configured")
        else:
            for _ent in self.config['entities']:
                _module = None
                try:
                    if 'module' in _ent:
                        _module = importlib.import_module(_ent['module'])
                    else:
                        _module = MODULES[__name__]
                    _class = getattr(_module, _ent['class'])
                    _ent['bot'] = self
                    _class(**_ent)
                except AttributeError as ae:
                    logging.warning('{} - ignoring entity'.format(ae.args[0], _ent['class']))

    def _process_message(self, channel, msg, msg_id, attachments, msg_text):
        processed = False
        start = 0
        item = 1
        if not isinstance(attachments, list):
            attachments = None
        while start < len(msg_text):
            cmd, cmd_match = AriaBotCommand.match_command(msg_text, start)
            if not cmd_match:
                break
            processed = True
            cmd.do(match=cmd_match, message=msg, msg_id=msg_id, index=item, attachments=attachments, channel=channel)
            start = cmd_match.span()[1] + 1
            item = item + 1
        return processed

    def _process_entities(self, msg, data):
        processed = False
        item = 1
        # Check for "io.fincloud.biz.objectlist"
        obj_type = data.get('type', None)
        if obj_type == "io.fincloud.biz.objectlist":
            obj_list = data.get('list', None)
            obj_header = data.get('header', None)
        else:
            obj_list = [data]
            obj_header = None

        # Loop through all the entities in the message
        for entity in obj_list:
            # Check if there is a 'type' attribute on the entity and process.
            if isinstance(entity, dict) and 'type' in entity:
                handler = AriaBotEntityHandler.match_entity(entity['type'])
                if not handler:
                    logging.debug('Unmatched entity {}'.format(entity['type']))
                    continue
                handler.handle(entity=entity, message=msg, index=item, header=obj_header)
                processed = True
            item = item + 1
        return processed

    def start(self):
        logging.info('Starting ARIA Bot version[{0}] - python version [{1}'.format(ariaclient.__version__, sys.version))
        authenticated = False
        poll_retry = ariaclient.api.DEFAULT_POLL_RETRY
        timeout = ariaclient.api.DEFAULT_TIMEOUT
        system = self.config.get('system', None)
        if system and 'poll_retry' in system:
            poll_retry = int(system['poll_retry'])
        if system and 'timeout' in system:
            timeout = int(system['timeout'])
        if not CONFIG_REQUIRED.issubset(list(self.env.keys())):
            raise AriaBotException('Missing required attribute from: '+str(CONFIG_REQUIRED))

        cer = None
        try:
            cer = AriaService.read_cert(self.env['cert'])
            self._delta_token = self.read_token_file.read_text()
            logging.info('Resuming aria stream [{0}]'.format(self._delta_token))
        except AriaError as e:
            logging.error(e)
            sys.exit(1)

        self.aria = AriaService(
            self.env['url'],
            self.env['session'],
            timeout=timeout
        )
        self.session = None
        # cross_pod = ('cross_pod' in self.env and not self.env['cross_pod'])
        while True:
            # reset these on every iteration
            channel = None
            msg_text = ''
            msg = None
            try:
                if not authenticated:
                    self.aria.authenticate(cer)
                    self.session = self.aria.who_am_i()
                    authenticated = True

                for msg in self.aria.get_messages(delta_token=self._delta_token):
                    # Check the cross-pod flag and ignore message if not valid.
                    # if (not cross_pod) and msg['header']['crossPod']:
                    #    logging.debug('Ignore cross-pod message from [{}]'.format(msg['from']))
                    #    continue

                    logging.debug('Msg: {}'.format(str(msg)))
                    # Ignore everything except actual messages, or anonymous
                    if msg['type'] != 'MESSAGE_SENT' or 'email' not in msg['sender']:
                        continue
                    from_email = msg['sender']['email']
                    # if this message is from the bot skip to next message.
                    if from_email == self.session:
                        continue

                    msg_text = msg['text']
                    channel = from_email
                    if 'channel' in msg:
                        channel = msg['channel']['name']
                    payload = msg['payload']
                    processed_text = self._process_message(
                        channel,
                        payload.get('message', ''),
                        payload.get('messageId', ''),
                        msg['attachments'], msg_text
                    )
                    processed_entities = False
                    if 'data' in payload:
                        data = json.loads(payload['data'])
                        processed_entities = self._process_entities(msg, data)

                    if (not processed_text) and (not processed_entities):
                        logging.debug('Not matched {}'.format(msg_text))

            except (ValueError, AriaBotException) as ex:
                logging.error(ex.args[0])
                if msg is not None:
                    err_msg = SymphonyMessageML()
                    err_msg.root().text = '🤖 [{}]'.format(ex.args[0])
                    self.aria.send_message(channel, err_msg)

            except (KeyboardInterrupt, SystemExit) as exiting:
                logging.error('Exiting: {}'.format(exiting))
                break

            except HTTPError as hte:
                status = hte.response.status_code
                logging.error('Error: {} {}'.format(status, hte.response.text))
                if status == 401:
                    authenticated = False
                    sleep(1)
                elif status == 404:
                    # Datafeed not found - renewing
                    logging.warning(hte.response.text+' renewing datafeed')
                    # Blank the delta token for the next read, causing a refresh
                    self.aria.delta_token = ''
                    self._delta_token = ''
                elif status == 502:
                    logging.error('Gateway error: {} retry in {} seconds'.format(hte.response.status_code, poll_retry))
                    sleep(poll_retry)
                else:
                    logging.error('Error[{}] req[{}] res[{}] '.format(status, hte.request.body, hte.response.text))
                    if channel is not None:
                        err_msg = SymphonyMessageML()
                        err_msg.root().text = '🤖 [{}]'.format(msg_text)
                        self.aria.send_message(channel, err_msg)
                    sleep(poll_retry)

            except ConnectionError as ce:
                logging.error('Connection Error: {}'.format(ce))
                sleep(poll_retry)

            except RequestException as reqE:
                logging.error('Request Exception: {}'.format(reqE))
                sleep(poll_retry)
            # if aria client has a token value from a new session, then write this to disk
            if self.aria.delta_token != self._delta_token:
                self._delta_token = self.aria.delta_token
                self.read_token_file.write_text(self._delta_token)


class AriaBotCommand:

    _commands = []

    def __init__(self, **kwargs):
        self.bot = kwargs['bot']
        self.pattern = kwargs['pattern']
        self.name = kwargs['name']
        self.helptext = kwargs.get('helptext', None)
        self.config = kwargs['config']
        AriaBotCommand._commands.append(self)

    @staticmethod
    def match_command(msg_text, start):
        for cmd in AriaBotCommand._commands:
            match = cmd.pattern.match(msg_text, start)
            if match:
                return cmd, match
        return None, None

    def do(self, **kwargs):
        pass

    def simple_help(self):
        help_msg = SymphonyMessageML().bold('🤖: Here\'s a list of commands I understand')
        help_msg.hrule()
        for cmd in self._commands:
            if cmd.helptext is not None:
                help_msg = help_msg.bold(cmd.name).tail(' {} '.format(cmd.helptext)).tbreak()
            else:
                help_msg = help_msg.bold(cmd.name).tbreak()
        return help_msg


class AriaBotEntityHandler:

    _handlers = {}

    def __init__(self, **kwargs):
        self.bot = kwargs['bot']
        self.entity = kwargs['entity']
        self.name = kwargs['name']
        AriaBotEntityHandler._handlers[self.entity] = self

    @staticmethod
    def match_entity(entity):
        if entity in AriaBotEntityHandler._handlers.keys():
            return AriaBotEntityHandler._handlers[entity]
        else:
            return None

    def handle(self, **kwargs):
        pass


class AriaBotException(Exception):
    pass


__all__ = ['AriaBotException', 'AriaBot', 'AriaBotEntityHandler', 'AriaBotCommand']

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ARIA Bot Framework')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('configfile', help='configuration file')
    parser.add_argument('environment', help='environment, referenced in config section')
    args = parser.parse_args()

    allConfig = load(open(args.configfile, 'r'), Loader=Loader)

    if args.verbose:
        logging.basicConfig(format="%(asctime)-15s %(levelname)s-%(message)s",
                            level=logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S')
    else:
        logging.basicConfig(format="%(asctime)-15s %(message)s", level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
        logging.getLogger("requests").setLevel(logging.WARNING)

    _bot = AriaBot(config=allConfig, environment=args.environment)
    _bot.start()
