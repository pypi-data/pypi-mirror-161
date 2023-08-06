"""
This program only controls the basic commands of the program's window.
Like starting, closing, and checking if it exists.
"""

from time import sleep
from pywinauto import keyboard
import win32clipboard
import cv2
import pickle
from pathlib import Path


class Application:

    def __init__(self):
        self.__desktop = None
        self.__window = None
        self.pane = None
        self.ark_path = Path(__file__).parent.parent / Path("ark.lnk")

    def start(self, resize=False):
        """ Starts the application by running the shortcut file. """
        self.__assert_ark_link_exists()
        from subprocess import Popen
        Popen(str(self.ark_path), shell=True)
        self.__find_desktop_app()
        self.wait_exists()
        if resize:
            sleep(7)
            self.auto_fix_window_position()
            sleep(0.5)
            self.auto_fix_window_size()
            sleep(0.5)
            self.auto_fix_window_position()

    def __find_ark_pywinauto(self, desktop):
        self.__window = desktop.window(title="ARK: Survival Evolved")
        if self.exists():
            self.pane = self.__window['Pane2']
            self.window = self.__window
        else:
            raise LookupError("Application was unable to be located as a background process.")

    def __find_desktop_app(self):
        from pywinauto import Desktop
        self.__desktop = Desktop(backend="uia")
        self.__find_ark_pywinauto(self.__desktop)  # also finds the ark app

    def __assert_ark_link_exists(self):
        if not self.ark_path.exists():
            raise FileNotFoundError(f"'ark.lnk' file is not found in the directory: {self.ark_path}")

    def exists(self, seconds=5):
        """ Checks if the program is currently running. Default times out at 5 seconds. """
        return self.__window.exists(seconds)

    def close(self):
        """ Closes the application """
        if self.exists():
            self.__window.close()

    def wait_exists(self):
        """ halts the program until the ark starts. """
        self.__window.wait('exists')

    def wait_visible(self):
        """ halts the program until the ark is on screen (e.g. not minimized) """
        self.__window.wait('visible')

    def wait_active(self):
        """ Halts the program until ark is the main focus """
        self.__window.wait('active')

    def minimize(self):
        """ Minimizes the window. """
        self.__window.minimize()

    def maximize(self):
        """ Maximizes the window. """
        self.__window.maximize()

    def set_focus(self):
        """
        Makes this window the current focus/active window
        """
        self.__window.set_focus()

    def capture_as_image(self, path):
        """
        Saves the pane as an images into the desired path.
        :param path: path to save the images with .png extension
        """
        self.pane.set_focus()
        img = self.pane.capture_as_image()
        img.save(path)
        # TODO: assert images is saved (e.g. timestamps)

    def resize_window(self, width, height):
        """
        Resizes the window to desired width and height.
        :param width: size in pixels
        :param height: size in pixels
        """
        rect = self.__window.rectangle()
        top_left = (rect.left, rect.top)
        bottom_right = (rect.right - 1, rect.bottom - 1)
        self.set_focus()
        self.drag(top_left, (10, 10))
        self.drag(bottom_right, (width - 1, height - 1))
        # TODO: assert window has been resized

    def __get_monitor_size(self):
        """ Returns width, height of monitor resolution """
        from win32api import GetSystemMetrics
        return GetSystemMetrics(0), GetSystemMetrics(1)

    def auto_fix_window_position(self):
        """ Defaults the window position """
        width, height = self.__get_monitor_size()
        self.move_window(width // 2, height // 4)

    def auto_fix_window_size(self):
        """ Defaults the window size """
        rect = self.__window.rectangle()
        top_left = (rect.left + 1, rect.top + 1)
        bottom_right = (rect.right - 1, rect.bottom - 1)
        self.set_focus()
        self.drag(top_left, (10, 10))
        self.drag(bottom_right, (1025 - 1, 613 - 1))

    def __window_pane_offset(self):
        """
        Absolute differences between the whole window and the pane.
        :return: the absolute difference
        """
        window_rect = self.__window.rectangle()
        pane_rect = self.pane.rectangle()
        top = abs(window_rect.top - pane_rect.top)
        left = abs(window_rect.left - pane_rect.left)
        bottom = abs(window_rect.bottom - pane_rect.bottom)
        right = abs(window_rect.right - pane_rect.right)
        return left, top, right, bottom

    def resize_pane(self, width=1016, height=563):
        """
        Resizes the window by desired pane size
        :param width: size in pixels
        :param height: size in pixels
        """
        o_left, o_top, o_right, o_bottom = self.__window_pane_offset()
        self.resize_window(width + o_left + o_right, height + o_top + o_bottom)
        # TODO: assert it has been resized

    def move_window(self, left, top):
        """ Moves the window to a new position as the top left corner being the origin """
        self.set_focus()
        dialog_rect = self.__window['Dialog'].rectangle()
        dialog_left = dialog_rect.left + (dialog_rect.width() // 2)
        dialog_top = dialog_rect.top + (dialog_rect.height() // 2)
        self.drag((dialog_left, dialog_top), (left, top))
        # TODO: assert the window has been moved (e.g. program interruption)

    def has_keyboard_focus(self):
        # will have to use AI to figure this out
        pass

    def double_click_dialog(self):
        self.__window['Dialog'].double_click_input()

    def send_keys(self, string):
        self.set_focus()
        sleep(1)
        for c in string:
            if c == " ":
                keyboard.send_keys("{SPACE down}", pause=0.2)
                keyboard.send_keys("{SPACE up}", pause=0.2)
            elif c == "_":
                # keyboard.send_keys("{VK_SHIFT down}", pause=0.5)
                keyboard.send_keys("_", pause=0.5)
                # keyboard.send_keys("{VK_SHIFT up}", pause=0.5)
            else:
                keyboard.send_keys("{" + "{}".format(c) + " down}", pause=0.2)
                keyboard.send_keys("{" + "{}".format(c) + " up}", pause=0.2)

    def send_key_tab(self):
        keyboard.send_keys("{TAB down}")
        keyboard.send_keys("{TAB up}")

    def send_key_enter(self):
        keyboard.send_keys("{ENTER down}")
        keyboard.send_keys("{ENTER up}")

    def send_key_copy(self):
        keyboard.send_keys("{VK_CONTROL down}", pause=0.5)
        keyboard.send_keys("{c down}", pause=0.5)
        keyboard.send_keys("{VK_CONTROL up}", pause=0.5)
        keyboard.send_keys("{c up}", pause=0.5)

    def send_key_paste(self):
        keyboard.send_keys("{VK_CONTROL down}")
        keyboard.send_keys("{v down}")
        keyboard.send_keys("{VK_CONTROL up}")
        keyboard.send_keys("{v up}")

    def send_key_ctrl_n(self):
        keyboard.send_keys("{VK_CONTROL down}")
        keyboard.send_keys("{n down}")
        keyboard.send_keys("{VK_CONTROL up}")
        keyboard.send_keys("{n up}")

    def save_to_clipboard_text(self, string):
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_UNICODETEXT, string)
        # Alternate version if above fails
        # win32clipboard.SetClipboardText(string)
        win32clipboard.CloseClipboard()

    def get_from_clipboard(self):
        win32clipboard.OpenClipboard()
        data = win32clipboard.GetClipboardData()
        win32clipboard.CloseClipboard()
        return data

    def __del__(self):
        """ Close the application when the program finishes """
        # self.close()

    def click(self, coords):
        """ Left click on coordinates """
        self.set_focus()
        self.__window.move_mouse_input(coords=coords)
        self.__window.press_mouse_input(coords=coords)
        self.__window.release_mouse_input(coords=coords)

    def drag(self, start_coords, end_coords):
        """ Click and drag from starting coordinates to ending coordinates """
        self.set_focus()
        self.__window.press_mouse_input(coords=start_coords)
        self.__window.release_mouse_input(coords=end_coords)

    def sides(self, pywin_obj):
        """ Gets the left, top, right, and bottom coordinates of a window/pane """
        rect = pywin_obj.rectangle()
        return rect.left, rect.top, rect.right, rect.bottom

    def window_size(self):
        rect = self.window.rectangle()
        return rect.width(), rect.height

    def pane_size(self):
        rect = self.pane.rectangle()
        return rect.width(), rect.height()

    def window_wrapper(self):
        return self.__window.wrapper_object()

    def pane_wrapper(self):
        return self.pane.wrapper_object()

    def __cached_index(self):
        index = 1
        path = Path('images/menus/cached/index.pickle')
        if path.exists():
            with open(path, 'rb') as r:
                index = pickle.load(r)
        with open(path, 'wb') as w:
            pickle.dump(index + 1, w)
        return index

    def absolute_pane_coords(self, pane_coords):
        left, top, right, bottom = self.sides(self.pane)
        return left + pane_coords[0], top + pane_coords[1]

    def locate_button_by_image(self, menu_name, button_name):
        index = self.__cached_index()
        self.capture_as_image('menus/cached/{}_{}_{}.png'.format(menu_name, button_name, index))
        screenshot = cv2.imread("menus/cached/{}_{}_{}.png".format(menu_name, button_name, index), 0)
        template = cv2.imread("menus/{}/{}.png".format(menu_name, button_name), 0)
        height, width = template.shape
        res = cv2.matchTemplate(screenshot, template, cv2.TM_SQDIFF)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        left, top = min_loc
        return self.absolute_pane_coords((left + (width // 2), top + (height // 2)))


def __test_startup():
    ark = Application()
    ark.start()
    ark.wait_exists()
    ark.set_focus()
    ark.close()


def __test_resizing():
    ark = Application()
    ark.start()
    ark.wait_exists()
    ark.set_focus()

    ark.resize_window(433, 999)
    ark.resize_pane(1000, 600)

    if ark.pane.width != 1000 or ark.pane.height != 600:
        raise ArithmeticError("Width or height is inaccurate")

    ark.close()


def main():
    __test_startup()
    __test_resizing()


if __name__ == "__main__":
    main()
