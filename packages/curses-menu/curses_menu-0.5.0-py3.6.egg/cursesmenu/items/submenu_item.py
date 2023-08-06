import curses

from cursesmenu.items import MenuItem, SubmenuReturnItem, SubmenuExitItem


class SubmenuItem(MenuItem):
    """
    A menu item to open a submenu
    """

    def __init__(self, text, submenu, menu=None, should_exit=False, show_return_item=True, show_exit_item=False):
        """
        :ivar CursesMenu self.submenu: The submenu to be opened when this item is selected
        """
        super(SubmenuItem, self).__init__(text=text, menu=menu, should_exit=should_exit)

        self.submenu = submenu
        if menu:
            self.submenu.parent = menu

        self.show_return_item = show_return_item
        self.show_exit_item = show_exit_item

        self.return_item = SubmenuReturnItem(menu=self.submenu)
        self.exit_item = SubmenuExitItem(menu=self.submenu)

    def set_menu(self, menu):
        """
        Sets the menu of this item.
        Should be used instead of directly accessing the menu attribute for this class.

        :param CursesMenu menu: the menu
        """
        self.menu = menu
        self.submenu.parent = menu

    def set_up(self):
        """
        This class overrides this method
        """
        curses.def_prog_mode()
        self.menu.clear_screen()
        self.submenu.show_exit_option = False

        if self.show_return_item:
            self.add_return()
        else:
            self.remove_return()

        if self.show_exit_item:
            self.add_exit()
        else:
            self.remove_exit()

    def action(self):
        """
        This class overrides this method
        """
        self.submenu.run()

    def clean_up(self):
        """
        This class overrides this method
        """
        curses.reset_prog_mode()
        curses.curs_set(1)  # reset doesn't do this right
        curses.curs_set(0)

    def get_return(self):
        """
        :return: The returned value in the submenu
        """
        return self.submenu.returned_value

    def add_exit(self):
        """
        Add the exit item if necessary. Used to make sure there aren't multiple exit items

        :return: True if item needed to be added, False otherwise
        :rtype: bool
        """
        if self.submenu.items:
            if self.submenu.items[-1] is not self.exit_item:
                self.submenu.items.append(self.exit_item)
                return True
        return False

    def remove_exit(self):
        """
        Remove the exit item if necessary. Used to make sure we only remove the exit item, not something else

        :return: True if item needed to be removed, False otherwise
        :rtype: bool
        """
        if self.submenu.items:
            if self.submenu.items[-1] is self.exit_item:
                del self.submenu.items[-1]
                return True
        return False

    def add_return(self):
        """
        Add the exit item if necessary. Used to make sure there aren't multiple exit items

        :return: True if item needed to be added, False otherwise
        :rtype: bool
        """
        if self.submenu.items:
            if self.submenu.items[-1] is self.exit_item:
                if len(self.submenu.items) == 1:
                    self.submenu.items.insert(0, self.return_item)
                    return True
                elif self.submenu.items[-2] is not self.return_item:
                    self.submenu.items.insert(len(self.submenu.items) - 1, self.return_item)
                    return True
            elif self.submenu.items[-1] is not self.return_item:
                self.submenu.items.append(self.return_item)
                return True

        return False

    def remove_return(self):
        """
        Remove the exit item if necessary. Used to make sure we only remove the exit item, not something else

        :return: True if item needed to be removed, False otherwise
        :rtype: bool
        """
        if self.submenu.items:
            if self.submenu.items[-1] is self.return_item:
                del self.submenu.items[-1]
                return True
            if len(self.submenu.items) > 1 and self.submenu.items[-2] is self.return_item:
                del self.submenu.items[-2]
                return True
        return False
