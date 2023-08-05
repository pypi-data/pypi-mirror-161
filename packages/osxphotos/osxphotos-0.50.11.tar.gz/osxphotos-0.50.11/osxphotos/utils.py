""" Utility functions used in osxphotos """

import datetime
import fnmatch
import hashlib
import importlib
import inspect
import logging
import os
import os.path
import pathlib
import platform
import re
import subprocess
import sys
import unicodedata
import urllib.parse
from plistlib import load as plistload
from typing import Callable, List, Optional, Tuple, Union
from uuid import UUID

import CoreFoundation
import requests
import shortuuid

from ._constants import UNICODE_FORMAT

__all__ = [
    "dd_to_dms_str",
    "expand_and_validate_filepath",
    "get_last_library_path",
    "get_system_library_path",
    "hexdigest",
    "increment_filename_with_count",
    "increment_filename",
    "lineno",
    "list_directory",
    "list_photo_libraries",
    "load_function",
    "noop",
    "normalize_fs_path",
    "normalize_unicode",
    "pluralize",
    "shortuuid_to_uuid",
    "uuid_to_shortuuid",
]


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d - %(message)s",
)

VERSION_INFO_URL = "https://pypi.org/pypi/osxphotos/json"


def _get_logger():
    """Used only for testing

    Returns:
        logging.Logger object -- logging.Logger object for osxphotos
    """
    return logging.Logger(__name__)


def noop(*args, **kwargs):
    """do nothing (no operation)"""
    pass


def lineno(filename):
    """Returns string with filename and current line number in caller as '(filename): line_num'
    Will trim filename to just the name, dropping path, if any."""
    line = inspect.currentframe().f_back.f_lineno
    filename = pathlib.Path(filename).name
    return f"{filename}: {line}"


def _get_os_version():
    # returns tuple of str containing OS version
    # e.g. 10.13.6 = ("10", "13", "6")
    version = platform.mac_ver()[0].split(".")
    if len(version) == 2:
        (ver, major) = version
        minor = "0"
    elif len(version) == 3:
        (ver, major, minor) = version
    else:
        raise (
            ValueError(
                f"Could not parse version string: {platform.mac_ver()} {version}"
            )
        )
    return (ver, major, minor)


def _check_file_exists(filename):
    """returns true if file exists and is not a directory
    otherwise returns false"""
    filename = os.path.abspath(filename)
    return os.path.exists(filename) and not os.path.isdir(filename)


def _get_resource_loc(model_id):
    """returns folder_id and file_id needed to find location of edited photo"""
    """ and live photos for version <= Photos 4.0 """
    # determine folder where Photos stores edited version
    # edited images are stored in:
    # Photos Library.photoslibrary/resources/media/version/XX/00/fullsizeoutput_Y.jpeg
    # where XX and Y are computed based on RKModelResources.modelId

    # file_id (Y in above example) is hex representation of model_id without leading 0x
    file_id = hex_id = hex(model_id)[2:]

    # folder_id (XX) in above example if first two chars of model_id converted to hex
    # and left padded with zeros if < 4 digits
    folder_id = hex_id.zfill(4)[0:2]

    return folder_id, file_id


def _dd_to_dms(dd):
    """convert lat or lon in decimal degrees (dd) to degrees, minutes, seconds"""
    """ return tuple of int(deg), int(min), float(sec) """
    dd = float(dd)
    negative = dd < 0
    dd = abs(dd)
    min_, sec_ = divmod(dd * 3600, 60)
    deg_, min_ = divmod(min_, 60)
    if negative:
        if deg_ > 0:
            deg_ = deg_ * -1
        elif min_ > 0:
            min_ = min_ * -1
        else:
            sec_ = sec_ * -1

    return int(deg_), int(min_), sec_


def dd_to_dms_str(lat, lon):
    """convert latitude, longitude in degrees to degrees, minutes, seconds as string"""
    """ lat: latitude in degrees  """
    """ lon: longitude in degrees """
    """ returns: string tuple in format ("51 deg 30' 12.86\" N", "0 deg 7' 54.50\" W") """
    """ this is the same format used by exiftool's json format """
    # TODO: add this to readme

    lat_deg, lat_min, lat_sec = _dd_to_dms(lat)
    lon_deg, lon_min, lon_sec = _dd_to_dms(lon)

    lat_hemisphere = "N"
    if any([lat_deg < 0, lat_min < 0, lat_sec < 0]):
        lat_hemisphere = "S"

    lon_hemisphere = "E"
    if any([lon_deg < 0, lon_min < 0, lon_sec < 0]):
        lon_hemisphere = "W"

    lat_str = (
        f"{abs(lat_deg)} deg {abs(lat_min)}' {abs(lat_sec):.2f}\" {lat_hemisphere}"
    )
    lon_str = (
        f"{abs(lon_deg)} deg {abs(lon_min)}' {abs(lon_sec):.2f}\" {lon_hemisphere}"
    )

    return lat_str, lon_str


def get_system_library_path():
    """return the path to the system Photos library as string"""
    """ only works on MacOS 10.15 """
    """ on earlier versions, returns None """
    _, major, _ = _get_os_version()
    if int(major) < 15:
        logging.debug(
            f"get_system_library_path not implemented for MacOS < 10.15: you have {major}"
        )
        return None

    plist_file = pathlib.Path(
        str(pathlib.Path.home())
        + "/Library/Containers/com.apple.photolibraryd/Data/Library/Preferences/com.apple.photolibraryd.plist"
    )
    if plist_file.is_file():
        with open(plist_file, "rb") as fp:
            pl = plistload(fp)
    else:
        logging.debug(f"could not find plist file: {str(plist_file)}")
        return None

    return pl.get("SystemLibraryPath")


def get_last_library_path():
    """returns the path to the last opened Photos library
    If a library has never been opened, returns None"""
    plist_file = pathlib.Path(
        str(pathlib.Path.home())
        + "/Library/Containers/com.apple.Photos/Data/Library/Preferences/com.apple.Photos.plist"
    )
    if plist_file.is_file():
        with open(plist_file, "rb") as fp:
            pl = plistload(fp)
    else:
        logging.debug(f"could not find plist file: {str(plist_file)}")
        return None

    # get the IPXDefaultLibraryURLBookmark from com.apple.Photos.plist
    # this is a serialized CFData object
    photosurlref = pl.get("IPXDefaultLibraryURLBookmark")

    if photosurlref is not None:
        # use CFURLCreateByResolvingBookmarkData to de-serialize bookmark data into a CFURLRef
        # pylint: disable=no-member
        # pylint: disable=undefined-variable
        photosurl = CoreFoundation.CFURLCreateByResolvingBookmarkData(
            CoreFoundation.kCFAllocatorDefault, photosurlref, 0, None, None, None, None
        )

        # the CFURLRef we got is a sruct that python treats as an array
        # I'd like to pass this to CFURLGetFileSystemRepresentation to get the path but
        # CFURLGetFileSystemRepresentation barfs when it gets an array from python instead of expected struct
        # first element is the path string in form:
        # file:///Users/username/Pictures/Photos%20Library.photoslibrary/
        photosurlstr = photosurl[0].absoluteString() if photosurl[0] else None

        # now coerce the file URI back into an OS path
        # surely there must be a better way
        if photosurlstr is not None:
            photospath = os.path.normpath(
                urllib.parse.unquote(urllib.parse.urlparse(photosurlstr).path)
            )
        else:
            logging.warning(
                "Could not extract photos URL String from IPXDefaultLibraryURLBookmark"
            )
            return None

        return photospath
    else:
        logging.debug("Could not get path to Photos database")
        return None


def list_photo_libraries():
    """returns list of Photos libraries found on the system"""
    """ on MacOS < 10.15, this may omit some libraries """

    # On 10.15, mdfind appears to find all libraries
    # On older MacOS versions, mdfind appears to ignore some libraries
    # glob to find libraries in ~/Pictures then mdfind to find all the others
    # TODO: make this more robust
    lib_list = list_directory(
        f"{pathlib.Path.home()}/Pictures/", glob="*.photoslibrary"
    )

    # On older OS, may not get all libraries so make sure we get the last one
    if last_lib := get_last_library_path():
        lib_list.append(last_lib)

    output = subprocess.check_output(
        ["/usr/bin/mdfind", "-onlyin", "/", "-name", ".photoslibrary"]
    ).splitlines()
    for lib in output:
        lib_list.append(lib.decode("utf-8"))
    lib_list = sorted(set(lib_list))
    return lib_list


def normalize_fs_path(path: str) -> str:
    """Normalize filesystem paths with unicode in them"""
    # macOS HFS+ uses NFD, APFS doesn't normalize but stick with NFD
    # ref: https://eclecticlight.co/2021/05/08/explainer-unicode-normalization-and-apfs/
    return unicodedata.normalize("NFD", path)


# def findfiles(pattern, path):
#     """Returns list of filenames from path matched by pattern
#     shell pattern. Matching is case-insensitive.
#     If 'path_' is invalid/doesn't exist, returns []."""
#     if not os.path.isdir(path):
#         return []

#     # paths need to be normalized for unicode as filesystem returns unicode in NFD form
#     pattern = normalize_fs_path(pattern)
#     rule = re.compile(fnmatch.translate(pattern), re.IGNORECASE)
#     files = os.listdir(path)
#     return [name for name in files if rule.match(name)]


def list_directory(
    directory: Union[str, pathlib.Path],
    startswith: Optional[str] = None,
    endswith: Optional[str] = None,
    contains: Optional[str] = None,
    glob: Optional[str] = None,
    include_path: bool = False,
    case_sensitive: bool = False,
) -> List[Union[str, pathlib.Path]]:
    """List directory contents and return list of files or directories matching search criteria.
    Accounts for case-insensitive filesystems, unicode filenames. directory can be a str or a pathlib.Path object.

    Args:
        directory: directory to search
        startswith: string to match at start of filename
        endswith: string to match at end of filename
        contains: string to match anywhere in filename
        glob: shell-style glob pattern to match filename
        include_path: if True, return full path to file
        case_sensitive: if True, match case-sensitively

    Returns: List of files or directories matching search criteria as either str or pathlib.Path objects depending on the input type;
    returns empty list if directory is invalid or doesn't exist.

    """
    is_pathlib = isinstance(directory, pathlib.Path)
    if is_pathlib:
        directory = str(directory)

    if not os.path.isdir(directory):
        return []

    startswith = normalize_fs_path(startswith) if startswith else None
    endswith = normalize_fs_path(endswith) if endswith else None
    contains = normalize_fs_path(contains) if contains else None
    glob = normalize_fs_path(glob) if glob else None

    files = [normalize_fs_path(f) for f in os.listdir(directory)]
    if not case_sensitive:
        files_normalized = {f.lower(): f for f in files}
        files = [f.lower() for f in files]
        startswith = startswith.lower() if startswith else None
        endswith = endswith.lower() if endswith else None
        contains = contains.lower() if contains else None
        glob = glob.lower() if glob else None
    else:
        files_normalized = {f: f for f in files}

    if startswith:
        files = [f for f in files if f.startswith(startswith)]
    if endswith:
        endswith = normalize_fs_path(endswith)
        files = [f for f in files if f.endswith(endswith)]
    if contains:
        contains = normalize_fs_path(contains)
        files = [f for f in files if contains in f]
    if glob:
        glob = normalize_fs_path(glob)
        flags = re.IGNORECASE if not case_sensitive else 0
        rule = re.compile(fnmatch.translate(glob), flags)
        files = [f for f in files if rule.match(f)]

    files = [files_normalized[f] for f in files]

    if include_path:
        files = [os.path.join(directory, f) for f in files]
    if is_pathlib:
        files = [pathlib.Path(f) for f in files]

    return files


def normalize_unicode(value):
    """normalize unicode data"""
    if value is None:
        return None
    if isinstance(value, (tuple, list)):
        return tuple(unicodedata.normalize(UNICODE_FORMAT, v) for v in value)
    elif isinstance(value, str):
        return unicodedata.normalize(UNICODE_FORMAT, value)
    else:
        return value


def increment_filename_with_count(
    filepath: Union[str, pathlib.Path], count: int = 0
) -> Tuple[str, int]:
    """Return filename (1).ext, etc if filename.ext exists

        If file exists in filename's parent folder with same stem as filename,
        add (1), (2), etc. until a non-existing filename is found.

    Args:
        filepath: str or pathlib.Path; full path, including file name
        count: int; starting increment value

    Returns:
        tuple of new filepath (or same if not incremented), count

    Note: This obviously is subject to race condition so using with caution.
    """
    dest = filepath if isinstance(filepath, pathlib.Path) else pathlib.Path(filepath)
    dest_files = list_directory(dest.parent, startswith=dest.stem)
    dest_files = [f.stem.lower() for f in dest_files]
    dest_new = f"{dest.stem} ({count})" if count else dest.stem
    dest_new = normalize_fs_path(dest_new)

    while dest_new.lower() in dest_files:
        count += 1
        dest_new = normalize_fs_path(f"{dest.stem} ({count})")
    dest = dest.parent / f"{dest_new}{dest.suffix}"
    return normalize_fs_path(str(dest)), count


def increment_filename(filepath: Union[str, pathlib.Path]) -> str:
    """Return filename (1).ext, etc if filename.ext exists

        If file exists in filename's parent folder with same stem as filename,
        add (1), (2), etc. until a non-existing filename is found.

    Args:
        filepath: str or pathlib.Path; full path, including file name
        force: force the file count to increment by at least 1 even if filepath doesn't exist

    Returns:
        new filepath (or same if not incremented)

    Note: This obviously is subject to race condition so using with caution.
    """
    new_filepath, _ = increment_filename_with_count(filepath)
    return new_filepath


def extract_increment_count_from_filename(filepath: Union[str, pathlib.Path]) -> int:
    """Extract a count from end of file name if it exists or 0 if not; count takes forms file (1).ext, file (2).ext, etc."""
    filepath = str(filepath)
    match = re.search(r"(?s:.*)\((\d+)\)", filepath)
    return int(match[1]) if match else 0


def expand_and_validate_filepath(path: str) -> str:
    """validate and expand ~ in filepath, also un-escapes spaces

    Returns:
        expanded path if path is valid file, else None
    """

    path = re.sub(r"\\ ", " ", path)
    path = pathlib.Path(path).expanduser()
    if path.is_file():
        return str(path)
    return None


def load_function(pyfile: str, function_name: str) -> Callable:
    """Load function_name from python file pyfile"""
    module_file = pathlib.Path(pyfile)
    if not module_file.is_file():
        raise FileNotFoundError(f"module {pyfile} does not appear to exist")

    module_dir = module_file.parent or pathlib.Path(os.getcwd())
    module_name = module_file.stem

    # store old sys.path and ensure module_dir at beginning of path
    syspath = sys.path
    sys.path = [str(module_dir)] + syspath
    module = importlib.import_module(module_name)

    try:
        func = getattr(module, function_name)
    except AttributeError as e:
        raise ValueError(
            f"'{function_name}' not found in module '{module_name}'"
        ) from e

    finally:
        # restore sys.path
        sys.path = syspath

    return func


def format_sec_to_hhmmss(sec: float) -> str:
    """Format seconds to hh:mm:ss"""
    delta = datetime.timedelta(seconds=sec)
    return str(delta).split(".")[0]


def get_latest_version() -> Tuple[Optional[str], str]:
    """Get latest version of osxphotos or None if version can't be retrieved"""
    try:
        url = VERSION_INFO_URL
        response = requests.get(url)
        data = response.json()
        return data["info"]["version"], ""
    except Exception as e:
        return None, e


def pluralize(count: Optional[int], singular: str, plural: str) -> str:
    """Return singular or plural based on count"""
    return singular if count == 1 else plural


def hexdigest(strval: str) -> str:
    """hexdigest of a string, using blake2b"""
    h = hashlib.blake2b(digest_size=20)
    h.update(bytes(strval, "utf-8"))
    return h.hexdigest()


def uuid_to_shortuuid(uuid: str) -> str:
    """Convert uuid to shortuuid"""
    return str(shortuuid.encode(UUID(uuid)))


def shortuuid_to_uuid(short_uuid: str) -> str:
    """Convert shortuuid to uuid"""
    return str(shortuuid.decode(short_uuid)).upper()
