# omnifact_cli/config.py

import os
import configparser
from pathlib import Path

CONFIG_FILE = Path.home() / '.omnifact_cli.ini'

def get_api_key():
    if 'OMNIFACT_API_KEY' in os.environ:
        return os.environ['OMNIFACT_API_KEY']
    
    if CONFIG_FILE.exists():
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)
        return config.get('DEFAULT', 'api_key', fallback=None)
    
    return None

def get_connect_url():
    if 'OMNIFACT_CONNECT_URL' in os.environ:
        return os.environ['OMNIFACT_CONNECT_URL']
    
    if CONFIG_FILE.exists():
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)
        return config.get('DEFAULT', 'connect_url', fallback='https://connect.omnifact.ai')
    
    return 'https://connect.omnifact.ai'

def set_api_key(api_key):
    config = configparser.ConfigParser()
    if CONFIG_FILE.exists():
        config.read(CONFIG_FILE)
    config['DEFAULT']['api_key'] = api_key
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)

def set_connect_url(connect_url):
    config = configparser.ConfigParser()
    if CONFIG_FILE.exists():
        config.read(CONFIG_FILE)
    config['DEFAULT']['connect_url'] = connect_url
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)