import curses
import platform

import os

from cursesmenu import WindowManager


def clear_terminal():
    """
    Call the platform specific function to clear the terminal: cls on windows, reset otherwise
    """
    if platform.system().lower() == "windows":
        os.system('cls')
    else:
        os.system('reset')


def start(root_menu):
    clear_terminal()
    curses.wrapper(_start, root_menu)


def _start(main_window, root_menu):
    WindowManager.make_instance(main_window)
    root_menu.run()


def get_window_manager():  # type: () -> WindowManager
    if not WindowManager.has_instance():
        raise Exception("Window has not been created yet, call cursesmenu.start() first.")
    else:
        return WindowManager.get_instance()