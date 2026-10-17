import os
import re
import time
import platform
from pathlib import Path
from typing import Any, List, Optional

import cv2
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from PIL import Image
from CTkMessagebox import CTkMessagebox
from CTkToolTip import CTkToolTip
from _tkinter import TclError

from ._system import find_owner


def _path_is_selectable(path: Optional[str]) -> bool:
    if not path or not isinstance(path, str):
        return False
    try:
        return os.path.exists(path)
    except OSError:
        return False


def _dedupe_preserving_order(items: list) -> list:
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


class _CustomToolTip(CTkToolTip):
    def _show(self) -> None:
        if not self.widget.winfo_exists():
            self.hide()
            self.destroy()
            return
        super()._show()


class _System:
    @staticmethod
    def get_path(path: Optional[str] = None) -> str:
        return path if path is not None else os.getcwd()

    @staticmethod
    def parse_path(path: str) -> str:
        return os.path.abspath(os.path.expanduser(os.path.expandvars(path)))


def _load_ctk_icon(
    icons_dir: Path,
    icon_files: dict,
    key: str,
    size: int = 32,
    cache: Optional[dict] = None,
) -> Optional[ctk.CTkImage]:
    if cache is None:
        cache = {}

    cache_key = (key, size)
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    filename = icon_files.get(key, icon_files.get("default", ""))
    path = icons_dir / filename

    def _load(p: Path):
        img = Image.open(p).convert("RGBA")
        bbox = img.getbbox()
        if bbox:
            img = img.crop(bbox)
        img = img.resize((size * 2, size * 2), Image.LANCZOS)
        return ctk.CTkImage(light_image=img, dark_image=img, size=(size, size))

    try:
        icon = _load(path)
    except (FileNotFoundError, OSError):
        fallback_name = icon_files.get("default", "")
        if not fallback_name:
            return None
        try:
            icon = _load(icons_dir / fallback_name)
        except (FileNotFoundError, OSError):
            return None

    cache[cache_key] = icon
    return icon


class _DrawApp:
    _ICON_FILES = {
        "folder": "filetypes/folder.png",
        "bash": "filetypes/bash.png",
        "image": "filetypes/image.png",
        "python": "filetypes/python.png",
        "text": "filetypes/text.png",
        "markdown": "filetypes/markdown.png",
        "javascript": "filetypes/javascript.png",
        "php": "filetypes/php.png",
        "html": "filetypes/html.png",
        "css": "filetypes/css.png",
        "ini": "filetypes/ini.png",
        "conf": "filetypes/conf.png",
        "exe": "filetypes/exe.png",
        "odt": "filetypes/odt.png",
        "pdf": "filetypes/pdf.png",
        "json": "filetypes/json.png",
        "gz": "filetypes/gz.png",
        "video": "filetypes/video.png",
        "webp": "filetypes/image.png",
        "home": "sidebar/home.png",
        "desktop": "sidebar/desktop.png",
        "downloads": "sidebar/downloads.png",
        "documents": "sidebar/documents.png",
        "pictures": "sidebar/pictures.png",
        "music": "sidebar/music.png",
        "videos": "sidebar/videos.png",
        "templates": "sidebar/templates.png",
        "public": "sidebar/public.png",
        "back": "toolbar/back.png",
        "up": "toolbar/up.png",
        "default": "filetypes/text.png",
    }

    _EXTENSION_ICONS = {
        ".webp": "webp",
        ".awk": "bash",
        ".mp4": "video",
        ".mkv": "video",
        ".sh": "bash",
        ".zsh": "bash",
        ".py": "python",
        ".png": "image",
        ".jpg": "image",
        ".jpeg": "image",
        ".txt": "text",
        ".js": "javascript",
        ".md": "markdown",
        ".php": "php",
        ".html": "html",
        ".css": "css",
        ".ini": "ini",
        ".conf": "conf",
        ".json": "json",
        ".odt": "odt",
        ".pdf": "pdf",
        ".exe": "exe",
        ".gz": "gz",
    }

    def __init__(
        self,
        method: str,
        filetypes: Optional[List[str]] = None,
        buffering: int = 1,
        encoding: str = "utf-8",
        current_path: str = ".",
        hidden: bool = False,
        preview_img: bool = False,
        autocomplete: bool = False,
        video_preview: bool = False,
        tool_tip: bool = False,
        title: str = "CTkFileDialog",
        geometry: str = "1320x720",
        icon_path: Optional[str] = None,
    ) -> None:
        self.method = method
        self.filetypes = filetypes
        self.buffering = buffering
        self.encoding = encoding
        self.hidden = hidden
        self.preview_img = preview_img
        self.autocomplete = autocomplete
        self.video_preview = video_preview
        self.tool_tip = tool_tip

        self.current_path = _System.parse_path(current_path or os.getcwd())
        self.current_theme = ctk.get_appearance_mode()
        self._text_color = (
            "#000000" if self.current_theme.lower() == "light" else "#cccccc"
        )

        self.selected_file: Optional[str] = ""
        self.selected_objects: list = []
        self._temp_item: Optional[str] = None
        self._temp_items: list = []
        self._all_buttons: list = []
        self.tab_index = -1
        self.LOADED = 0
        self.BATCH = 30
        self.archivos: list = []
        self.entire_paths: list = []

        self._BASE_DIR = Path(__file__).parent
        self._icons_dir = self._BASE_DIR / "icons"

        self._icon_cache: dict = {}
        self._image_cache: dict = {}
        self._video_cache: dict = {}
        self._info_cache: dict = {}

        self.app = ctk.CTkToplevel()
        self.app.title(title)
        self.app.geometry(geometry)
        if icon_path:
            try:
                self.app.wm_iconbitmap(icon_path)
            except Exception:
                pass
        self.app.protocol("WM_DELETE_WINDOW", self.protocol_windows)
        self.app.bind("<Alt-Left>", lambda _: self._go_back())

        self._build_top_side()
        self._build_left_side()
        self._build_center_side()

        try:
            self.app.grab_set()
        except TclError:
            pass

    def protocol_windows(self):
        if not self.selected_file and not self.selected_objects:
            self.selected_file = None
            self.selected_objects = []

        if getattr(self, "_scroll_job", None):
            try:
                self.app.after_cancel(self._scroll_job)
            except Exception:
                pass
            self._scroll_job = None

        try:
            self.app.unbind_all("<MouseWheel>")
            self.app.unbind_all("<Button-4>")
            self.app.unbind_all("<Button-5>")
        except Exception:
            pass

        try:
            self.app.destroy()
        except Exception:
            pass

    def _icon(self, key: str, size: int = 32) -> ctk.CTkImage:
        return _load_ctk_icon(
            self._icons_dir, self._ICON_FILES, key, size, self._icon_cache
        )

    def _update_entry(self, path: str) -> None:
        self.PathEntry.configure(state="normal")
        self.PathEntry.delete(0, "end")
        self.PathEntry.insert(0, path)

    @staticmethod
    def _truncate(name: str, max_len: int = 18) -> str:
        return name[: max_len - 3] if len(name) > max_len else name

    @staticmethod
    def _is_image(path: str) -> bool:
        try:
            with Image.open(path) as img:
                img.verify()
            return True
        except Exception:
            return False

    @staticmethod
    def _is_video(path: str) -> bool:
        try:
            cap = cv2.VideoCapture(path)
            valid = cap.isOpened()
            cap.release()
            return valid
        except Exception:
            return False

    def _is_image_cached(self, path: str) -> bool:
        hit = self._image_cache.get(path)
        if hit is None:
            hit = self._is_image(path)
            self._image_cache[path] = hit
        return hit

    def _is_video_cached(self, path: str) -> bool:
        hit = self._video_cache.get(path)
        if hit is None:
            hit = self._is_video(path)
            self._video_cache[path] = hit
        return hit

    def _get_video_frame(
        self, path: str, frame_number: int = 10
    ) -> Optional[Image.Image]:
        try:
            cap = cv2.VideoCapture(path)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = cap.read()
            cap.release()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                return Image.fromarray(frame)
        except Exception:
            pass
        return None

    def _get_info(self, path: str) -> str:
        try:
            st = os.stat(path)
            key = (path, st.st_mtime)
            cached = self._info_cache.get(key)
            if cached is not None:
                return cached

            owner = find_owner(path)
            created = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(st.st_ctime))
            info = (
                f"File: {os.path.basename(path)}\n"
                f"Creation: {created}\n"
                f"Owner: {owner}\n"
                f"Path: {path}"
            )
            self._info_cache = {
                k: v for k, v in self._info_cache.items() if k[0] != path
            }
            self._info_cache[key] = info
            return info
        except Exception as e:
            return f"Error retrieving info: {e}"

    def _reset_selection(self) -> None:
        if self.method != "askdirectory":
            self._temp_item = None
        self._temp_items.clear()
        self.selected_objects.clear()
        for btn in self._all_buttons:
            if btn.winfo_exists():
                try:
                    btn.configure(
                        fg_color="transparent",
                        hover_color="#8da3ae",
                        text_color=self._text_color,
                    )
                except TclError:
                    pass
        self._all_buttons.clear()

    def _go_back(self):
        parent = os.path.dirname(self.current_path)
        if parent and parent != self.current_path:
            self.current_path = parent
            self._update_entry(self.current_path)
            self._list_files()

    def navigate_to(self, path: str) -> None:
        try:
            path = _System.parse_path(path)
        except (OSError, ValueError):
            self._update_entry(str(self.current_path))
            CTkMessagebox(message="Invalid path.", title="Error", icon="cancel")
            return

        if os.path.isdir(path):
            if self.method == "askdirectory":
                self._temp_item = path
            self.current_path = path
            self._update_entry(path)
            self._list_files()
            return

        if not os.path.exists(path):
            self._update_entry(str(self.current_path))
            CTkMessagebox(
                message="No such file or directory!",
                title="Error",
                icon="cancel",
            )
            return

        if self.method in ("asksaveasfile", "asksaveasfilename"):
            if os.path.isfile(path):
                msg = CTkMessagebox(
                    message="This file already exists. Overwrite?",
                    icon="warning",
                    title="Warning",
                    option_1="Yes",
                    option_2="No",
                )
                if msg.get() == "No":
                    return
            self._temp_item = path
            self._close_app()
            return

        if self.method == "askopenfile":
            if not os.path.isfile(path):
                CTkMessagebox(message="File not found!", title="Error", icon="cancel")
                self._update_entry(str(self.current_path))
                return
            self._temp_item = path
            self._update_entry(path)
            return

        if os.path.isfile(path):
            self._temp_item = path
            self._update_entry(path)
            return

        self._update_entry(str(self.current_path))
        CTkMessagebox(message="Not a regular file.", title="Error", icon="cancel")

    def _close_app(self):
        if self.method == "asksaveasfilename":
            entry_value = self.PathEntry.get().strip()
            if entry_value and not os.path.isdir(entry_value):
                self.selected_file = entry_value

        if self.method == "askdirectory":
            candidate = self._temp_item or self.current_path
            if (
                candidate
                and _path_is_selectable(candidate)
                and os.path.isdir(candidate)
            ):
                self.selected_file = candidate
                self.protocol_windows()
                return

        if self._temp_item and _path_is_selectable(self._temp_item):
            self.selected_file = self._temp_item
            self.protocol_windows()
            return

        self.protocol_windows()

    def _build_top_side(self) -> None:
        top_bar = ctk.CTkFrame(master=self.app, height=40, fg_color="transparent")
        top_bar.pack(side="top", fill="x")

        def on_exit():
            msg = CTkMessagebox(
                message="Do you want to exit?",
                title="Exit",
                option_1="Yes",
                option_2="No",
                icon="warning",
            )
            if msg.get() == "Yes":
                self.selected_file = None
                self.selected_objects = []
                self._temp_item = None
                self._temp_items = []
                self.protocol_windows()

        ctk.CTkButton(
            master=top_bar,
            text="Exit",
            font=("Segoe UI", 15),
            width=70,
            command=on_exit,
            hover_color="red",
        ).pack(side="left", fill="x")

        self.PathEntry = ctk.CTkEntry(
            master=top_bar, width=1070, corner_radius=0, insertwidth=0
        )
        self.PathEntry.insert(0, _System.get_path(str(self.current_path)))
        self.PathEntry.pack(side="right", fill="y", padx=10, pady=10)
        self.PathEntry.bind(
            "<Return>", lambda _: self.navigate_to(self.PathEntry.get())
        )

        ctk.CTkButton(
            master=top_bar,
            text="",
            image=self._icon("back", size=20),
            width=70,
            command=self._go_back,
        ).pack(side="left", fill="x", padx=10, pady=10)

        ctk.CTkButton(
            master=top_bar,
            text="Ok",
            font=("Segoe UI", 15),
            width=70,
            command=self._close_app,
        ).pack(side="left", fill="x", padx=10, pady=10)

        if self.autocomplete:
            for key in ("<Down>", "<Up>", "<Tab>"):
                self.PathEntry.bind(key, self._autocomplete)

    def _build_left_side(self) -> None:
        frame = ctk.CTkFrame(master=self.app, width=200)
        frame.pack(side="left", fill="y", padx=10, pady=10)
        frame.pack_propagate(False)

        folders = self._get_places()

        ctk.CTkLabel(master=frame, text="Places", font=("Segoe UI", 15)).pack(
            side=ctk.TOP, padx=5, pady=5
        )

        place_icon_keys = {
            "Desktop": "desktop",
            "Downloads": "downloads",
            "Documents": "documents",
            "Pictures": "pictures",
            "Music": "music",
            "Videos": "videos",
            "Templates": "templates",
            "Public": "public",
        }

        for name, path in folders.items():
            icon_key = place_icon_keys.get(name, "home")
            ctk.CTkButton(
                master=frame,
                text=f"   {name}",
                image=self._icon(icon_key, size=20),
                compound="left",
                font=("Segoe UI", 14),
                anchor="w",
                fg_color="transparent",
                hover_color="#8da3ae",
                text_color=self._text_color,
                corner_radius=2,
                border_width=0,
                command=lambda p=path: self.navigate_to(p),
            ).pack(fill="x", pady=4)

    @staticmethod
    def _get_places() -> dict:
        home = os.path.expanduser("~")
        system = platform.system()

        if system == "Windows":
            home_path = Path(home)
            candidates = {
                home_path.name: home_path,
                "Desktop": home_path / "Desktop",
                "Documents": home_path / "Documents",
                "Downloads": home_path / "Downloads",
                "Pictures": home_path / "Pictures",
                "Music": home_path / "Music",
                "Videos": home_path / "Videos",
            }
            return {
                name: str(path) for name, path in candidates.items() if path.exists()
            } or {home_path.name: str(home_path)}

        folders = {os.path.basename(home) or "Home": home}

        dir_file = os.path.join(home, ".config", "user-dirs.dirs")
        pattern = re.compile(r'XDG_\w+_DIR="(.+?)"')

        if os.path.isfile(dir_file):
            try:
                with open(dir_file, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        match = pattern.search(line)
                        if not match:
                            continue
                        raw = match.group(1)
                        path = os.path.expandvars(os.path.expanduser(raw))
                        if not os.path.isdir(path):
                            continue
                        name = os.path.basename(os.path.normpath(path))
                        if name and name != os.path.basename(home):
                            folders.setdefault(name, path)
            except OSError:
                pass

        fallbacks = {
            "Desktop": os.path.join(home, "Desktop"),
            "Documents": os.path.join(home, "Documents"),
            "Downloads": os.path.join(home, "Downloads"),
            "Pictures": os.path.join(home, "Pictures"),
            "Music": os.path.join(home, "Music"),
            "Videos": os.path.join(home, "Videos"),
            "Public": os.path.join(home, "Public"),
            "Templates": os.path.join(home, "Templates"),
        }
        for name, path in fallbacks.items():
            if name not in folders and os.path.isdir(path):
                folders[name] = path

        return folders

    def _build_center_side(self) -> None:
        self.CenterSideFrame = ctk.CTkScrollableFrame(master=self.app)
        self.CenterSideFrame.pack(
            expand=True, side="top", fill="both", padx=10, pady=10
        )

        self._bind_scroll()
        self.CenterSideFrame._parent_canvas.bind(
            "<<Scroll>>", lambda _: self._check_scroll(), add="+"
        )

        self.content_frame = ctk.CTkFrame(master=self.CenterSideFrame)
        self.content_frame.pack(side="top", fill="both", expand=True, padx=20, pady=10)

        self._list_files()

    def _bind_scroll(self) -> None:
        canvas = self.CenterSideFrame._parent_canvas
        self._scroll_accum = 0

        def _on_mousewheel(event):
            x1 = self.CenterSideFrame.winfo_rootx()
            y1 = self.CenterSideFrame.winfo_rooty()
            x2 = x1 + self.CenterSideFrame.winfo_width()
            y2 = y1 + self.CenterSideFrame.winfo_height()
            if not (x1 <= event.x_root <= x2 and y1 <= event.y_root <= y2):
                return

            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")
            else:
                delta = event.delta
                if abs(delta) < 120:
                    self._scroll_accum += delta
                    steps = int(self._scroll_accum / 120)
                    if steps == 0:
                        return
                    self._scroll_accum -= steps * 120
                else:
                    steps = int(delta / 120)
                canvas.yview_scroll(-steps, "units")

            self._check_scroll()

        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        canvas.bind_all("<Button-4>", _on_mousewheel)
        canvas.bind_all("<Button-5>", _on_mousewheel)

        self._scroll_handler = _on_mousewheel

    def _clear_content(self):
        for widget in self.content_frame.winfo_children():
            try:
                widget.destroy()
            except Exception:
                pass

    def _handle_click(self, event, path: str, button: ctk.CTkButton):
        ctrl_pressed = bool(event.state & 0x0004)

        if not ctrl_pressed:
            self._reset_selection()
            if os.path.isdir(path):
                self.navigate_to(path)
                return
            self._temp_item = path
            button.configure(fg_color="blue")
            self._all_buttons.append(button)
            return

        if self.method not in ("askopenfilenames", "askopenfiles"):
            return

        if path in self._temp_items:
            self._temp_items.remove(path)
            button.configure(
                fg_color="transparent",
                hover_color="#8da3ae",
                text_color=self._text_color,
            )
            if button in self._all_buttons:
                self._all_buttons.remove(button)
        else:
            self._temp_items.append(path)
            button.configure(fg_color="blue")
            if button not in self._all_buttons:
                self._all_buttons.append(button)

    def _load_batch(self, count: int) -> None:
        columns = 5
        row = self.LOADED // columns
        col = self.LOADED % columns
        base = self.current_path

        while self.LOADED < len(self.archivos) and count > 0:
            name = self.archivos[self.LOADED]
            full_path = os.path.join(base, name)

            if self.method == "askdirectory" and os.path.isfile(full_path):
                self.LOADED += 1
                continue

            icon = self._get_icon(full_path, name)

            command = None
            if self.method not in ("askopenfilenames", "askopenfiles"):
                command = lambda p=full_path: self.navigate_to(p)

            button = ctk.CTkButton(
                master=self.content_frame,
                text=self._truncate(name),
                image=icon,
                compound="left",
                width=180,
                height=60,
                anchor="w",
                fg_color="transparent",
                hover_color="#8da3ae",
                text_color=self._text_color,
                command=command,
            )

            if self.tool_tip:
                _CustomToolTip(widget=button, message=self._get_info(full_path))

            if self.method in ("askopenfilenames", "askopenfiles"):
                button.bind(
                    "<Button-1>",
                    lambda event, p=full_path, b=button: self._handle_click(
                        event, p, b
                    ),
                )

            button.grid(row=row, column=col, padx=10, pady=10)

            col += 1
            if col >= columns:
                col = 0
                row += 1

            self.LOADED += 1
            count -= 1

    def _get_icon(self, full_path: str, name: str) -> ctk.CTkImage:
        if os.path.isdir(full_path):
            return self._icon("folder", size=32)

        if self.preview_img and self._is_image_cached(full_path):
            try:
                img = Image.open(full_path)
                img.thumbnail((32, 32))
                return ctk.CTkImage(light_image=img, dark_image=img, size=(32, 32))
            except Exception:
                return self._icon("image", size=32)

        if self.video_preview and self._is_video_cached(full_path):
            frame = self._get_video_frame(full_path, frame_number=10)
            if frame:
                frame.thumbnail((32, 32))
                return ctk.CTkImage(light_image=frame, dark_image=frame, size=(32, 32))
            return self._icon("video", size=32)

        ext = os.path.splitext(name)[1].lower()
        key = self._EXTENSION_ICONS.get(ext, "default")
        return self._icon(key, size=32)

    def _check_scroll(self) -> None:
        if getattr(self, "_scroll_job", None):
            try:
                self.app.after_cancel(self._scroll_job)
            except Exception:
                pass
        self._scroll_job = self.app.after(150, self._do_check_scroll)

    def _do_check_scroll(self) -> None:
        self._scroll_job = None
        if self.LOADED >= len(self.archivos):
            return
        try:
            canvas = self.CenterSideFrame._parent_canvas
            if canvas.yview()[1] > 0.98:
                self._load_batch(10)
        except TclError:
            pass

    def _list_files(self) -> None:
        self.LOADED = 0
        self._reset_selection()

        try:
            self.CenterSideFrame._parent_canvas.yview_moveto(0)
        except Exception:
            pass

        self._clear_content()

        self._image_cache.clear()
        self._video_cache.clear()
        self._info_cache.clear()

        try:
            entries = list(os.scandir(self.current_path))
        except PermissionError:
            CTkMessagebox(message="Permission denied!", title="Error", icon="cancel")
            return
        except OSError as e:
            CTkMessagebox(
                message=f"Cannot read directory:\n{e}",
                title="Error",
                icon="cancel",
            )
            return

        self.archivos = [
            f.name
            for f in entries
            if (f.is_dir() or (self.method != "askdirectory" and f.is_file()))
            and (self.hidden or not f.name.startswith("."))
            and (
                f.is_dir()
                or not self.filetypes
                or any(f.name.endswith(ext) for ext in self.filetypes)
            )
        ]

        if not self.archivos:
            self.entire_paths = []
            return

        if self.autocomplete:
            self.entire_paths = [
                os.path.join(self.current_path, f) for f in self.archivos
            ]

        self._load_batch(self.BATCH)

    def _autocomplete(self, event) -> str:
        paths = getattr(self, "entire_paths", None) or []
        if not paths or not self.archivos:
            return "break"

        n = len(paths)
        if self.tab_index >= n:
            self.tab_index = -1

        if event.keysym == "Up":
            self.tab_index = (self.tab_index - 1) % n
        else:
            self.tab_index = (self.tab_index + 1) % n

        path = paths[self.tab_index]
        self._update_entry(path)
        self._temp_item = path
        return "break"


class _MiniDialog:
    _ICON_FILES = {
        "up": "toolbar/up.png",
        "default": "filetypes/text.png",
    }

    def __init__(
        self,
        method: str,
        hidden: bool = False,
        filetypes: Optional[List[str]] = None,
        autocomplete: bool = False,
        initial_dir: str = ".",
        _extra_method: str = "",
        geometry: str = "500x400",
        title: str = "CTkFileDialog",
        icon_path: Optional[str] = None,
        **ignored,
    ):
        self.method = method
        self._extra_method = _extra_method
        self.hidden = hidden
        self.filetypes = filetypes
        self.autocomplete = autocomplete
        self.tab_index = -1
        self.max_index = 0

        resolved = _System.parse_path(initial_dir or os.getcwd())
        if not os.path.isdir(resolved):
            resolved = os.path.expanduser("~")
        self.initial_dir = resolved

        self.selected_path: Optional[str] = None
        self.selected_paths: Optional[list] = None
        self.selected_item: Optional[str] = None
        self._finalize = False

        self._PATH = os.path.dirname(os.path.realpath(__file__))
        self._icons_dir = Path(self._PATH) / "icons"
        self._icon_cache: dict = {}
        self.folder_image = self._load_image(
            os.path.join(self._PATH, "icons/_IconsMini/folder.png")
        )
        self.file_image = self._load_image(
            os.path.join(self._PATH, "icons/_IconsMini/file.png")
        )

        self.master = ctk.CTkToplevel()
        self.master.geometry(geometry)
        self.master.title(title)
        if icon_path:
            try:
                self.master.wm_iconbitmap(icon_path)
            except Exception:
                pass
        self.master.bind("<Alt-Left>", lambda _: self._up())

        self._build_top_side()
        self._build_center_side()
        self.list_files()

        self.master.wait_visibility()
        try:
            self.master.grab_set()
        except TclError:
            pass
        self.master.wait_window()

    def _icon(self, key: str, size: int = 20) -> Optional[ctk.CTkImage]:
        return _load_ctk_icon(
            self._icons_dir, self._ICON_FILES, key, size, self._icon_cache
        )

    def _build_top_side(self):
        self.frame = ctk.CTkFrame(self.master)
        self.frame.pack(fill=ctk.BOTH, expand=True)

        path_frame = ctk.CTkFrame(self.frame)
        path_frame.pack(fill=ctk.X, padx=10, pady=10)

        self.path_entry = ctk.CTkEntry(path_frame)
        self.path_entry.pack(expand=True, fill=ctk.X, side=ctk.LEFT, padx=10, pady=10)
        self.path_entry.bind("<Return>", lambda _: self._on_enter_path())
        self.path_entry.insert(0, self.initial_dir)

        if self.autocomplete:
            for key in ("<Tab>", "<Down>", "<Up>"):
                self.path_entry.bind(key, self._autocomplete)

        ctk.CTkButton(
            path_frame,
            text="",
            image=self._icon("up", size=20),
            width=30,
            command=self._up,
        ).pack(side=ctk.RIGHT, padx=10, pady=10)

        btn_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        btn_frame.pack(side=ctk.BOTTOM, fill=ctk.X, padx=10, pady=10)

        ctk.CTkButton(btn_frame, text="OK", command=self._on_select).pack(
            side=ctk.RIGHT
        )
        ctk.CTkButton(btn_frame, text="Cancel", command=self._on_cancel).pack(
            side=ctk.RIGHT, padx=10
        )

    def _build_center_side(self):
        tree_frame = ctk.CTkFrame(self.frame)
        tree_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=5)

        style = ttk.Style()
        style.theme_use("clam")
        mode = ctk.get_appearance_mode()

        if mode == "Dark":
            style.configure(
                "Treeview",
                background="#242424",
                foreground="#FFFFFF",
                fieldbackground="#242424",
                bordercolor="#242424",
                rowheight=30,
            )
            style.map(
                "Treeview",
                background=[("selected", "#444444")],
                foreground=[("selected", "#FFFFFF")],
            )
        else:
            style.configure(
                "Treeview",
                background="#FFFFFF",
                foreground="#000000",
                fieldbackground="#FFFFFF",
                bordercolor="#DDDDDD",
                rowheight=30,
            )
            style.map(
                "Treeview",
                background=[("selected", "#E0E0E0")],
                foreground=[("selected", "#000000")],
            )

        select_mode = (
            "extended"
            if self.method in ("askopenfilenames", "askopenfiles")
            else "browse"
        )
        self.tree = ttk.Treeview(tree_frame, show="tree", selectmode=select_mode)
        self.tree.bind("<Double-1>", self._on_click)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    @staticmethod
    def _load_image(image: str) -> tk.PhotoImage:
        return tk.PhotoImage(file=image)

    def list_files(self):
        raw = self.path_entry.get().strip()
        path = _System.parse_path(raw) if raw else self.initial_dir

        if os.path.isfile(path):
            return

        if not os.path.isdir(path):
            fallback = os.path.expanduser("~")
            if os.path.isdir(fallback) and fallback != path:
                self.initial_dir = fallback
                self.update_entry(fallback)
                return self.list_files()

            CTkMessagebox(message="Directory not found!", title="Error", icon="cancel")
            self.update_entry(self.initial_dir)
            return

        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
        except TclError:
            return

        try:
            entries = list(os.scandir(path))
        except PermissionError:
            CTkMessagebox(message="Permission denied!", title="Error", icon="cancel")
            self.update_entry(self.initial_dir)
            return
        except OSError as e:
            CTkMessagebox(
                message=f"Cannot read directory:\n{e}",
                title="Error",
                icon="cancel",
            )
            self.update_entry(self.initial_dir)
            return

        filtered = [
            f
            for f in entries
            if (f.is_dir() or (self.method != "askdirectory" and f.is_file()))
            and (self.hidden or not f.name.startswith("."))
            and (
                f.is_dir()
                or not self.filetypes
                or any(f.name.endswith(ext) for ext in self.filetypes)
            )
        ]
        ordered = sorted(filtered, key=lambda f: (not f.is_dir(), f.name.lower()))

        self.initial_dir = path
        self.update_entry(path)

        for f in ordered:
            icon = self.folder_image if f.is_dir() else self.file_image
            self.tree.insert("", tk.END, text=f.name, image=icon)

        if self.autocomplete:
            self.absolute_paths = [f.path for f in ordered]
            self.max_index = len(self.absolute_paths)
            self.tab_index = -1
        else:
            self.absolute_paths = []
            self.max_index = 0

    def update_entry(self, path: str):
        self.path_entry.configure(state="normal")
        self.path_entry.delete(0, ctk.END)
        self.path_entry.insert(0, path)

    def _autocomplete(self, event) -> str:
        paths = getattr(self, "absolute_paths", None) or []
        if not paths or not self.max_index:
            return "break"

        n = len(paths)
        if self.tab_index >= n:
            self.tab_index = -1

        if event.keysym == "Up":
            self.tab_index = (self.tab_index - 1) % n
        else:
            self.tab_index = (self.tab_index + 1) % n

        path = paths[self.tab_index]
        self.path_entry.delete(0, ctk.END)
        self.path_entry.insert(0, path)

        item_id = self.tree.get_children()[self.tab_index]
        self.tree.focus(item_id)
        self.tree.selection_set(item_id)
        self.tree.see(item_id)

        self.selected_item = path
        return "break"

    def _on_enter_path(self):
        raw = self.path_entry.get().strip()
        if not raw:
            self.update_entry(self.initial_dir)
            return

        try:
            path = _System.parse_path(raw)
        except (OSError, ValueError):
            self.update_entry(self.initial_dir)
            CTkMessagebox(message="Invalid path.", title="Error", icon="cancel")
            return

        if os.path.isdir(path):
            self.initial_dir = path
            self.list_files()
            return

        if os.path.isfile(path):
            self.selected_item = path
            return

        self.update_entry(self.initial_dir)
        CTkMessagebox(
            title="Error",
            icon="cancel",
            message="No such file or directory!",
        )

    def _on_cancel(self, destroy: bool = True):
        self.selected_path = None
        self.selected_paths = None
        self.selected_item = None
        self._finalize = False
        if destroy:
            self.master.destroy()

    def _on_select(self):
        raw = self.path_entry.get().strip()
        path = _System.parse_path(raw) if raw else None

        if (
            self.method
            in (
                "askopenfilename",
                "askopenfile",
                "askdirectory",
            )
            and path
            and _path_is_selectable(path)
        ):
            if self.method == "askdirectory" and os.path.isdir(path):
                self.selected_path = path
                self._finalize = True
                self.master.destroy()
                return
            if self.method != "askdirectory" and os.path.isfile(path):
                self.selected_path = path
                self._finalize = True
                self.master.destroy()
                return

        if self.method in ("asksaveasfile", "asksaveasfilename"):
            if not path or os.path.isdir(path):
                return
            parent = os.path.dirname(path) or "."
            if not os.path.isdir(parent):
                CTkMessagebox(
                    message="Parent directory does not exist.",
                    title="Error",
                    icon="cancel",
                )
                return
            if os.path.exists(path) and self._extra_method != "askopenfile":
                opts = CTkMessagebox(
                    message="This file already exists. Overwrite?",
                    title="Warning",
                    icon="warning",
                    option_1="Yes",
                    option_2="No",
                )
                if opts.get() == "No":
                    return
            self.selected_path = path
            self._finalize = True
            self.master.destroy()
            return

        if self.method in ("askopenfiles", "askopenfilenames"):
            if not self.absolute_paths:
                return
            selected = self.tree.selection()
            paths = [
                self.absolute_paths[self.tree.index(item)]
                for item in selected
                if 0 <= self.tree.index(item) < len(self.absolute_paths)
                and os.path.isfile(self.absolute_paths[self.tree.index(item)])
            ]
            paths = _dedupe_preserving_order(paths)
            if paths:
                self.selected_paths = paths
                self._finalize = True
                self.master.destroy()
            return

        if self.method in ("askopenfilename", "askopenfile", "askdirectory"):
            if not self.selected_item:
                return
            if not _path_is_selectable(self.selected_item):
                CTkMessagebox(
                    message="Path no longer exists.",
                    title="Error",
                    icon="cancel",
                )
                return
            if self.method == "askdirectory":
                if not os.path.isdir(self.selected_item):
                    return
            else:
                if not os.path.isfile(self.selected_item):
                    return
            self.selected_path = self.selected_item
            self._finalize = True
            self.master.destroy()

    def _on_click(self, event=None):
        selected = self.tree.focus()
        if not selected:
            return

        items = self.tree.get_children()
        if selected not in items:
            return

        idx = items.index(selected)
        if idx >= len(self.absolute_paths):
            return

        target = self.absolute_paths[idx]
        self.selected_item = target

        if os.path.isdir(target):
            self.initial_dir = target
            self.update_entry(target)
            self.list_files()
            return

        self.update_entry(target)

    def _up(self):
        current = _System.parse_path(self.initial_dir)
        parent = os.path.dirname(current)

        if not parent or parent == current:
            return

        if not os.path.isdir(parent):
            self.initial_dir = os.path.expanduser("~")
        else:
            self.initial_dir = parent

        self.update_entry(self.initial_dir)
        self.list_files()
