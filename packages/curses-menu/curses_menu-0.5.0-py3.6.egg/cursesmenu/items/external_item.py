from cursesmenu import WindowManager
from cursesmenu.items import MenuItem


def get_window_manager():  # type: () -> WindowManager
    if not WindowManager.has_instance():
        raise Exception("Window has not been created yet, call cursesmenu.start() first.")
    else:
        return WindowManager.get_instance()


class ExternalItem(MenuItem):
    """
    A base class for items that need to do stuff on the console outside of curses mode.
    Sets the terminal back to standard mode until the action is done.
    Should probably be subclassed.
    """

    def __init__(self, text, menu=None, should_exit=False):
        # Here so Sphinx doesn't copy extraneous info from the superclass's docstring
        super(ExternalItem, self).__init__(text=text, menu=menu, should_exit=should_exit)

    def set_up(self):
        """
        This class overrides this method
        """
        manager = get_window_manager()
        manager.leave_curses()

    def clean_up(self):
        """
        This class overrides this method
        """
        manager = get_window_manager()
        manager.reenter_curses()
