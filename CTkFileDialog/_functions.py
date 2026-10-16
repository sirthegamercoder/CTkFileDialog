import os
from typing import List, Literal, Optional, Tuple

from typeguard import typechecked

from .Dialog import _DrawApp, _MiniDialog

FileTypes = Optional[List[Tuple[str, str]]]
OpenMode = Literal[
    "r",
    "rb",
    "r+",
    "rb+",
    "r+b",
    "w",
    "wb",
    "w+",
    "wb+",
    "a",
    "ab",
    "a+",
    "ab+",
    "x",
    "xb",
]

_WRITE_MODES = frozenset("wax+")

_DEFAULT_GEOMETRY: Tuple[str, str] = ("1320x720", "500x400")
_DEFAULT_TITLE = "CTkFileDialog"


def _open_checked(path: str, mode: str, **kwargs):
    if any(c in mode for c in _WRITE_MODES):
        parent = os.path.dirname(path) or "."
        if not os.path.isdir(parent):
            raise FileNotFoundError(f"Parent directory does not exist: {parent}")
    return open(path, mode=mode, **kwargs)


def _run_dialog(
    method: str,
    style: str,
    *,
    filetypes: FileTypes = None,
    hidden: bool = False,
    preview_img: bool = False,
    autocomplete: bool = False,
    video_preview: bool = False,
    initial_dir: str = ".",
    tool_tip: bool = False,
    geometry: Tuple[str, str] = _DEFAULT_GEOMETRY,
    title: str = _DEFAULT_TITLE,
    icon: Optional[str] = None,
):
    if style == "Default":
        app = _DrawApp(
            filetypes=filetypes,
            current_path=initial_dir,
            hidden=hidden,
            preview_img=preview_img,
            method=method,
            autocomplete=autocomplete,
            video_preview=video_preview,
            tool_tip=tool_tip,
            geometry=geometry[0],
            title=title,
            icon_path=icon,
        )
        app.app.wait_window()
        return app

    return _MiniDialog(
        method=method,
        filetypes=filetypes,
        initial_dir=initial_dir,
        autocomplete=autocomplete,
        hidden=hidden,
        geometry=geometry[1],
        title=title,
        icon_path=icon,
    )


def _selected_single(app, style: str) -> Optional[str]:
    if style == "Default":
        return app.selected_file or None
    return app.selected_path or None


def _selected_multi(app, style: str) -> Optional[tuple]:
    if style == "Default":
        return tuple(app.selected_objects) if app.selected_objects else None
    return tuple(app.selected_paths) if app.selected_paths else None


@typechecked
def askopenfilename(
    style: Literal["Mini", "Default"] = "Default",
    filetypes: FileTypes = None,
    hidden: bool = False,
    preview_img: bool = False,
    autocomplete: bool = False,
    video_preview: bool = False,
    initial_dir: str = ".",
    tool_tip: bool = False,
    geometry: Tuple[str, str] = _DEFAULT_GEOMETRY,
    title: str = _DEFAULT_TITLE,
    icon: Optional[str] = None,
) -> Optional[str]:
    app = _run_dialog(
        "askopenfilename",
        style,
        filetypes=filetypes,
        hidden=hidden,
        preview_img=preview_img,
        autocomplete=autocomplete,
        video_preview=video_preview,
        initial_dir=initial_dir,
        tool_tip=tool_tip,
        geometry=geometry,
        title=title,
        icon=icon,
    )
    return _selected_single(app, style)


@typechecked
def askdirectory(
    style: Literal["Default", "Mini"] = "Default",
    filetypes: FileTypes = None,
    hidden: bool = False,
    autocomplete: bool = False,
    initial_dir: str = ".",
    tool_tip: bool = False,
    geometry: Tuple[str, str] = _DEFAULT_GEOMETRY,
    title: str = _DEFAULT_TITLE,
    icon: Optional[str] = None,
) -> Optional[str]:
    app = _run_dialog(
        "askdirectory",
        style,
        filetypes=filetypes,
        hidden=hidden,
        autocomplete=autocomplete,
        initial_dir=initial_dir,
        tool_tip=tool_tip,
        geometry=geometry,
        title=title,
        icon=icon,
    )
    return _selected_single(app, style)


@typechecked
def askopenfilenames(
    style: Literal["Default", "Mini"] = "Default",
    filetypes: FileTypes = None,
    hidden: bool = False,
    preview_img: bool = False,
    autocomplete: bool = False,
    video_preview: bool = False,
    initial_dir: str = ".",
    tool_tip: bool = False,
    geometry: Tuple[str, str] = _DEFAULT_GEOMETRY,
    title: str = _DEFAULT_TITLE,
    icon: Optional[str] = None,
) -> Optional[Tuple[str, ...]]:
    app = _run_dialog(
        "askopenfilenames",
        style,
        filetypes=filetypes,
        hidden=hidden,
        preview_img=preview_img,
        autocomplete=autocomplete,
        video_preview=video_preview,
        initial_dir=initial_dir,
        tool_tip=tool_tip,
        geometry=geometry,
        title=title,
        icon=icon,
    )
    return _selected_multi(app, style)


@typechecked
def asksaveasfilename(
    style: Literal["Default", "Mini"] = "Default",
    filetypes: FileTypes = None,
    hidden: bool = False,
    preview_img: bool = False,
    autocomplete: bool = False,
    video_preview: bool = False,
    initial_dir: str = ".",
    tool_tip: bool = False,
    geometry: Tuple[str, str] = _DEFAULT_GEOMETRY,
    title: str = _DEFAULT_TITLE,
    icon: Optional[str] = None,
) -> Optional[str]:
    app = _run_dialog(
        "asksaveasfilename",
        style,
        filetypes=filetypes,
        hidden=hidden,
        preview_img=preview_img,
        autocomplete=autocomplete,
        video_preview=video_preview,
        initial_dir=initial_dir,
        tool_tip=tool_tip,
        geometry=geometry,
        title=title,
        icon=icon,
    )
    return _selected_single(app, style)


@typechecked
def asksaveasfile(
    style: Literal["Default", "Mini"] = "Default",
    mode: OpenMode = "w",
    filetypes: FileTypes = None,
    hidden: bool = False,
    preview_img: bool = False,
    autocomplete: bool = False,
    video_preview: bool = False,
    initial_dir: str = ".",
    tool_tip: bool = False,
    geometry: Tuple[str, str] = _DEFAULT_GEOMETRY,
    title: str = _DEFAULT_TITLE,
    icon: Optional[str] = None,
    **kwargs,
):
    app = _run_dialog(
        "asksaveasfile",
        style,
        filetypes=filetypes,
        hidden=hidden,
        preview_img=preview_img,
        autocomplete=autocomplete,
        video_preview=video_preview,
        initial_dir=initial_dir,
        tool_tip=tool_tip,
        geometry=geometry,
        title=title,
        icon=icon,
    )
    path = _selected_single(app, style)
    if not path:
        return None
    return _open_checked(path, mode=mode, **kwargs)


@typechecked
def askopenfile(
    style: Literal["Mini", "Default"] = "Default",
    mode: OpenMode = "r",
    hidden: bool = False,
    filetypes: FileTypes = None,
    preview_img: bool = False,
    autocomplete: bool = False,
    video_preview: bool = False,
    initial_dir: str = ".",
    tool_tip: bool = False,
    geometry: Tuple[str, str] = _DEFAULT_GEOMETRY,
    title: str = _DEFAULT_TITLE,
    icon: Optional[str] = None,
    **kwargs,
):
    app = _run_dialog(
        "askopenfile",
        style,
        filetypes=filetypes,
        hidden=hidden,
        preview_img=preview_img,
        autocomplete=autocomplete,
        video_preview=video_preview,
        initial_dir=initial_dir,
        tool_tip=tool_tip,
        geometry=geometry,
        title=title,
        icon=icon,
    )
    path = _selected_single(app, style)
    if not path:
        return None
    return _open_checked(path, mode=mode, **kwargs)


@typechecked
def askopenfiles(
    style: Literal["Default", "Mini"] = "Default",
    mode: OpenMode = "r",
    hidden: bool = False,
    filetypes: FileTypes = None,
    preview_img: bool = False,
    autocomplete: bool = False,
    video_preview: bool = False,
    initial_dir: str = ".",
    tool_tip: bool = False,
    geometry: Tuple[str, str] = _DEFAULT_GEOMETRY,
    title: str = _DEFAULT_TITLE,
    icon: Optional[str] = None,
    **kwargs,
):
    app = _run_dialog(
        "askopenfilenames",
        style,
        filetypes=filetypes,
        hidden=hidden,
        preview_img=preview_img,
        autocomplete=autocomplete,
        video_preview=video_preview,
        initial_dir=initial_dir,
        tool_tip=tool_tip,
        geometry=geometry,
        title=title,
        icon=icon,
    )
    paths = _selected_multi(app, style)
    if not paths:
        return None
    return tuple(_open_checked(f, mode=mode, **kwargs) for f in paths)
