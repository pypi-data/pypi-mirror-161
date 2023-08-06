# Stolen from 
# https://github.com/TeamSpen210/srctools/blob/3be2d058e1755cadfe1ea2f5ee0f5b08efd9c015/src/srctools/_pyinstaller/__init__.py

"""Tell PyInstaller to use the hook module."""
import os.path
from typing import List


def get_hook_dirs() -> List[str]:
    """Our only hooks location is this package."""
    return [os.path.dirname(__file__)]
