import re
import imaplib

import email
import base64

from myloguru.my_loguru import get_logger


class MailReader:
    def __init__(self, email: str, password: str, logger=None, log_level: int = 20) -> None:
        self.login: str = email
        self.password: str = password
        self.logger = logger or get_logger(log_level)
        self.data: list = []
        server: str = 'imap.' + email.strip().split('@')[-1]
        self.imap: 'imaplib.IMAP4_SSL' = imaplib.IMAP4_SSL(server)

    @staticmethod
    def _b64_pad_and_decode(b: bytes) -> str:
        """Decode unpadded base64 data"""

        b += (-len(b) % 4) * '='
        return base64.b64decode(b, altchars='+,', validate=True).decode('utf-16-be')

    @staticmethod
    def _imap_utf7_decode(string: str) -> str:
        """Decode a string encoded according to RFC2060 aka IMAP UTF7.

        Minimal validation of input, only works with trusted data"""
        lst = string.split('&')
        out = lst[0]
        for e in lst[1:]:
            u, a = e.split('-', 1)
            if u == '':
                out += '&'
            else:
                out += MailReader._b64_pad_and_decode(u)
            out += a
        return out

    @staticmethod
    def _imap_utf7_encode(string: str) -> str:
        """"Encode a string into RFC2060 aka IMAP UTF7"""

        string = string.replace('&', '&-')
        unipart = out = ''
        for c in string:
            if 0x20 <= ord(c) <= 0x7f:
                if unipart != '':
                    out += '&' + base64.b64encode(unipart.encode('utf-16-be')).decode('ascii').rstrip('=') + '-'
                    unipart = ''
                out += c
            else:
                unipart += c
        if unipart != '':
            out += '&' + base64.b64encode(unipart.encode('utf-16-be')).decode('ascii').rstrip('=') + '-'
        return out

    def reader_login(self) -> None:
        self.imap.login(self.login, self.password)

    def reader_logout(self) -> None:
        self.imap.logout()

    def read_folder(self, folder) -> None:
        self.imap.select(self._imap_utf7_encode(folder))
        result, data = self.imap.uid('search', '', 'ALL')
        if data:
            self.data = data[0].split()[::-1]

    def get_link_from_last_email(self) -> str:
        self.read_folder('inbox')
        new_count = 0
        for uid in self.data:
            try:
                uid = int(uid.decode('utf-8'))
                new_count += 1
                result, msg = self.imap.uid('fetch', str(uid), '(RFC822)')
                if not msg[0]:
                    continue
                mail = email.message_from_bytes(msg[0][1])
                body = ''
                if mail.is_multipart():
                    for payload in mail.get_payload():
                        if payload.get_content_maintype() == 'text':
                            body = payload.get_payload(decode=True).decode('utf-8', 'ignore')
                else:
                    body = mail.get_payload(decode=True).decode('utf-8', 'ignore')

                search = re.search(r'<a href="(https://click\.discord\.com.[^"]*?)".[^>]*?>([^<:]*?)</a>', body)
                result: str = search.group(1)

            except Exception as err:
                self.logger.error(err)
                result = f'error: {err}'

            self.logger.debug(f'MailReader result: {result}')
            return result

    def start(self) -> str:
        try:
            self.reader_login()
            link: str = self.get_link_from_last_email()
            self.reader_logout()
        except Exception as err:
            link: str = f'error: {err}'

        return link
