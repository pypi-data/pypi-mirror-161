from cursesmenu.items import MenuItem


class SubmenuExitItem(MenuItem):
    """
    Used to exit the current menu. Handled by :class:`cursesmenu.CursesMenu`
    """

    def __init__(self, text="Exit", menu=None):
        super(SubmenuExitItem, self).__init__(text=text, menu=menu, should_exit=True)

    def action(self):
        menu = self.menu
        while menu is not None:
            menu.selected_item.should_exit = True
            menu = menu.parent
