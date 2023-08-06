# -*- coding: utf-8 -*-

import mimetypes
import os
from functools import wraps

from flask import Flask, request, redirect, jsonify
from flask import render_template, make_response, Response
from flask import send_from_directory
from flask_httpauth import HTTPBasicAuth
from markupsafe import Markup

from fserver import conf
from fserver.bean import GetArg
from fserver.conf import VIDEO_CDN_JS, VIDEO_SUFFIX
from fserver.git import git_command, git_command_with_input
from fserver.path_util import get_filename
from fserver.path_util import get_suffix
from fserver.path_util import listdir
from fserver.path_util import normalize_path
from fserver.path_util import parent_path
from fserver.path_util import secure_filename
from fserver.path_util import to_unicode_str
from fserver.path_util import url_path_to_local_abspath
from fserver.permission import path_permission_deny
from fserver.util import debug, warning

try:
    from urllib.parse import unquote, quote
except:
    from urllib import unquote, quote

app = Flask(__name__, template_folder='templates')

auth = HTTPBasicAuth()


@auth.verify_password
def authenticate(username, password):
    return username == conf.USER_NAME and password == conf.PASSWORD


def normalize_url(fun):
    @wraps(fun)
    def wrapper(path):
        original_url = to_unicode_str(request.environ['PATH_INFO'])
        n_url = normalize_path(original_url)

        if original_url.endswith('/'):
            n_url += '/'

        if n_url.startswith('..'):
            warning('attempt to access parent directory: {}'.format(path))
            return resp_deny(path)

        if original_url != n_url:
            re_url = n_url if request.environ['QUERY_STRING'] == '' else '?'.join(
                (n_url, request.environ['QUERY_STRING']))
            return redirect(re_url)
        else:
            return fun(path)

    return wrapper


@app.route('/', defaults={'path': ''}, methods=['GET'])
@app.route('/<path:path>', methods=['GET'])
@normalize_url
def do_get(path):
    arg = GetArg(request.args)

    debug('do_get: path %s,' % path, 'arg is', arg.to_dict())

    is_dir = os.path.isdir(path)

    if path_permission_deny(path, is_dir):
        warning('permission deny: %s' % path)
        return resp_deny(path)

    if path == '' or path == '/':
        return get_root(arg)

    if is_dir:
        if path.endswith('/'):
            return list_dir(path, arg)
        else:
            return redirect('/'.join((path, arg.format_for_url())))

    elif os.path.isfile(path):
        if is_curl_or_wget():
            return respond_file(path)
        elif arg.mode == GetArg.MODE_TXT:
            return respond_file(path, mime='text/plain')
        elif arg.mode == GetArg.MODE_DOWN:
            return respond_file(path, as_attachment=True)
        elif arg.mode == GetArg.MODE_VIDEO:
            return play_video(path, arg)
        else:
            if get_suffix(path).lower() in VIDEO_SUFFIX:
                return play_video(path, arg)
            else:
                return respond_file(path)

    return resp_deny(path)


@app.route('/', defaults={'path': ''}, methods=['POST'])
@app.route('/<path:path>', methods=['POST'])
@normalize_url
def do_post(path):
    debug('do_post: %s' % path)

    if path == '' or path == '/':
        path = './'

    is_dir = os.path.isdir(path)
    if not conf.UPLOAD or not is_dir:
        return redirect(request.url)

    if path_permission_deny(path, is_dir):
        warning('permission deny: %s' % path)
        return resp_deny(path)

    try:
        if 'file' not in request.files:
            warning('do_post: No file in request')
            return redirect(request.url)
        else:
            request_file = request.files['file']
            filename = secure_filename(request_file.filename)
            local_path = os.path.join(path, filename)
            if os.path.exists(local_path):
                if not conf.UPLOAD_OVERRIDE_MODE:
                    local_path = plus_filename(local_path)
            request_file.save(local_path)
            state = 'succeed' if os.path.exists(local_path) else 'failed'
            debug('save file to: {}, state: {}'.format(local_path, state))
            res = {'operation': 'upload_file', 'state': state, 'filename': request_file.filename}
            return jsonify(**res)

    except Exception as e:
        warning('do_post : ', e)
        return render_template('error.html', error=e)


@app.route('/<string:repo_name>/git-upload-pack', methods=['POST'])
def git_upload_pack(repo_name):
    if not conf.GIT_SERVICE or not is_git():
        return do_get('{}/git-upload-pack'.format(repo_name))

    repo_name = repo_name if repo_name.endswith('.git') else repo_name + '.git'
    args = ['upload-pack', "--stateless-rpc", '.']
    res = git_command_with_input(repo_name, request.data, *args)

    return Response(res)


@app.route('/<string:repo_name>/git-receive-pack', methods=['POST'])
@auth.login_required
def git_receive_pack(repo_name):
    # push
    if not conf.GIT_SERVICE or not is_git():
        return do_get('{}/git-receive-pack'.format(repo_name))

    repo = repo_name if repo_name.endswith('.git') else repo_name + '.git'
    args = ['receive-pack', "--stateless-rpc", '.']
    res = git_command_with_input(repo, request.data, *args)
    return Response(res)


@app.route('/<string:repo_name>/info/refs', methods=['GET'])
def git_info_refs(repo_name):
    if not conf.GIT_SERVICE or not is_git():
        return do_get('{}/info/refs'.format(repo_name))

    repo_name = repo_name if repo_name.endswith('.git') else repo_name + '.git'

    service = request.args.get('service')

    if service and 'git-' in service:
        service_name = service[4:]
    else:
        service_name = 'upload-pack'

    if service_name == 'receive-pack' and not auth.username():
        # push
        return auth.login_required(git_info_refs)(repo_name)

    args = [service_name, "--stateless-rpc", "--advertise-refs", "."]

    res = git_command(repo_name, *args)

    first_line = '# service=git-%s\n0000' % service_name
    first_line = ('%.4x' % len(first_line)) + first_line

    resp = make_response(first_line + res.decode())
    resp.headers['Content-Type'] = 'application/x-git-%s-advertisement' % service_name
    return resp


def get_root(arg):
    if conf.STRING is not None:
        if is_curl_or_wget():
            return conf.STRING
        return render_template('string.html', content=conf.STRING)
    else:
        return list_dir('./', arg)


def list_dir(path, arg):
    debug('list_dir:', path)
    local_path = url_path_to_local_abspath(path)
    if not os.path.isdir(local_path):
        return resp_deny(path)

    if not path.endswith('/'):
        path += '/'
    lst = []
    for entry in listdir(local_path):
        f = entry.name
        if path_permission_deny(path + f, entry.is_dir()):
            continue
        if entry.is_dir():
            f += '/'
        lst.append(f)

    if local_path != conf.ROOT:
        lst.append('../')
    lst.sort()
    if is_curl_or_wget():
        lst.append('')
        return '\n'.join(lst)
    return render_template('list.html',
                           upload=conf.UPLOAD,
                           path='/' if path == './' else '/%s' % path,
                           arg=arg.format_for_url(),
                           list=lst)


def respond_file(path, mime=None, as_attachment=False):
    debug('respond_file:', path)
    if os.path.isdir(path):
        return do_get(path)
    local_path = url_path_to_local_abspath(path)
    if mime is None or mime not in mimetypes.types_map.values():  # invalid mime
        mime = mimetypes.guess_type(local_path)[0]
        if mime is None:  # use text/plain as default
            mime = 'text/plain'
    if mime in ('text/html', ''):
        mime = 'text/plain'
    return send_from_directory(parent_path(local_path),
                               get_filename(local_path),
                               mimetype=mime,
                               as_attachment=as_attachment)


def play_video(path, arg):
    debug('play_video:', path)
    if os.path.isdir(url_path_to_local_abspath(path)):
        return do_get(path)

    suffix = get_suffix(path).lower()
    if arg.play is not None:
        t = arg.play
    elif suffix in VIDEO_SUFFIX:
        t = suffix
    else:
        t = 'auto'

    if t in VIDEO_CDN_JS.keys():
        tj = VIDEO_CDN_JS[t]
        tjs = tuple()
    else:
        tj = ''
        tjs = tuple(_ for _ in VIDEO_CDN_JS.values() if _ != '')
    return render_template('video.html',
                           name=get_filename(path),
                           url='/%s?%s=%s' % (urlencode_filter(path), GetArg.ARG_MODE, GetArg.MODE_DOWN),
                           type=t,
                           typejs=tj,
                           typejss=tjs)


def resp_deny(path):
    if is_curl_or_wget():
        return 'Invalid url: {}\n'.format(path)
    return render_template('error.html', error='Invalid url: %s' % path)


def plus_filename(filename):
    ind = -1 if '.' not in filename else filename.rindex('.')
    prefix = filename[:ind] if ind >= 0 else filename
    suffix = get_suffix(filename)
    i = 0
    while True:
        i += 1
        if suffix != '':
            res = '{}({}).{}'.format(prefix, i, suffix)
        else:
            res = '{}({})'.format(prefix, i)
        if not os.path.exists(res):
            return res


def is_curl_or_wget():
    ag = request.headers.get('User-Agent')
    ag = ag.lower().split('/')[0]
    return ag in ('curl', 'wget')


def is_git():
    ag = request.headers.get('User-Agent')
    ag = ag.lower().split('/')[0]
    return ag == 'git'


@app.template_filter('urlencode')
def urlencode_filter(s):
    if type(s) == Markup:
        s = s.unescape()
    s = s.encode('utf8')
    s = quote(s)
    return Markup(s)
