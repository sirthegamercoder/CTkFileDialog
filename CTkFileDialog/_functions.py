import os
from typing import List, Literal, Optional, Tuple

from typeguard import typechecked

from .Dialog import _DrawApp, _MiniDialog


def _open_checked(path: str, mode: str, **kwargs):
    if any(c in mode for c in "wax+"):
        parent = os.path.dirname(path) or "."
        if not os.path.isdir(parent):
            raise FileNotFoundError(f"Parent directory does not exist: {parent}")
    return open(path, mode=mode, **kwargs)


@typechecked
def askopenfilename(
    style: Literal["Mini", "Default"] = "Default",
    filetypes: Optional[List[str]] = None,
    hidden: bool = False,
    preview_img: bool = False,
    autocomplete: bool = False,
    video_preview: bool = False,
    initial_dir: str = ".",
    tool_tip: bool = False,
    geometry: Tuple[str, str] = ("1320x720", "500x400"),
    title: str = "CTkFileDialog",
) -> Optional[str]:
    if style == "Default":
        app = _DrawApp(
            filetypes=filetypes,
            current_path=initial_dir,
            hidden=hidden,
            preview_img=preview_img,
            method="askopenfilename",
            autocomplete=autocomplete,
            video_preview=video_preview,
            tool_tip=tool_tip,
            geometry=geometry[0],
            title=title,
        )
        app.app.wait_window()
        return app.selected_file if app.selected_file else None

    app = _MiniDialog(
        method="askopenfilename",
        filetypes=filetypes,
        initial_dir=initial_dir,
        autocomplete=autocomplete,
        hidden=hidden,
        geometry=geometry[1],
        title=title,
    )
    return app.selected_path if app.selected_path else None


@typechecked
def askdirectory(
    style: Literal["Default", "Mini"] = "Default",
    filetypes: Optional[List[str]] = None,
    hidden: bool = False,
    autocomplete: bool = False,
    initial_dir: str = ".",
    tool_tip: bool = False,
    geometry: Tuple[str, str] = ("1320x720", "500x400"),
    title: str = "CTkFileDialog",
) -> Optional[str]:
    if style == "Default":
        app = _DrawApp(
            filetypes=filetypes,
            current_path=initial_dir,
            hidden=hidden,
            method="askdirectory",
            autocomplete=autocomplete,
            tool_tip=tool_tip,
            geometry=geometry[0],
            title=title,
        )
        app.app.wait_window()
        return app.selected_file if app.selected_file else None

    app = _MiniDialog(
        filetypes=filetypes,
        initial_dir=initial_dir,
        hidden=hidden,
        method="askdirectory",
        autocomplete=autocomplete,
        title=title,
        geometry=geometry[1],
    )
    return app.selected_path if app.selected_path else None


@typechecked
def askopenfilenames(
    style: Literal["Default", "Mini"] = "Default",
    filetypes: Optional[List[str]] = None,
    hidden: bool = False,
    preview_img: bool = False,
    autocomplete: bool = False,
    video_preview: bool = False,
    initial_dir: str = ".",
    tool_tip: bool = False,
    geometry: Tuple[str, str] = ("1320x720", "500x400"),
    title: str = "CTkFileDialog",
) -> Optional[Tuple[str, ...]]:
    if style == "Default":
        app = _DrawApp(
            filetypes=filetypes,
            current_path=initial_dir,
            hidden=hidden,
            preview_img=preview_img,
            method="askopenfilenames",
            autocomplete=autocomplete,
            video_preview=video_preview,
            tool_tip=tool_tip,
            geometry=geometry[0],
            title=title,
        )
        app.app.wait_window()
        return tuple(app.selected_objects) if app.selected_objects else None

    app = _MiniDialog(
        filetypes=filetypes,
        initial_dir=initial_dir,
        hidden=hidden,
        method="askopenfilenames",
        autocomplete=autocomplete,
        geometry=geometry[1],
        title=title,
    )
    return tuple(app.selected_paths) if app.selected_paths else None


@typechecked
def asksaveasfilename(
    style: Literal["Default", "Mini"] = "Default",
    filetypes: Optional[List[str]] = None,
    hidden: bool = False,
    preview_img: bool = False,
    autocomplete: bool = False,
    video_preview: bool = False,
    initial_dir: str = ".",
    tool_tip: bool = False,
    geometry: Tuple[str, str] = ("1320x720", "500x400"),
    title: str = "CTkFileDialog",
) -> Optional[str]:
    if style == "Default":
        app = _DrawApp(
            filetypes=filetypes,
            current_path=initial_dir,
            hidden=hidden,
            preview_img=preview_img,
            method="asksaveasfilename",
            autocomplete=autocomplete,
            video_preview=video_preview,
            tool_tip=tool_tip,
            geometry=geometry[0],
            title=title,
        )
        app.app.wait_window()
        return app.selected_file if app.selected_file else None

    app = _MiniDialog(
        filetypes=filetypes,
        initial_dir=initial_dir,
        hidden=hidden,
        method="asksaveasfilename",
        autocomplete=autocomplete,
        geometry=geometry[1],
        title=title,
    )
    return app.selected_path if app.selected_path else None


@typechecked
def asksaveasfile(
    style: Literal["Default", "Mini"] = "Default",
    mode: Literal[
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
    ] = "w",
    filetypes: Optional[List[str]] = None,
    hidden: bool = False,
    preview_img: bool = False,
    autocomplete: bool = False,
    video_preview: bool = False,
    initial_dir: str = ".",
    tool_tip: bool = False,
    geometry: Tuple[str, str] = ("1320x720", "500x400"),
    title: str = "CTkFileDialog",
    **kwargs,
):
    if style == "Default":
        app = _DrawApp(
            filetypes=filetypes,
            current_path=initial_dir,
            hidden=hidden,
            preview_img=preview_img,
            method="asksaveasfile",
            autocomplete=autocomplete,
            video_preview=video_preview,
            tool_tip=tool_tip,
            geometry=geometry[0],
            title=title,
        )
        app.app.wait_window()
        if not app.selected_file:
            return None
        return _open_checked(app.selected_file, mode=mode, **kwargs)

    app = _MiniDialog(
        filetypes=filetypes,
        initial_dir=initial_dir,
        hidden=hidden,
        method="asksaveasfile",
        autocomplete=autocomplete,
        geometry=geometry[1],
        title=title,
    )
    if not app.selected_path:
        return None
    return _open_checked(app.selected_path, mode=mode, **kwargs)


@typechecked
def askopenfile(
    style: Literal["Mini", "Default"] = "Default",
    mode: Literal[
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
    ] = "r",
    hidden: bool = False,
    filetypes: Optional[List[str]] = None,
    preview_img: bool = False,
    autocomplete: bool = False,
    video_preview: bool = False,
    initial_dir: str = ".",
    tool_tip: bool = False,
    geometry: Tuple[str, str] = ("1320x720", "500x400"),
    title: str = "CTkFileDialog",
    **kwargs,
):
    if style == "Default":
        app = _DrawApp(
            filetypes=filetypes,
            current_path=initial_dir,
            hidden=hidden,
            preview_img=preview_img,
            method="askopenfile",
            autocomplete=autocomplete,
            video_preview=video_preview,
            tool_tip=tool_tip,
            geometry=geometry[0],
            title=title,
        )
        app.app.wait_window()
        if not app.selected_file:
            return None
        return open(app.selected_file, mode=mode, **kwargs)

    app = _MiniDialog(
        filetypes=filetypes,
        initial_dir=initial_dir,
        hidden=hidden,
        method="askopenfile",
        autocomplete=autocomplete,
        geometry=geometry[1],
        title=title,
    )
    if not app.selected_path:
        return None
    return open(app.selected_path, mode=mode, **kwargs)


@typechecked
def askopenfiles(
    style: Literal["Default", "Mini"] = "Default",
    mode: Literal[
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
    ] = "r",
    hidden: bool = False,
    filetypes: Optional[List[str]] = None,
    preview_img: bool = False,
    autocomplete: bool = False,
    video_preview: bool = False,
    initial_dir: str = ".",
    tool_tip: bool = False,
    geometry: Tuple[str, str] = ("1320x720", "500x400"),
    title: str = "CTkFileDialog",
    **kwargs,
):
    if style == "Default":
        app = _DrawApp(
            filetypes=filetypes,
            current_path=initial_dir,
            hidden=hidden,
            preview_img=preview_img,
            method="askopenfilenames",
            autocomplete=autocomplete,
            video_preview=video_preview,
            tool_tip=tool_tip,
            geometry=geometry[0],
            title=title,
        )
        app.app.wait_window()
        if not app.selected_objects:
            return None
        return tuple(open(f, mode=mode, **kwargs) for f in app.selected_objects)

    app = _MiniDialog(
        filetypes=filetypes,
        initial_dir=initial_dir,
        hidden=hidden,
        method="askopenfilenames",
        autocomplete=autocomplete,
        geometry=geometry[1],
        title=title,
    )
    if not app.selected_paths:
        return None
    return tuple(open(f, mode=mode, **kwargs) for f in app.selected_paths)
