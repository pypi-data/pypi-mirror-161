import curses


class WindowManager(object):
    __instance = None

    def __init__(self, main_window):
        self.main_window = main_window

    @classmethod
    def has_instance(cls):
        return cls.__instance is not None

    @classmethod
    def get_instance(cls):
        return cls.__instance

    @classmethod
    def make_instance(cls, main_window):
        cls.__instance = WindowManager(main_window)

    def get_window_width(self):
        return self.main_window.getmaxyx()[1]

    def get_window_height(self):
        return self.main_window.getmaxyx()[0]

    def refresh_window(self):
        self.main_window.refresh()

    def leave_curses(self):
        curses.def_prog_mode()
        self.main_window.keypad(0)
        curses.nocbreak()
        curses.echo()
        curses.endwin()

    def reenter_curses(self):
        curses.reset_prog_mode()
        self.main_window = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.main_window.keypad(1)
