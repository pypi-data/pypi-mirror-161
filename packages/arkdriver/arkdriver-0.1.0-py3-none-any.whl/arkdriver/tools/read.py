from pathlib import Path
from dataclasses import dataclass
from typing import Union, List, Optional
import win32clipboard
import win32con


@dataclass
class Clip:
    type: str
    value: Union[str, List[Path]]


def read_clipboard() -> Optional[Clip]:
    try:
        win32clipboard.OpenClipboard()
        if win32clipboard.IsClipboardFormatAvailable(win32con.CF_HDROP):
            data: tuple = win32clipboard.GetClipboardData(win32con.CF_HDROP)
            return Clip('files', [Path(f) for f in data])
        elif win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
            data: str = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
            return Clip('text', data)
        elif win32clipboard.IsClipboardFormatAvailable(win32con.CF_TEXT):
            data: bytes = win32clipboard.GetClipboardData(win32con.CF_TEXT)
            return Clip('text', data.decode())
        elif win32clipboard.IsClipboardFormatAvailable(win32con.CF_BITMAP):
            # TODO: handle screenshots
            pass
        return None
    finally:
        win32clipboard.CloseClipboard()


if __name__ == '__main__':
    print(read_clipboard())
