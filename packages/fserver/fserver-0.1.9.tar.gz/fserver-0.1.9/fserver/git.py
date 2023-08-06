# ref: https://github.com/qhzhyt/http-git-server/blob/master/git.py
import os
import subprocess

from fserver import conf


def create_repo(repo_name):
    project_path = os.path.join(conf.PROJECTS_PATH, repo_name)
    git_repo_path = os.path.join(conf.GIT_REPOS_PATH, repo_name + '.git')

    cmds = [
        {
            'cwd': conf.GIT_REPOS_PATH,
            'cmd': [conf.GIT_PATH, 'clone', '--bare', project_path, repo_name + '.git']
        },
        # git config --global core.autocrlf true
        {
            'cwd': git_repo_path,
            'cmd': [conf.GIT_PATH, 'config', 'core.autocrlf', 'true']
        },
        # git config --global core.safecrlf false
        {
            'cwd': git_repo_path,
            'cmd': [conf.GIT_PATH, 'config', 'core.safecrlf', 'false']
        },
        # git config receive.denyCurrentBranch ignore
        {
            'cwd': git_repo_path,
            'cmd': [conf.GIT_PATH, 'config', 'receive.denyCurrentBranch', 'ignore']
        }
    ]
    for item in cmds:
        p = subprocess.Popen(' '.join(item.get('cmd')), cwd=item.get('cwd'), shell=True,
                             stderr=subprocess.PIPE)
        for line in p.stderr:
            yield line

    yield 'ok!'


def git_command(repo_name, *args):
    dir_name = os.path.join(conf.GIT_REPOS_PATH, repo_name)

    if not os.path.isdir(dir_name):
        for _ in create_repo(repo_name[:-4]):
            pass

    cmd = [conf.GIT_PATH, *args]
    env = os.environ.copy()
    env['PROJECT_DIR'] = os.path.join(conf.PROJECTS_PATH, repo_name[:-4])
    p = subprocess.Popen(' '.join(cmd), cwd=dir_name, env=env, shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)

    p.wait()
    out = p.stdout.read()

    return out


def git_command_with_input(repo_name, input_data, *args):
    dir_name = os.path.join(conf.GIT_REPOS_PATH, repo_name)

    if not os.path.isdir(dir_name):
        for _ in create_repo(repo_name[:-4]):
            pass
    env = os.environ.copy()
    cmd = [conf.GIT_PATH, *args]
    env['PROJECT_DIR'] = os.path.join(conf.PROJECTS_PATH, repo_name[:-4])
    p = subprocess.Popen(' '.join(cmd), cwd=dir_name, env=env, shell=True, stdout=subprocess.PIPE,
                         stdin=subprocess.PIPE)

    p.stdin.write(input_data)
    p.stdin.flush()
    for line in p.stdout:
        yield line
