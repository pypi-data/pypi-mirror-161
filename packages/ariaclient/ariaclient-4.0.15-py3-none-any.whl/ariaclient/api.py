import logging, base64, io
import requests
import shutil
import mimetypes
from lxml import etree
import json
import pathlib

DEFAULT_TRANSPORT = 'Symphony'
DEFAULT_POLL_RETRY = 30
DEFAULT_TIMEOUT = 60


class AriaService:
    def __init__(self, base_url, session_id, **kwargs):
        self._base_url = base_url
        self._token = None
        self.delta_token = ''
        self._paging_token = None
        self._session_id = session_id
        self._timeout_default = 30 if 'timeout' not in kwargs else int(kwargs['timeout'])
        self._headers = {'content-type':'application/json'}

    def _process_aria_message(self, data, attribute=None):
        if 'detail' in data:
            detail = data['detail']
            if detail is not None and attribute in detail:
                return detail.get(attribute)
            else:
                return detail
        else:
            raise AriaError('Unrecognised server response', data)

    def authenticate_app(self, key):
        token = self._authenticate('appKey', key)
        self._headers['Authorization'] = 'Bearer {}'.format(token)

    def authenticate(self, key):
        token = self._authenticate('userKey', key)
        self._headers['Authorization'] = 'Bearer {}'.format(token)

    def _authenticate(self, keyType, key):
        data = {
            "session": self._session_id,
            "credentials": [{'transport': 'Symphony', keyType: key.decode('utf-8')}]
        }
        res = requests.post(
            self._base_url+'/auth',
            json=data,
            headers={'content-type': 'application/json'}
        )
        res.raise_for_status()
        return self._process_aria_message(res.json(), 'token')

    def get_messages(self, delta_token=None):
        if delta_token is not None:
            self.delta_token = delta_token
        res = requests.get(
            self._base_url+'/message',
            headers=self._headers,
            timeout=self._timeout_default,
            params={'deltaToken': self.delta_token, 'isSubscription': True}
        )
        res.raise_for_status()
        data = res.json()
        if 'deltaToken' in data:
            self.delta_token = data.get('deltaToken')
        retval = self._process_aria_message(data)
        if retval is None:
            return []
        else:
            return retval

    def search_messages(self, data, timeout=None, limit=1000):
        timeout = self._timeout_default if timeout is None else timeout

        res = requests.post(
            self._base_url+'/message/search',
            json=data,
            headers=self._headers,
            timeout=timeout,
            params={'limit': limit}
        )
        res.raise_for_status()
        return self._process_aria_message(res.json())

    def send_message(self, channel, raw_message, **kwargs):
        message = {"channel": channel, "payload": {}}
        data = None if 'data' not in kwargs else kwargs['data']
        if isinstance(data, str):
            data = json.loads(data)

        message = AriaService.set_text(message, raw_message, data)
        if 'attachment' in kwargs and kwargs['attachment'] is not None:
            if isinstance(kwargs['attachment'], tuple):
                filename, fdata = kwargs['attachment']
                message['attachments'] = []
                message['attachments'].append(
                    {'name': filename,
                     'data': base64.b64encode(fdata).decode(),
                     'content-type': mimetypes.guess_type(filename)}
                )
        if 'on_behalf' in kwargs and kwargs['on_behalf'] is not None:
            message['onBehalf'] = kwargs['on_behalf']
        return requests.post('{}/message'.format(self._base_url), json=message, headers=self._headers)

    def delete_message(self, id):
        payload = {"id": id}
        res = requests.delete('{}/message'.format(self._base_url), params=payload, headers=self._headers)
        res.raise_for_status()
        return res

    def get_user(self, user_id, id_type='id', admin=False):
        params = {id_type: user_id}
        if admin:
            params['admin'] = True
        res = requests.get(
            self._base_url+'/user', params=params,
            headers=self._headers,
            timeout=self._timeout_default
        )
        res.raise_for_status()
        return self._process_aria_message(res.json())

    def who_am_i(self):
        res = requests.get(
            self._base_url+'/user/session',
            headers=self._headers,
            timeout=self._timeout_default
        )
        res.raise_for_status()
        return self._process_aria_message(res.json(), 'email')

    def get_connections(self):
        res = requests.get(
            self._base_url+'/connection',
            headers=self._headers,
            timeout=self._timeout_default
        )
        res.raise_for_status()
        return self._process_aria_message(res.json())

    def add_connection(self, user, accept=None):
        data = {"user": user}
        if accept:
            data['accept'] = "true"
        elif not accept:
            data['accept'] = "false"

        res = requests.post(
            self._base_url+'/connection',
            headers=self._headers,
            json=data,
            timeout=self._timeout_default
        )
        res.raise_for_status()
        return self._process_aria_message(res.json())

    def get_room_details(self, room_id, id_type='id', limit=1):
        params = { id_type: room_id, 'limit': limit }
        res = requests.get(
            '{}/room'.format(self._base_url),
            params=params,
            headers=self._headers,
            timeout=self._timeout_default
        )
        if res.status_code == requests.codes.not_found:
            raise AriaError('RoomId {0} not found'.format(room_id), res)
        else:
            res.raise_for_status()

        return self._process_aria_message(res.json())

    def create_room(self, room_name, room_description):
        res = requests.post(
            '{}/room'.format(self._base_url),
            json={"name": room_name, "description": room_description},
            headers=self._headers,
            timeout=self._timeout_default
        )
        res.raise_for_status()
        return self._process_aria_message(res.json())

    '''Display all members of a room'''
    def get_room_members(self, room_name, **kwargs):
        params = {}
        if 'on_behalf' in kwargs and kwargs['on_behalf'] is not None:
            params['on_behalf'] = kwargs['on_behalf']

        res = requests.get(
            '{}/room/{}/member'.format(self._base_url, room_name),
            headers=self._headers,
            params=params,
            timeout=self._timeout_default
        )
        if res.status_code == requests.codes.not_found:
            raise AriaError('Room {0} not found'.format(room_name), res)
        else:
            res.raise_for_status()
        return self._process_aria_message(res.json())

    '''Add a member or list of members to a room'''
    def add_room_members(self, room_name, member_email, **kwargs):
        users = []
        if not isinstance(member_email, list):
            users.append(member_email)
        else:
            for user in member_email:
                users.append(user)

        data = {"email": users}
        if 'on_behalf' in kwargs and kwargs['on_behalf'] is not None:
            data['on_behalf'] = kwargs['on_behalf']

        res = requests.post(
            '{}/room/{}/member'.format(self._base_url, room_name),
            json=data,
            headers=self._headers,
            timeout=self._timeout_default
        )
        if res.status_code == requests.codes.not_found:
            raise AriaError('Room {0} not found'.format(room_name), res)
        else:
            res.raise_for_status()
        return self._process_aria_message(res.json())

    '''Remove a member or list of members from a room'''
    def remove_room_members(self, room_name, member_email, **kwargs):
        users = []
        if not isinstance(member_email, list):
            users.append(member_email)
        else:
            for user in member_email:
                users.append(user)

        data = {"email": users}
        if 'on_behalf' in kwargs and kwargs['on_behalf'] is not None:
            data['on_behalf'] = kwargs['on_behalf']

        res = requests.delete(
            '{}/room/{}/member'.format(self._base_url, room_name),
            params=data,
            headers=self._headers,
            timeout=self._timeout_default
        )
        if res.status_code == requests.codes.not_found:
            raise AriaError('Room {0} not found'.format(room_name), res)
        else:
            res.raise_for_status()
        return self._process_aria_message(res.json())

    def download_file(self, url, local_filename=None):
        if not local_filename:
            local_filename = url.split('/')[-1]
        r = requests.get(url, headers=self._headers, stream=True)
        r.raise_for_status()
        body = r.json()
        logging.debug('File: {}'.format(str(body)))
        with open(local_filename, 'wb') as f:
            bfile = io.BytesIO(base64.b64decode(body['message']))
            shutil.copyfileobj(bfile, f)
        return local_filename

    #    def send_stream_as_attachment(self, channel, attach, stream, disableEncoding=True, passthrough=True):

    @staticmethod
    def set_text(message, text, data=None):
        if isinstance(text, SymphonyMessageML):
            message['payload']['message'] = text.tostring()
        else:
            message['payload']['message'] = text
        if data is not None:
            message['payload']['data'] = json.dumps(data)
        return message

    @staticmethod
    def read_cert(filename):
        return AriaService.base64_encode_file(filename)

    @staticmethod
    def base64_encode_file(filename):
        if not pathlib.Path(filename).exists():
            raise AriaError('File {} does not exist'.format(filename), None)
        with open(filename,'rb') as f:
            return base64.b64encode(f.read())


class AriaError(Exception):
    def __init__(self, text, res):
        self.text = text
        self.response = res


class SymphonyMessageML:
    def __init__(self):
        self._root = etree.Element('messageML')

    def tostring(self):
        return etree.tostring(self._root).decode('utf-8')

    def root(self):
        return self._root

    def text(self, text):
        self._root[len(self._root)-1].text = text
        return self

    def tail(self, text):
        self._root[len(self._root)-1].tail = text
        return self

    def bold(self, text=None):
        _elem = etree.SubElement(self._root, 'b')
        if text is not None:
            _elem.text = text
        return self

    def span(self, text=None):
        _elem = etree.SubElement(self._root, 'span')
        if text is not None:
            _elem.text = text
        return self

    def paragraph(self, text=None):
        _elem = etree.SubElement(self._root, 'p')
        if text is not None:
            _elem.text = text
        return self

    def anchor(self, url=None):
        _elem = etree.SubElement(self._root, 'a')
        if url is not None:
            _elem.attrib['href'] = url
        return self

    def tbreak(self, text=None):
        _elem = etree.SubElement(self._root, 'br')
        if text is not None:
            _elem.text = text
        return self

    def hrule(self, text=None):
        _elem = etree.SubElement(self._root, 'hr')
        if text is not None:
            _elem.text = text
        return self

    def italic(self, text=None):
        _elem = etree.SubElement(self._root, 'i')
        if text is not None:
            _elem.text = text
        return self

    def __str__(self):
        return self.tostring()


__all__ = ['AriaService', 'SymphonyMessageML', 'AriaError']
