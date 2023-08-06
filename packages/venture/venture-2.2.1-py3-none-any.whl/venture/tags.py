from pathlib import Path
from .util import resolve
from .icons import file_icon_map


path_fragments = ("config",)

# When we look into the directory, if any of these
# files exist, we can assume that the project is related to the
# given language
project_files = {
    "package.json": "js",
    "tsconfig.json": "ts",
    "Pipfile": "py",
    "requirements.txt": "py",
    "pyproject.toml": "py",
    "Gemfile": "rb",
    "Cargo.toml": "rs",
}


def format_tag(icon: str, icon_only: bool = False):
    return f":{icon}:" if icon_only else f"|{icon}|"


def get_tags(
    filepath: str,
    user_tags: list[str],
    icon_only: bool = False,
    no_default_tags: bool = False,
) -> set[str]:

    if no_default_tags:
        return set(user_tags)


    path = Path(resolve(filepath))
    return set(
        user_tags
        + get_tags_from_path(path, icon_only)
        + get_tags_from_dir(path, icon_only)
        + get_tags_from_file(path, icon_only)
    )


def get_tags_from_path(path: Path, icon_only: bool):
    return list(
        format_tag(name, icon_only) for name in path_fragments if name in str(path)
    )


def get_tags_from_dir(path: Path, icon_only: bool):
    """Peaks at the contents of a directory to discover tags"""
    if not path.is_dir():
        return []

    contents = path.iterdir()

    return list(
        format_tag(project_files[p.name], icon_only)
        for p in contents
        if p.name in project_files
    )


def get_tags_from_file(path: Path, icon_only: bool):
    if not path.is_file():
        return []

    extension = path.suffix.lstrip(".")
    if extension in file_icon_map:
        return [format_tag(extension, icon_only)]

    return []
