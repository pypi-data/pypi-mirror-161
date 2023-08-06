import os
import rsa
from bs4 import BeautifulSoup
import requests
import re
import hashlib
import oe_common
from ovcrypt import cfg

public_key_file = cfg['rsa_server_public_key_file']
private_key_file = cfg['rsa_server_private_key_file']


def get_ip_hash(address):
    h = hashlib.sha1()
    for a in address:
        h.update(str(a).encode())
    return h.hexdigest()


class OvCrypt:
    class Key:
        def __init__(self, key):
            self.key = key
            self.auth = False
            self.t = 'public'
            self.verification_string = None

    def __init__(self, debug=None):
        self.public_key = None
        self.private_key = None
        self.debug = debug
        self.key_size = cfg['key_size']
        self.import_keys()

    def import_keys(self):
        if not (os.path.isfile(public_key_file) or os.path.isfile(private_key_file)):
            self.generate_keys()
        with open(public_key_file, 'rb') as f:
            public_key_data = f.read()
        with open(private_key_file, 'rb') as f:
            private_key_data = f.read()
        self.public_key = rsa.PublicKey.load_pkcs1(public_key_data)
        self.private_key = rsa.PrivateKey.load_pkcs1(private_key_data)

    def generate_keys(self):
        public, private = rsa.newkeys(self.key_size)
        public_exp = rsa.PublicKey.save_pkcs1(public)
        private_exp = rsa.PrivateKey.save_pkcs1(private)
        oe_common.check_create_dir(public_key_file, private_key_file)
        with open(public_key_file, 'wb') as f:
            f.write(public_exp)
        with open(private_key_file, 'wb') as f:
            f.write(private_exp)

    @staticmethod
    def ov_pad(s, length):
        return s + b'\x00' * (length - len(s))

    def get_master_keys(self):
        url = cfg['master_keys_url']
        page = requests.get(url).text
        # print(f'page: {page}')
        soup = BeautifulSoup(page, 'html.parser')
        list_keys = [url + node.get('href') + 'ov_public.pub' for node in soup.findAll("a") if re.match(r'\w+\/', node['href'])]
        if self.debug:
            print(f'list: {list_keys}')
        ret_ar = []
        for key_link in list_keys:
            try:
                page = requests.get(key_link).text
                if self.debug:
                    print(page)
                ret_ar.append(rsa.PublicKey.load_pkcs1(page.encode()))
            except requests.exceptions.ConnectionError as e:
                # print(f'type: {type(e)}')
                # print(f'exception: {e}')
                if self.debug:
                    print(f'Can\'t load page: {key_link} (connection error)')
            except requests.exceptions.MissingSchema as e:
                if self.debug:
                    print(f'Cant load page: {key_link} (bad url)')
        return ret_ar


class OvSign:
    def __init__(self, key=None):
        self.key = key
        self.s_hash = b''

    def update_hash(self, part):
        updated_hash = rsa.compute_hash(self.s_hash + part, 'SHA-256')
        # print(f'hash len: {len(updated_hash)}')
        self.s_hash = updated_hash

    def get_verification_result(self, sign):
        # print(f'hash is: {self.s_hash}')
        try:
            rsa.verify(self.s_hash, sign, self.key)
        except rsa.pkcs1.VerificationError:
            print('verification error')
            return False
        return True

    def get_sign(self):
        # print(f'hash is: {self.s_hash}')
        return rsa.sign(self.s_hash, self.key, 'SHA-1')

    def get_hash(self):
        return self.s_hash


if __name__ == '__main__':
    cr = OvCrypt()
    mk = cr.get_master_keys()
    cr.import_keys()
    # print('\n\n\n\n')
    print(mk)
    # print('\n\n\n\n')
