import ctypes
import os
import platform
from ctypes import wintypes
from pathlib import Path

_IS_WINDOWS = platform.system() == "Windows"

if _IS_WINDOWS:
    _advapi32 = ctypes.windll.advapi32
    _kernel32 = ctypes.windll.kernel32

    _GetNamedSecurityInfoW = _advapi32.GetNamedSecurityInfoW
    _GetNamedSecurityInfoW.argtypes = [
        wintypes.LPCWSTR,
        ctypes.c_int,
        wintypes.DWORD,
        ctypes.POINTER(ctypes.c_void_p),
        ctypes.POINTER(ctypes.c_void_p),
        ctypes.POINTER(ctypes.c_void_p),
        ctypes.POINTER(ctypes.c_void_p),
        ctypes.POINTER(ctypes.c_void_p),
    ]
    _GetNamedSecurityInfoW.restype = wintypes.DWORD

    _LookupAccountSidW = _advapi32.LookupAccountSidW
    _LookupAccountSidW.argtypes = [
        wintypes.LPCWSTR,
        ctypes.c_void_p,
        wintypes.LPWSTR,
        ctypes.POINTER(wintypes.DWORD),
        wintypes.LPWSTR,
        ctypes.POINTER(wintypes.DWORD),
        ctypes.POINTER(wintypes.DWORD),
    ]
    _LookupAccountSidW.restype = wintypes.BOOL

    _LocalFree = _kernel32.LocalFree
    _LocalFree.argtypes = [ctypes.c_void_p]
    _LocalFree.restype = ctypes.c_void_p

    _SE_FILE_OBJECT = 1
    _OWNER_SECURITY_INFORMATION = 0x00000001


def find_owner(path) -> str:
    path = os.fspath(path)
    if _IS_WINDOWS:
        return _get_windows_owner(path)
    return _get_unix_owner(path)


def _get_unix_owner(path: str) -> str:
    try:
        return Path(path).owner()
    except Exception:
        return "unknown"


def _get_windows_owner(path: str) -> str:
    pSidOwner = ctypes.c_void_p()
    pSD = ctypes.c_void_p()

    result = _GetNamedSecurityInfoW(
        path,
        _SE_FILE_OBJECT,
        _OWNER_SECURITY_INFORMATION,
        ctypes.byref(pSidOwner),
        None,
        None,
        None,
        ctypes.byref(pSD),
    )
    if result != 0:
        return "unknown"

    try:
        name = ctypes.create_unicode_buffer(256)
        domain = ctypes.create_unicode_buffer(256)
        name_size = wintypes.DWORD(len(name))
        domain_size = wintypes.DWORD(len(domain))
        sid_name_use = wintypes.DWORD()

        if not _LookupAccountSidW(
            None,
            pSidOwner,
            name,
            ctypes.byref(name_size),
            domain,
            ctypes.byref(domain_size),
            ctypes.byref(sid_name_use),
        ):
            return "unknown"
        return name.value
    finally:
        _LocalFree(pSD)
