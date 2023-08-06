import curses
from typing import Optional

import cursesmenu


class MenuManager(object):

    __instance = None  # type: Optional[cursesmenu.MenuManager]

    def __init__(self):
        self.main_window = None
        self.root_menu = None
        self.menus = []
        self.current_menu = None

    @classmethod
    def get_instance(cls):  # type: () -> cursesmenu.MenuManager
        if cls.__instance is None:
            cls.__instance = MenuManager()
        return cls.__instance

    def start(self, root_menu):
        self.root_menu = root_menu
        curses.wrapper(self.__main_loop)

    def __main_loop(self, main_window):
        self.main_window = main_window
        self.push_menu(self.root_menu)

        while self.current_menu is not None:
            self.current_menu.draw()
            self.current_menu.process_user_input()

    def push_menu(self,new_menu):
        self.menus.append(new_menu)
        self.current_menu = new_menu
        self.current_menu.setup()

    def pop_menu(self):
        self.current_menu.cleanup()
        self.menus.pop()
        if len(self.menus) > 0:
            self.current_menu = self.menus[-1]
            self.current_menu.setup()
        else:
            self.current_menu=None


