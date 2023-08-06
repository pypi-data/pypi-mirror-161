import os
from ovcfg import Config


sc = {
    'rsa_server_public_key_file': os.path.join('/var/lib/overengine', 'keys', 'ov_public.pub'),
    'rsa_server_private_key_file': os.path.join('/var/lib/overengine', 'keys', 'ov_private.pem'),
    'key_size': 2048,
    'master_keys_url': 'http://example.com/master_keys'
}
cfg_class = Config(std_config=sc, file='ovcrypt.json', cfg_dir_name='overengine')
cfg = cfg_class.import_config()
