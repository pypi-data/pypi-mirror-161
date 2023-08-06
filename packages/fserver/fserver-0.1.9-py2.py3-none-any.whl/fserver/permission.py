# -*- coding: utf-8 -*-

import re

from fserver import conf
from fserver.path_util import scandir


class PathNode(object):
    __slots__ = 'node', 'pattern', 'leaf', 'is_end'

    def __init__(self, node=None):
        self.node = node
        self.pattern = re.compile(node.replace('\\', r'\\')
                                  .replace(r'$', r'\$')
                                  .replace(r'(', r'\(')
                                  .replace(r')', r'\)')
                                  .replace(r'+', r'\+')
                                  .replace(r'.', r'\.')
                                  .replace(r'[', r'\[')
                                  .replace(r'?', r'\?')
                                  .replace(r'^', r'\^')
                                  .replace(r'{', r'\{')
                                  .replace(r'|', r'\|')
                                  .replace(r'*', r'.*') + '$') if node is not None else None
        self.leaf = dict()
        self.is_end = False

    def __str__(self):
        slf = self.node if self.node is not None else 'None'
        if self.is_end:
            slf += '@'
        if len(self.leaf) != 0:
            return '{}/({})'.format(slf, ', '.join(str(_) for _ in self.leaf.values()))
        else:
            return slf

    def __repr__(self):
        return "'{}'".format(self)


def build_path_tree(root, paths):
    head = PathNode(root.rstrip('/'))
    for path in paths:
        cur = head
        for node in path.rstrip('/').split('/'):
            if node not in cur.leaf:
                cur.leaf[node] = PathNode(node)
            cur = cur.leaf[node]
        cur.is_end = True
    return head if len(paths) != 0 else None


def match(tree: PathNode, paths, ix=0, match_dir=False):
    """
    :return: 0: no match, 1: match directory, 2: match to end
    """
    if ix == len(paths):
        if tree.is_end:
            return 2
        else:
            if match_dir:
                for entry in scandir('/'.join(paths)):
                    if entry.is_dir():
                        res = match(tree, paths + [entry.name], len(paths), True)
                        if res == 0 and tree.node == '**':
                            res = match(tree, paths + [entry.name], len(paths) + 1, True)
                        if res != 0:
                            return res
                    elif any(_.pattern.match(entry.name) and _.is_end for _ in tree.leaf.values()):
                        return 1
            return 0

    val = paths[ix]
    res = 0
    for key, node in tree.leaf.items():
        if res == 2 or (match_dir and res != 0):
            break
        if key == '**':
            for _ in reversed(range(ix, len(paths) + 1)):
                res = max(match(node, paths, _, match_dir), res)
                if res == 2 or (match_dir and res != 0):
                    break
        elif node.pattern.match(val):
            res = max(match(node, paths, ix + 1, match_dir), res)
    return res


def path_permission_deny(path, is_dir):
    """
    :param path: normalized path
    :param is_dir:
    :return:     preferred deny
    """
    DENY = True
    ALLOW = not DENY

    if path.startswith('./'):
        path = path[2:]

    if len(path) > 1 and path[-1] == '/':
        path = path.rstrip('/')

    if path == '' or path == 'favicon.ico':
        return ALLOW

    if path.startswith('../'):
        return DENY

    if conf.ALLOW_TREE is not None:
        res = match(conf.ALLOW_TREE, path.split('/'), match_dir=is_dir)
        if not (res == 2 or (is_dir and res != 0)):
            return DENY

    if conf.BLOCK_TREE is not None:
        res = match(conf.BLOCK_TREE, path.split('/'), match_dir=False)
        if res != 0:
            return DENY

    return ALLOW


def _test_match():
    data = """|          | */a2 | *1/a2 | b1/* | **/an | b1/** |
| -------- | ---- | ----- | ---- | ----- | ----- |
| a1/a2    | yes  | yes   |      |       |       |
| a1/an    |      |       |      | yes   |       |
| a1/a2/an |      |       |      | yes   |       |
| b1/a2    | yes  | yes   | yes  |       | yes   |
| b1/a2/an |      |       |      | yes   | yes   |
| an       |      |       |      | yes   |       |"""

    data = [line.strip().strip('|').split('|') for line in data.strip().split('\n')]
    pattern = [_.strip() for _ in data[0]]
    pattern = [_ for _ in pattern if len(_) != 0]
    fs = [line[0].strip() for line in data[2:]]
    fs = [_ for _ in fs if len(_) != 0]
    ans = [line[1:] for line in data[2:]]
    for i in ans:
        print(i)

    import os
    for f in fs:
        if not os.path.exists(f):
            os.makedirs(f)
    trees = [build_path_tree('./', [_]) for _ in pattern]
    print(trees)
    pred = [[match(t, f.split('/'), 0, False) for t in trees] for f in fs]

    for i in pred:
        print(i)

    assert all(
        [_ == 2 for _ in p] ==
        [_.strip() == 'yes' for _ in a]
        for p, a in zip(pred, ans))

    for f in sorted(fs, key=lambda _: -len(_)):
        if os.path.exists(f):
            os.removedirs(f)


if __name__ == '__main__':
    _test_match()
