from os.path import abspath, dirname
from os.path import join as pj
from configparser import ConfigParser

PROJECT_PATH = dirname(abspath(__file__))
CONFIG = ConfigParser()
CONFIG.read(pj(PROJECT_PATH, '.env'))
