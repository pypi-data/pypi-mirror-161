# -*- coding: utf-8 -*-
import argparse
import os
import signal
import sys

import gevent
from gevent.pywsgi import WSGIServer

from fserver import conf
from fserver import path_util
from fserver import permission
from fserver import util
from fserver.fserver_app import app as application


def args():
    parser = argparse.ArgumentParser('fserver')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='run with debug mode')
    parser.add_argument('-u', '--upload', action='store_true',
                        help='run with upload file function')
    parser.add_argument('-o', '--override', action='store_true',
                        help='override mode for upload file')
    parser.add_argument('-i', '--ip', default=conf.BIND_IP,
                        help='ip address for listening, default {}'.format(conf.BIND_IP))
    parser.add_argument('-p', '--port', type=int, default=conf.BIND_PORT,
                        help='port for listening, default {}'.format(conf.BIND_PORT))
    parser.add_argument('-r', '--root', metavar='PATH', default=conf.ROOT,
                        help='root path for server, default current path')
    parser.add_argument('-a', '--allow', nargs='+', metavar='PATH', default=tuple(),
                        help='run with allow_list. Only [PATH ...] will be accessed')
    parser.add_argument('-b', '--block', nargs='+', metavar='PATH', default=tuple(),
                        help='run with block_list. [PATH ...] will not be accessed')
    parser.add_argument('-s', '--string', default=conf.STRING,
                        help='share string only')
    parser.add_argument('-v', '--version', action='store_true',
                        help='print version info')
    parser.add_argument('-g', '--git', action='store_true',
                        help='open git http service for project in root')
    parser.add_argument('--git_path', default='',
                        help='path for git executable file')
    parser.add_argument('--username', default=conf.USER_NAME,
                        help='username for git authentication')
    parser.add_argument('--password', default=conf.PASSWORD,
                        help='password for git authentication')
    return parser


def run_fserver():
    _conf = args().parse_args()
    _conf.root = path_util.normalize_path(_conf.root)

    if _conf.version:
        msg = 'fserver {} build at {}\nPython {}'.format(conf.VERSION, conf.BUILD_TIME, sys.version)
        print(msg)
        sys.exit(0)

    conf.DEBUG = _conf.debug
    conf.UPLOAD = _conf.upload
    conf.UPLOAD_OVERRIDE_MODE = _conf.override
    conf.BIND_IP = _conf.ip
    conf.BIND_PORT = _conf.port
    conf.STRING = _conf.string
    conf.ROOT = path_util.normalize_path(os.path.abspath(_conf.root))
    conf.GIT_SERVICE = _conf.git
    conf.GIT_REPOS_PATH = conf.ROOT
    conf.PROJECTS_PATH = conf.ROOT
    conf.GIT_PATH = _conf.git_path
    conf.USER_NAME = _conf.username
    conf.PASSWORD = _conf.password

    if conf.GIT_SERVICE and conf.GIT_PATH == '':
        cmd = None
        if os.name == 'nt':
            cmd = 'where git'
        elif os.name == 'posix':
            cmd = 'which git'
        if cmd is not None:
            conf.GIT_PATH = [_ for _ in os.popen(cmd).read().split('\n') if len(_) > 0][0]
    if conf.GIT_SERVICE and not os.path.isfile(conf.GIT_PATH):
        print('[WARN] invalid git path: {}'.format(conf.GIT_PATH))
        conf.GIT_SERVICE = False
    if conf.GIT_SERVICE and ' ' in conf.GIT_PATH:
        conf.GIT_PATH = '"{}"'.format(conf.GIT_PATH)

    trees = []
    lsts = []
    for __ in (_conf.allow, _conf.block):
        _lst = set()
        for _afn in __:
            _afn = path_util.url_path_to_local_abspath(_afn)
            if not _afn.startswith(conf.ROOT):
                continue
            _afn = _afn[len(conf.ROOT):]
            if len(_afn) == 0 or _afn.startswith('/'):  # make sure that `_afn` in `conf.ROOT`
                _lst.add(_afn[1:])
        trees.append(permission.build_path_tree(conf.ROOT, _lst))
        lsts.append(_lst)

    conf.ALLOW_TREE, conf.BLOCK_TREE = trees
    _conf.allow, _conf.block = trees

    allow_list, block_list = lsts
    u = allow_list & block_list
    if len(u) > 0:
        print(lsts)
        print('a path should not be in allow list and block list at the same time: \n{}'.format(list(u)))
        sys.exit(-1)

    try:
        os.chdir(conf.ROOT)
    except:
        print('invalid root: {}'.format(conf.ROOT))
        sys.exit(-1)

    if conf.STRING is not None:
        conf.ALLOW_TREE = permission.build_path_tree(conf.ROOT, [""])

    if conf.DEBUG:
        print(conf.debug_msg(_conf))

    print('fserver is available at following address:')
    if conf.BIND_IP == '0.0.0.0':
        print('\n'.join('  http://%s:%s' % (_ip, conf.BIND_PORT) for _ip in util.get_ip_v4()))
    else:
        print('  http://%s:%s' % (conf.BIND_IP, conf.BIND_PORT))
    if conf.GIT_SERVICE:
        print('[INFO] authentication for git:')
        print('[INFO] username: {}\n[INFO] password: {}'.format(conf.USER_NAME, conf.PASSWORD))

    gevent.signal_handler(signal.SIGINT, _quit)
    gevent.signal_handler(signal.SIGTERM, _quit)
    http_server = WSGIServer((conf.BIND_IP, int(conf.BIND_PORT)), application)
    http_server.serve_forever()


def _quit():
    print('Bye')
    sys.exit(0)


if __name__ == '__main__':
    run_fserver()
