import curses
import os
import platform

from cursesmenu import WindowManager
from cursesmenu.items import ExitItem


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


class CursesMenu(object):
    """
    A class that displays a menu and allows the user to select an option
    """

    def __init__(self, title=None, subtitle=None, show_exit_option=True):
        """
        :ivar str title: The title of the menu
        :ivar str subtitle: The subtitle of the menu
        :ivar bool show_exit_option: Whether this menu should show an exit item by default. Can be overridden \
        when the menu is started
        :ivar items: The list of MenuItems that the menu will display
        :vartype items: list[:class:`MenuItem<cursesmenu.items.MenuItem>`]
        :ivar CursesMenu parent: The parent of this menu
        :ivar int current_option: The currently highlighted menu option
        :ivar MenuItem current_item: The item corresponding to the menu option that is currently highlighted
        :ivar int selected_option: The option that the user has most recently selected
        :ivar MenuItem selected_item: The item in :attr:`items` that the user most recently selected
        :ivar returned_value: The value returned by the most recently selected item
        :ivar screen: the curses window associated with this menu
        :ivar normal: the normal text color pair for this menu
        :ivar highlight: the highlight color pair associated with this window
        """

        self.screen = None
        self.highlight = None
        self.normal = None

        self.title = title
        self.subtitle = subtitle
        self.show_exit_option = show_exit_option

        self.items = list()

        self.parent = None

        self.exit_item = ExitItem(menu=self)

        self.current_option = 0
        self.selected_option = -1

        self.returned_value = None

        self.should_exit = False

    def __repr__(self):
        return "%s: %s. %d items" % (self.title, self.subtitle, len(self.items))

    @property
    def current_item(self):
        """
        :rtype: MenuItem|None
        """
        if self.items:
            return self.items[self.current_option]
        else:
            return None

    @property
    def selected_item(self):
        """
        :rtype: MenuItem|None
        """
        if self.items and self.selected_option != -1:
            return self.items[self.current_option]
        else:
            return None

    def append_item(self, item):
        """
        Add an item to the end of the menu before the exit item

        :param MenuItem item: The item to be added
        """
        did_remove = self.remove_exit()
        item.menu = self
        self.items.append(item)
        if did_remove:
            self.add_exit()
        if self.screen:
            max_row, max_cols = self.screen.getmaxyx()
            if max_row < 6 + len(self.items):
                self.screen.resize(6 + len(self.items), max_cols)
            self.draw()

    def add_exit(self):
        """
        Add the exit item if necessary. Used to make sure there aren't multiple exit items

        :return: True if item needed to be added, False otherwise
        :rtype: bool
        """
        if self.items:
            if self.items[-1] is not self.exit_item:
                self.items.append(self.exit_item)
                return True
        return False

    def remove_exit(self):
        """
        Remove the exit item if necessary. Used to make sure we only remove the exit item, not something else

        :return: True if item needed to be removed, False otherwise
        :rtype: bool
        """
        if self.items:
            if self.items[-1] is self.exit_item:
                del self.items[-1]
                return True
        return False

    def run(self):
        self.setup()
        self.main_loop()
        self.cleanup()

    def setup(self):
        self.should_exit = False

        if self.show_exit_option:
            self.add_exit()
        else:
            self.remove_exit()

        manager = get_window_manager()
        self.screen = curses.newpad(self.get_pad_height(), manager.get_window_width())
        self._set_up_colors()
        curses.curs_set(0)
        manager.refresh_window()
        self.draw()

    def get_pad_height(self):
        number_of_items = len(self.items)
        exit_line = 1 if self.show_exit_option and self.items and self.items[-1] is not self.exit_item else 0
        header_and_footer = 6
        return number_of_items + exit_line + header_and_footer

    def _set_up_colors(self):
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
        self.highlight = curses.color_pair(1)
        self.normal = curses.A_NORMAL

    def main_loop(self):
        while not self.should_exit:
            self.process_user_input()

    def cleanup(self):
        self.clear_screen()

    def clear_screen(self):
        """
        Clear the screen belonging to this menu
        """
        self.screen.clear()
        self.refresh_visible_pad_section()

    def draw(self):
        """
        Redraws the menu and refreshes the screen. Should be called whenever something changes that needs to be redrawn.
        """

        self.draw_border()
        self.draw_title()
        self.draw_subtitle()
        self.draw_items()

        self.refresh_visible_pad_section()

    def draw_border(self):
        self.screen.border()

    def draw_title(self):
        if self.title is not None:
            self.screen.addstr(2, 2, self.title, curses.A_STANDOUT)

    def draw_subtitle(self):
        if self.subtitle is not None:
            self.screen.addstr(4, 2, self.subtitle, curses.A_BOLD)

    def draw_items(self):
        for index, item in enumerate(self.items):
            if self.current_option == index:
                text_style = self.highlight
            else:
                text_style = self.normal
            self.screen.addstr(self.get_start_of_items() + index, 4, item.show(index), text_style)

    def get_start_of_items(self):
        start = 1
        if self.title is not None:
            start += 2
        if self.subtitle is not None:
            start += 2
        return start

    def refresh_visible_pad_section(self):
        main_window_rows = get_window_manager().get_window_height()
        main_window_cols = get_window_manager().get_window_width()

        top_row = self.calculate_top_visible_row()
        self.screen.refresh(top_row, 0, 0, 0, main_window_rows - 1, main_window_cols - 1)

    def calculate_top_visible_row(self):
        if self.pad_is_bigger_than_window():
            if self.bottom_of_pad_is_visible():
                main_window_rows = get_window_manager().get_window_height()
                return self.get_pad_height() - main_window_rows
            else:
                return self.current_option
        else:
            return 0

    def pad_is_bigger_than_window(self):
        main_window_rows = get_window_manager().get_window_height()
        return self.get_pad_height() > main_window_rows

    def bottom_of_pad_is_visible(self):
        main_window_rows = get_window_manager().get_window_height()
        return main_window_rows + self.current_option > self.get_pad_height()

    def process_user_input(self):
        """
        Gets the next single character and decides what to do with it
        """
        user_input = self.get_input()

        go_to_max = ord("9") if len(self.items) >= 9 else ord(str(len(self.items)))

        if ord('1') <= user_input <= go_to_max:
            self.go_to(user_input - ord('0') - 1)
        elif user_input == curses.KEY_DOWN:
            self.go_down()
        elif user_input == curses.KEY_UP:
            self.go_up()
        elif user_input == ord("\n"):
            self.select()

        return user_input

    def get_input(self):
        """
        Can be overridden to change the input method.
        Called in :meth:`process_user_input()<cursesmenu.CursesMenu.process_user_input>`

        :return: the ordinal value of a single character
        :rtype: int
        """
        return get_window_manager().main_window.getch()

    def go_to(self, option):
        """
        Go to the option entered by the user as a number

        :param option: the option to go to
        :type option: int
        """
        self.current_option = option
        self.draw()

    def go_down(self):
        """
        Go down one, wrap to beginning if necessary
        """
        if self.current_option < len(self.items) - 1:
            self.current_option += 1
        else:
            self.current_option = 0
        self.draw()

    def go_up(self):
        """
        Go up one, wrap to end if necessary
        """
        if self.current_option > 0:
            self.current_option += -1
        else:
            self.current_option = len(self.items) - 1
        self.draw()

    def select(self):
        """
        Select the current item and run it
        """
        self.selected_option = self.current_option
        self.selected_item.set_up()
        self.selected_item.action()
        self.selected_item.clean_up()
        self.returned_value = self.selected_item.get_return()
        self.should_exit = self.selected_item.should_exit

        if not self.should_exit:
            self.draw()
