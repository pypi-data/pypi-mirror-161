# -*- coding: utf-8 -*-

class GetArg(object):
    ARG_MODE = 'mode'
    ARG_PLAY = 'play_type'

    MODE_NORMAL = 'normal'
    MODE_TXT = 'txt'
    MODE_VIDEO = 'play'
    MODE_DOWN = 'down'
    MODES = (MODE_NORMAL, MODE_TXT, MODE_VIDEO, MODE_DOWN)

    PLAY_AUTO = 'auto'
    PLAY_MP4 = 'mp4'
    PLAY_FLV = 'flv'
    PLAY_HLS = 'hls'
    PLAY_DASH = 'dash'
    PLAYS = (PLAY_AUTO, PLAY_MP4, PLAY_FLV, PLAY_HLS, PLAY_DASH)

    __slots__ = 'mode', 'play'

    def __init__(self, request_arg=None):
        self.mode = None
        self.play = None
        if request_arg is not None:
            self.resolve_arg(request_arg)

    def resolve_arg(self, request_arg):
        self.mode = request_arg.get(self.ARG_MODE, default=None)
        if self.mode is not None and self.mode not in self.MODES:
            self.mode = self.MODE_NORMAL

        self.play = request_arg.get(self.ARG_PLAY)
        if self.play is not None and self.play not in self.PLAYS:
            self.play = self.PLAY_AUTO

    def format_for_url(self):
        args = []
        if self.mode in self.MODES:
            args.append(self.ARG_MODE + '=' + self.mode)
        if self.play in self.PLAYS:
            args.append(self.ARG_PLAY + '=' + self.play)

        if len(args) > 0:
            return '?' + '&'.join(args)
        else:
            return ''

    def to_dict(self):
        res = {}
        if self.mode is not None:
            res[GetArg.ARG_MODE] = self.mode
        if self.play is not None:
            res[GetArg.ARG_PLAY] = self.play
        return res
