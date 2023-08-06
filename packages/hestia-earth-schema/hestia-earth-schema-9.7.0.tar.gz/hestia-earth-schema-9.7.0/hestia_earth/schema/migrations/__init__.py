import os
from os.path import abspath, dirname


CURRENT_DIR = dirname(abspath(__file__))


def list_migrations():
    files = list(filter(lambda f: not f.startswith('__'), os.listdir(CURRENT_DIR)))
    return list(map(lambda f: f.replace('.py', ''), files))
