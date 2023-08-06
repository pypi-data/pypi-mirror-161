# -*- coding: utf-8 -*-
import random

VERSION = '0.1.9'
BUILD_TIME = '2022/07/31'

DEBUG = False
UPLOAD_OVERRIDE_MODE = False
UPLOAD = False
BIND_IP = '0.0.0.0'
BIND_PORT = 2000
ROOT = '.'
STRING = None

VIDEO_SUFFIX = ['mp4', 'flv', 'hls', 'dash', 'mkv']
VIDEO_CDN_JS = {
    'flv': '/static/flv.min.js',
    'hls': '/static/hls.js@latest',
    'dash': '/static/dash.all.min.js',
    'mp4': '',
    'mkv': ''
}

ALLOW_TREE = None
BLOCK_TREE = None

PROJECTS_PATH = ''
GIT_REPOS_PATH = ''
GIT_PATH = ''
GIT_SERVICE = False
USER_NAME = 'admin'
PASSWORD = ''.join([chr(random.randint(33, 126)) for _ in range(16)])


def debug_msg(args):
    cfg = args.__dict__
    keys = sorted(cfg.keys())
    msg = ['=' * 45]
    for k in keys:
        v = cfg[k]
        tmp = k + ' ' * (22 - len(k)) + '=' + ' ' * 12
        if not isinstance(v, (list, tuple, set)):
            tmp += str(v)
        else:
            if isinstance(v, set):
                v = tuple(v)
            if len(v) == 0:
                _ = 'None'
            elif len(v) == 1:
                _ = str(v[0])
            else:
                _ = (',\n' + ' ' * 35).join(str(__) for __ in v)
            tmp += _
        msg.append(tmp)
    msg.append('=' * 45)
    return '\n'.join(msg)
