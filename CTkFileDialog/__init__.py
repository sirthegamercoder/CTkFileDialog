"""
File dialog created in custom Tkinter and inspired by the Tkinter dialog.

- Version: 0.6.0
- Author: MTGC
- Github: https://github.com/sirthegamercoder/CTkFileDialog
"""

from ._functions import (
    askopenfilename,
    askdirectory,
    askopenfile,
    askopenfiles,
    askopenfilenames,
    asksaveasfile,
    asksaveasfilename,
)
from . import Constants

__version__ = "0.6.0"
__all__ = [
    "askopenfilename",
    "askdirectory",
    "askopenfile",
    "askopenfiles",
    "askopenfilenames",
    "asksaveasfile",
    "asksaveasfilename",
    "Constants",
]
