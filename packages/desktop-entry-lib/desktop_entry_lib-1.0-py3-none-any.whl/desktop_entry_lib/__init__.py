from typing import Union, Optional, Literal
import subprocess
import locale
import os
import re


__version__ = "1.0"
"The version"


def _parse_desktop_sections(content: str) -> dict[str, dict[str, str]]:
    sections = {}
    current_section = None
    for line in content.splitlines():
        if line.startswith("[") and line.endswith("]"):
            current_section = line[1:-1]
            sections[current_section] = {}
        elif current_section is None:
            continue
        else:
            try:
                key, value = line.split("=", 1)
                sections[current_section][key] = value
            except ValueError:
                continue
    return sections


def _string_to_bool(string: Optional[str]) -> Optional[bool]:
    "Converts a String to a Boolean"
    if string is None:
        return None
    elif string.lower() == "true":
        return True
    elif string.lower() == "false":
        return False
    else:
        return None


def get_xdg_data_dirs() -> list[str]:
    "Get all XDG DATA DIRS"
    try:
        return os.getenv("XDG_DATA_DIRS").split(":")
    except AttributeError:
        return [os.path.expanduser("~/.local/share"), "/usr/share"]


def _get_icon_size_dirs(path: str) -> list[str]:
    size_list = []
    for i in os.listdir(path):
        if not os.path.isdir(os.path.join(path, i)) or not re.match(r"\d+x\d+", i):
            continue

        size_list.append(int(re.search(r"^\d+", i).group()))

    size_list.sort(reverse=True)

    dir_list = []
    for i in size_list:
        dir_list.append(f"{i}x{i}")

    return dir_list


def get_icon_path(icon_name: str) -> Optional[str]:
    for data_dir in get_xdg_data_dirs():
        scalable_dir = os.path.join(data_dir, "icons", "hicolor", "scalable")
        if os.path.isdir(scalable_dir):
            for directory in os.listdir(scalable_dir):
                icon_path = os.path.join(scalable_dir, directory, icon_name + ".svg")
                if os.path.isfile(icon_path):
                    return icon_path
        for size in _get_icon_size_dirs(os.path.join(data_dir, "icons", "hicolor")):
            size_dir = os.path.join(data_dir, "icons", "hicolor", size)
            for directory in os.listdir(size_dir):
                icon_path = os.path.join(size_dir, directory, icon_name + ".png")
                if os.path.isfile(icon_path):
                    return icon_path
        if os.path.isdir(os.path.join(data_dir, "pixmaps")):
            if os.path.isfile(os.path.join(data_dir, "pixmaps", icon_name + ".png")):
                return os.path.join(data_dir, "pixmaps", icon_name + ".png")

    return None


class TranslatableKey:
    def __init__(self) -> None:
        self.default_text: str = ""
        "The untranslated text"

        self.translations: dict[str, str] = {}
        "The translations"

    def get_translated_text(self) -> str:
        "Returns the text for the current language"
        current_lang = locale.getlocale()[0]
        if current_lang in self.translations:
            return self.translations[current_lang]
        elif current_lang.split("_")[0] in self.translations:
            return self.translations[current_lang.split("_")[0]]
        else:
            return self.default_text

    def load_section(self, section: dict[str, str], search_key: str) -> None:
        self.clear()

        for key, value in section.items():
            if not key.startswith(search_key):
                continue

            if search_key == key:
                self.default_text = value
            else:
                try:
                    lang = re.search(r"(?<=\[).+(?=\]$)", key).group()
                    self.translations[lang] = value
                except AttributeError:
                    continue

    def get_text(self, entry_key) -> str:
        if self.default_text == "":
            return ""

        text = f"{entry_key}={self.default_text}\n"
        for key, value in self.translations.items():
            text += f"{entry_key}[{key}]={value}\n"
        return text

    def clear(self) -> None:
        "Clear"
        self.default_text = ""
        self.translations.clear()


class TranslatableListKey:
    def __init__(self) -> None:
        self.default_list: list[str] = []
        self.translations: dict[str, list[str]] = {}

    def load_section(self, section: dict[str, str], search_key: str) -> None:
        self.clear()

        for key, value in section.items():
            if not key.startswith(search_key):
                continue

            if search_key == key:
                self.default_text = value.removesuffix(";").split(";")
            else:
                try:
                    lang = re.search(r"(?<=\[).+(?=\]$)", key).group()
                    self.translations[lang] = value.removesuffix(";").split(";")
                except AttributeError:
                    continue

    def get_text(self, entry_key) -> str:
        if len(self.default_list) == 0:
            return ""

        text = f"{entry_key}={';'.join(self.default_text)};\n"
        for key, value in self.translations.items():
            text += f"{entry_key}[{key}]={';'.join(value)};\n"
        return text

    def clear(self) -> None:
        self.default_list.clear()
        self.translations.clear()


class DesktopEntry:
    def __init__(self) -> None:
        self.Type: Literal["Application", "Link", "Directory"] = "Application"
        "The Type Key"

        self.Version: Optional[Literal["1.0", "1.1", "1.2", "1.3", "1.4", "1.5"]] = None
        "The Version Key"

        self.Name: TranslatableKey = TranslatableKey()
        "The Name Key"

        self.GenericName: TranslatableKey = TranslatableKey()
        "The GenericName Key"

        self.NoDisplay: Optional[bool] = None
        "The NoDisplay Key"

        self.Comment: TranslatableKey = TranslatableKey()
        "The Comment Key"

        self.Icon: Optional[str] = None
        "The Icon Key"

        self.Hidden: Optional[bool] = None
        "The Hidden Key"

        self.OnlyShowIn: list[str] = []
        "The OnlyShowIn Key"

        self.NotShowIn: list[str] = []
        "The NotShowIn Key"

        self.DBusActivatable: Optional[bool] = None

        self.TryExec: Optional[str] = None

        self.Exec: Optional[str] = None

        self.Path: Optional[str] = None

        self.Terminal: Optional[bool] = None
        "The Terminal Key"

        self.MimeType: list[str] = []
        "The MimeType Key"

        self.Categories: list[str] = []
        "The Categories Key"

        self.Implements: list[str] = []
        "The Implements Key"

        self.Keywords: TranslatableListKey = TranslatableListKey()
        "The Keywords Key"

        self.StartupNotify: Optional[bool] = None
        "The StartupNotify Key"

        self.URL: Optional[str] = None
        "The URL Key"

        self.PrefersNonDefaultGPU: Optional[bool] = None
        "The PrefersNonDefaultGPU Key"

        self.SingleMainWindow: Optional[bool] = None
        "The SingleMainWindow Key"

        self.CustomKeys: dict[str, str] = {}
        "The Keys starting with X-"

    def should_show(self) -> bool:
        "Returns if a dektop entry should be displayed in the menu"
        if self.NoDisplay:
            return False

        return True

    def get_text(self) -> str:
        "Returns the content of the desktop entry"
        text = "[Desktop Entry]\n"
        text += f"Type={self.Type}\n"
        if self.Version is not None:
            text += f"Version={self.Version}\n"
        text += self.Name.get_text("Name")
        text += self.GenericName.get_text("GenericName")

        if self.NoDisplay is not None:
            text += f"NoDisplay={self.NoDisplay}"

        text += self.Comment.get_text("Comment")
        if self.Icon is not None:
            text += f"Icon={self.Icon}\n"
        if self.Hidden is not None:
            text += f"Hidden={self.Hidden}\n"

        if len(self.OnlyShowIn) != 0:
            text += "OnlyShowIn=" + ";".join(self.OnlyShowIn) + ";\n"

        if len(self.NotShowIn) != 0:
            text += "NotShowIn=" + ";".join(self.NotShowIn) + ";\n"

        if self.TryExec is not None:
            text += f"TryExec={self.TryExec}\n"

        if self.Exec is not None:
            text += f"Exec={self.Exec}\n"

        if self.Path is not None:
            text += f"Exec={self.Exec}\n"

        if len(self.MimeType) != 0:
            text += "MimeType=" + ";".join(self.MimeType) + ";\n"

        if len(self.Categories) != 0:
            text += "Categories=" + ";".join(self.Categories) + ";\n"

        if len(self.Implements) != 0:
            text += "Implements=" + ";".join(self.Implements) + ";\n"

        text += self.Keywords.get_text("Keywords")

        if self.StartupNotify is not None:
            text += f"StartupNotify={self.StartupNotify}\n"

        if self.URL is not None:
            text += f"URL={self.URL}\n"

        if self.PrefersNonDefaultGPU is not None:
            text += f"PrefersNonDefaultGPU={self.PrefersNonDefaultGPU}\n"

        if self.SingleMainWindow is not None:
            text += f"SingleMainWindow={self.SingleMainWindow}\n"

        for key, value in self.CustomKeys.items():
            if key.startswith("X-"):
                text += f"{key}={value}\n"

        return text

    def write_file(self, path: Union[str, os.PathLike]) -> None:
        "Writes a .desktop file"
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(self.get_text())

    @classmethod
    def from_string(cls, text: str):
        "Loads the content of a .desktop file from a string"
        entry = cls()

        sections = _parse_desktop_sections(text)

        if "Desktop Entry" not in sections:
            return entry

        entry.Type = sections["Desktop Entry"].get("Type", "Application")
        entry.Version = sections["Desktop Entry"].get("Version", None)
        entry.Name.load_section(sections["Desktop Entry"], "Name")
        entry.GenericName.load_section(sections["Desktop Entry"], "GenericName")
        entry.NoDisplay = _string_to_bool(sections["Desktop Entry"].get("NoDisplay", None))
        entry.Comment.load_section(sections["Desktop Entry"], "Comment")
        entry.Icon = sections["Desktop Entry"].get("Icon", None)
        entry.Hidden = _string_to_bool(sections["Desktop Entry"].get("Hidden", None))

        if "OnlyShowIn" in sections["Desktop Entry"]:
            entry.OnlyShowIn = sections["Desktop Entry"]["OnlyShowIn"].removesuffix(";").split(";")

        if "NotShowIn" in sections["Desktop Entry"]:
            entry.NotShowIn = sections["Desktop Entry"]["NotShowIn"].removesuffix(";").split(";")

        entry.DBusActivatable = bool(sections["Desktop Entry"].get("DBusActivatable", None))
        entry.TryExec = sections["Desktop Entry"].get("TryExec", None)
        entry.Exec = sections["Desktop Entry"].get("Exec", None)
        entry.Path = sections["Desktop Entry"].get("Path", None)
        entry.Terminal = _string_to_bool(sections["Desktop Entry"].get("Terminal", None))

        if "MimeType" in sections["Desktop Entry"]:
            entry.MimeType = sections["Desktop Entry"]["MimeType"].removesuffix(";").split(";")

        if "Categories" in sections["Desktop Entry"]:
            entry.Categories = sections["Desktop Entry"]["Categories"].removesuffix(";").split(";")

        if "Implements" in sections["Desktop Entry"]:
            entry.Categories = sections["Desktop Entry"]["Implements"].removesuffix(";").split(";")

        entry.Keywords.load_section(sections["Desktop Entry"], "Keywords")
        entry.StartupNotify = _string_to_bool(sections["Desktop Entry"].get("StartupNotify", None))
        entry.URL = sections["Desktop Entry"].get("URL", None)
        entry.PrefersNonDefaultGPU = _string_to_bool(sections["Desktop Entry"].get("PrefersNonDefaultGPU", None))
        entry.SingleMainWindow = _string_to_bool(sections["Desktop Entry"].get("SingleMainWindow", None))

        for key, value in sections["Desktop Entry"].items():
            if key.startswith("X-"):
                entry.CustomKeys[key] = value

        return entry

    @classmethod
    def from_file(cls, path: Union[str, os.PathLike]):
        "Returns a desktop entry from the given file"
        with open(path, "r", encoding="utf-8", newline="\n") as f:
            return cls.from_string(f.read())

    @classmethod
    def from_id(cls, desktop_id: str):
        "Returns a desktop entry from the given id"
        for i in get_xdg_data_dirs():
            entry_path = os.path.join(i, "applications", desktop_id + ".desktop")
            if os.path.isfile(entry_path):
                return cls.from_file(entry_path)

class DesktopEntryCollection:
    def __init__(self) -> None:
        self.desktop_entries: dict[str, DesktopEntry] = {}
        "The desktop entries"

        self._categories: dict[str, list[str]] = {}
        self._mime_types: dict[str, list[str]] = {}

    def load_file(self, path: Union[str, os.PathLike]):
        "Loads the given file"
        entry = DesktopEntry.from_file(path)

        for i in entry.Categories:
            if i not in self._categories:
                self._categories[i] = []
            self._categories[i].append(entry)

        for i in entry.MimeType:
            if i not in self._mime_types:
                self._mime_types[i] = []
            self._mime_types[i].append(entry)

        self.desktop_entries[str(path).removesuffix(".desktop")] = entry

    def load_directory(self, path: Union[str, os.PathLike]) -> None:
        "Loads all desktop entries from the given directory"
        for i in os.listdir(path):
            if i.endswith(".desktop"):
                self.load_file(os.path.join(path, i))

    def load_menu(self) -> None:
        "Loads all desktop entries from the menu"
        for i in get_xdg_data_dirs():
            menu_dir = os.path.join(i, "applications")
            if os.path.isdir(menu_dir):
                self.load_directory(menu_dir)

    def load_desktop(self) -> None:
        "Loads all desktop entries files from the Desktop"
        desktop_path = subprocess.check_output(["xdg-user-dir", "DESKTOP"]).decode("utf-8").strip()
        if os.path.isdir(desktop_path):
            self.load_directory(desktop_path)

    def get_entries_by_category(self, category: str) -> list[DesktopEntry]:
        "Returns a list of all desktop entries that have the given category"
        if category not in self._categories:
            return []

        entry_list = []
        for i in self._categories[category]:
            entry_list.append(self.desktop_entries[i])
        return entry_list

    def get_entries_by_mime_type(self, mime_type: str) -> list[DesktopEntry]:
        "Returns a list of all desktop entries that can open the given MimeType"
        if mime_type not in self._mime_types:
            return []

        entry_list = []
        for i in self._mime_types[mime_type]:
            entry_list.append(self.desktop_entries[i])
        return entry_list

    def get_visible_entries(self) -> list[DesktopEntry]:
        "Get a list of all desktop enties that should be shown"
        entry_list = []
        for i in self.desktop_entries.values():
            if i.should_show():
                entry_list.append(i)
        return entry_list
