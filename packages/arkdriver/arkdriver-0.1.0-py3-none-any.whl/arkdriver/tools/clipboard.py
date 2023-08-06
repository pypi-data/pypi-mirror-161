"""
Just a prototype, do not actually use. Its not finished.
"""
import threading
import ctypes
import win32api
import win32gui


class Clipboard:
    def _create_window(self) -> int:
        """
        Create a window for listening to messages
        :return: window hwnd
        """
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = self._process_message
        wc.lpszClassName = self.__class__.__name__
        wc.hInstance = win32api.GetModuleHandle(None)
        class_atom = win32gui.RegisterClass(wc)
        return win32gui.CreateWindow(class_atom, self.__class__.__name__, 0, 0, 0, 0, 0, 0, 0, wc.hInstance, None)

    def _process_message(self, hwnd: int, msg: int, wparam: int, lparam: int):
        WM_CLIPBOARDUPDATE = 0x031D
        if msg == WM_CLIPBOARDUPDATE:
            print('clipboard updated!')
        return 0

    def listen(self):
        def runner():
            hwnd = self._create_window()
            ctypes.windll.user32.AddClipboardFormatListener(hwnd)
            win32gui.PumpMessages()

        th = threading.Thread(target=runner, daemon=True)
        th.start()
        while th.is_alive():
            th.join(0.25)


"""
# import ctypes
# import threading
# from dataclasses import dataclass
# from pathlib import Path
# from typing import Callable, Union, List, Optional
#
# import win32api, win32clipboard, win32con, win32gui
#
#
# class Clipboard:
#     @dataclass
#     class Clip:
#         type: str
#         value: Union[str, List[Path]]
#
#     def __init__(
#             self,
#             trigger_at_start: bool = False,
#             on_text: Callable[[str], None] = None,
#             on_update: Callable[[Clip], None] = None,
#             on_files: Callable[[str], None] = None,
#     ):
#         self._trigger_at_start = trigger_at_start
#         self._on_update = on_update
#         self._on_files = on_files
#         self._on_text = on_text
#
#     def _create_window(self) -> int:
#         wc = win32gui.WNDCLASS()
#         wc.lpfnWndProc = self._process_message
#         wc.lpszClassName = self.__class__.__name__
#         wc.hInstance = win32api.GetModuleHandle(None)
#         class_atom = win32gui.RegisterClass(wc)
#         return win32gui.CreateWindow(class_atom, self.__class__.__name__, 0, 0, 0, 0, 0, 0, 0, wc.hInstance, None)
#
#     def _process_message(self, hwnd: int, msg: int, wparam: int, lparam: int):
#         WM_CLIPBOARDUPDATE = 0x031D
#         if msg == WM_CLIPBOARDUPDATE:
#             self._process_clip()
#         return 0
#
#     def _process_clip(self):
#         clip = self.read_clipboard()
#         if not clip:
#             return
#
#         if self._on_update:
#             self._on_update(clip)
#         if clip.type == 'text' and self._on_text:
#             self._on_text(clip.value)
#         elif clip.type == 'files' and self._on_text:
#             self._on_files(clip.value)
#
#     @staticmethod
#     def read_clipboard() -> Optional[Clip]:
#         try:
#             win32clipboard.OpenClipboard()
#
#             def get_formatted(fmt):
#                 if win32clipboard.IsClipboardFormatAvailable(fmt):
#                     return win32clipboard.GetClipboardData(fmt)
#                 return None
#
#             if files := get_formatted(win32con.CF_HDROP):
#                 return Clipboard.Clip('files', [Path(f) for f in files])
#             elif text := get_formatted(win32con.CF_UNICODETEXT):
#                 return Clipboard.Clip('text', text)
#             elif text_bytes := get_formatted(win32con.CF_TEXT):
#                 return Clipboard.Clip('text', text_bytes.decode())
#             elif bitmap_handle := get_formatted(win32con.CF_BITMAP):
#                 # TODO: handle screenshots
#                 pass
#
#             return None
#         finally:
#             win32clipboard.CloseClipboard()
#
#     def listen(self):
#         if self._trigger_at_start:
#             self._process_clip()
#
#         def runner():
#             hwnd = self._create_window()
#             ctypes.windll.user32.AddClipboardFormatListener(hwnd)
#             win32gui.PumpMessages()
#
#         th = threading.Thread(target=runner, daemon=True)
#         th.start()
#         while th.is_alive():
#             th.join(0.25)
#
#
# if __name__ == '__main__':
#     clipboard = Clipboard(on_update=print, trigger_at_start=True)
#     clipboard.listen()
#
#
# if __name__ == '__main__':
#     clipboard = Clipboard()
#     clipboard.listen()
"""
