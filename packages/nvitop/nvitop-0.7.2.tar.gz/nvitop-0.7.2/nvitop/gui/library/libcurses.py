# This file is part of nvitop, the interactive NVIDIA-GPU process viewer.
# License: GNU GPL version 3.

# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring

import contextlib
import curses
import locale
import os
import signal


LIGHT_THEME = False
DEFAULT_FOREGROUND = curses.COLOR_WHITE
DEFAULT_BACKGROUND = curses.COLOR_BLACK
COLOR_PAIRS = {None: 0}


def _init_color_theme(light_theme=False):
    """Sets the default fg/bg colors."""

    global LIGHT_THEME, DEFAULT_FOREGROUND, DEFAULT_BACKGROUND  # pylint: disable=global-statement

    LIGHT_THEME = light_theme
    if LIGHT_THEME:
        DEFAULT_FOREGROUND = curses.COLOR_BLACK
        DEFAULT_BACKGROUND = curses.COLOR_WHITE
    else:
        DEFAULT_FOREGROUND = curses.COLOR_WHITE
        DEFAULT_BACKGROUND = curses.COLOR_BLACK


def _get_color(fg, bg):
    """Returns the curses color pair for the given fg/bg combination."""

    global COLOR_PAIRS  # pylint: disable=global-statement,global-variable-not-assigned

    if isinstance(fg, str):
        fg = getattr(curses, 'COLOR_{}'.format(fg.upper()), -1)
    if isinstance(bg, str):
        bg = getattr(curses, 'COLOR_{}'.format(bg.upper()), -1)

    key = (fg, bg)
    if key not in COLOR_PAIRS:
        size = len(COLOR_PAIRS)
        try:
            curses.init_pair(size, fg, bg)
        except curses.error:
            # If curses.use_default_colors() failed during the initialization
            # of curses, then using -1 as fg or bg will fail as well, which
            # we need to handle with fallback-defaults:
            if fg == -1:  # -1 is the "default" color
                fg = DEFAULT_FOREGROUND
            if bg == -1:  # -1 is the "default" color
                bg = DEFAULT_BACKGROUND

            try:
                curses.init_pair(size, fg, bg)
            except curses.error:
                # If this fails too, colors are probably not supported
                pass
        COLOR_PAIRS[key] = size

    return COLOR_PAIRS[key]


def _get_color_attr(fg=-1, bg=-1, attr=0):
    """Returns the curses attribute for the given fg/bg/attr combination."""
    if isinstance(attr, str):
        attr_strings = map(str.strip, attr.split('|'))
        attr = 0
        for s in attr_strings:
            attr |= getattr(curses, 'A_{}'.format(s.upper()), 0)

    if LIGHT_THEME:  # tweak for light themes
        if attr & curses.A_REVERSE != 0 and bg == -1 and fg not in (DEFAULT_FOREGROUND, -1):
            bg = DEFAULT_FOREGROUND

    if fg == -1 and bg == -1:
        return attr
    return curses.color_pair(_get_color(fg, bg)) | attr


def setlocale_utf8():
    for code in ('C.UTF-8', 'en_US.UTF-8', '', 'C'):
        try:
            code = locale.setlocale(locale.LC_ALL, code)
        except locale.Error:
            continue
        else:
            if 'utf8' in code.lower() or 'utf-8' in code.lower():
                return True

    return False


@contextlib.contextmanager
def libcurses(light_theme=False):
    os.environ.setdefault('ESCDELAY', '25')
    setlocale_utf8()

    win = curses.initscr()
    win.nodelay(True)
    win.leaveok(True)
    win.keypad(True)

    curses.noecho()
    curses.cbreak()
    curses.curs_set(False)
    curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
    curses.mouseinterval(0)
    curses.ungetmouse(0, 0, 0, 0, 0)

    _init_color_theme(light_theme)

    curses.start_color()
    try:
        curses.use_default_colors()
    except curses.error:
        pass

    # Push a Ctrl+C (ascii value 3) to the curses getch stack
    def interrupt_handler(signalnum, frame):  # pylint: disable=unused-argument
        curses.ungetch(3)

    # Simulate a ^C press in curses when an interrupt is caught
    signal.signal(signal.SIGINT, interrupt_handler)

    try:
        yield win
    finally:
        curses.endwin()


class CursesShortcuts:
    """This class defines shortcuts to facilitate operations with curses.

    color(*keys) -- sets the color associated with the keys from
        the current colorscheme.
    color_at(y, x, width, *keys) -- sets the color at the given position
    color_reset() -- resets the color to the default
    addstr(*args) -- failsafe version of self.win.addstr(*args)
    """

    ASCII_TRANSTABLE = str.maketrans(
        '═' + '─╴' + '╒╤╕╪╘╧╛┌┬┐┼└┴┘' + '│╞╡├┤▏▎▍▌▋▊▉█░' + '▲▼' + '␤',
        '=' + '--' + '++++++++++++++' + '||||||||||||||' + '^v' + '?',
    )

    def __init__(self):
        self.win = None
        self.ascii = False

    def addstr(self, *args, **kwargs):
        if self.ascii:
            args = [
                arg.translate(self.ASCII_TRANSTABLE) if isinstance(arg, str) else arg
                for arg in args
            ]

        try:
            self.win.addstr(*args, **kwargs)
        except curses.error:
            pass

    def addnstr(self, *args, **kwargs):
        if self.ascii:
            args = [
                arg.translate(self.ASCII_TRANSTABLE) if isinstance(arg, str) else arg
                for arg in args
            ]

        try:
            self.win.addnstr(*args, **kwargs)
        except curses.error:
            pass

    def addch(self, *args, **kwargs):
        if self.ascii:
            args = [
                arg.translate(self.ASCII_TRANSTABLE) if isinstance(arg, str) else arg
                for arg in args
            ]

        try:
            self.win.addch(*args, **kwargs)
        except curses.error:
            pass

    def color(self, fg=-1, bg=-1, attr=0):
        """Change the colors from now on."""
        self.set_fg_bg_attr(fg, bg, attr)

    def color_at(self, y, x, width, *args, **kwargs):
        """Change the colors at the specified position"""
        try:
            self.win.chgat(y, x, width, _get_color_attr(*args, **kwargs))
        except curses.error:
            pass

    def set_fg_bg_attr(self, fg=-1, bg=-1, attr=0):
        try:
            self.win.attrset(_get_color_attr(fg, bg, attr))
        except curses.error:
            pass

    def color_reset(self):
        """Change the colors to the default colors"""
        self.color()

    def update_size(self, termsize=None):
        if termsize is None:
            self.update_lines_cols()
            termsize = self.win.getmaxyx()
        return termsize

    @staticmethod
    def update_lines_cols():
        curses.update_lines_cols()

    @staticmethod
    def beep():
        curses.beep()

    @staticmethod
    def flash():
        curses.flash()
