"""Click parameter types for osxphotos CLI"""
import datetime
import os
import pathlib
import re

import bitmath
import click
import pytimeparse2

from osxphotos.export_db_utils import export_db_get_version
from osxphotos.photoinfo import PhotoInfoNone
from osxphotos.phototemplate import PhotoTemplate, RenderOptions
from osxphotos.timeutils import time_string_to_datetime, utc_offset_string_to_seconds
from osxphotos.timezones import Timezone
from osxphotos.utils import expand_and_validate_filepath, load_function

__all__ = [
    "BitMathSize",
    "DateOffset",
    "DateTimeISO8601",
    "ExportDBType",
    "FunctionCall",
    "TemplateString",
    "TimeISO8601",
    "TimeOffset",
    "TimeString",
    "UTCOffset",
]


class DateTimeISO8601(click.ParamType):

    name = "DATETIME"

    def convert(self, value, param, ctx):
        try:
            return datetime.datetime.fromisoformat(value)
        except Exception:
            self.fail(
                f"Invalid datetime format {value}. "
                "Valid format: YYYY-MM-DD[*HH[:MM[:SS[.fff[fff]]]][+HH:MM[:SS[.ffffff]]]]"
            )


class BitMathSize(click.ParamType):

    name = "BITMATH"

    def convert(self, value, param, ctx):
        try:
            value = bitmath.parse_string(value)
        except ValueError:
            # no units specified
            try:
                value = int(value)
                value = bitmath.Byte(value)
            except ValueError as e:
                self.fail(
                    f"{value} must be specified as bytes or using SI/NIST units. "
                    + "For example, the following are all valid and equivalent sizes: '1048576' '1.048576MB', '1 MiB'."
                )
        return value


class TimeISO8601(click.ParamType):

    name = "TIME"

    def convert(self, value, param, ctx):
        try:
            return datetime.time.fromisoformat(value).replace(tzinfo=None)
        except Exception:
            self.fail(
                f"Invalid time format {value}. "
                "Valid format: HH[:MM[:SS[.fff[fff]]]][+HH:MM[:SS[.ffffff]]] "
                "however, note that timezone will be ignored."
            )


class FunctionCall(click.ParamType):
    name = "FUNCTION"

    def convert(self, value, param, ctx):
        if "::" not in value:
            self.fail(
                f"Could not parse function name from '{value}'. "
                "Valid format filename.py::function"
            )

        filename, funcname = value.split("::")

        filename_validated = expand_and_validate_filepath(filename)
        if not filename_validated:
            self.fail(f"'{filename}' does not appear to be a file")

        try:
            function = load_function(filename_validated, funcname)
        except Exception as e:
            self.fail(f"Could not load function {funcname} from {filename_validated}")

        return (function, value)


class ExportDBType(click.ParamType):

    name = "EXPORTDB"

    def convert(self, value, param, ctx):
        try:
            export_db_name = pathlib.Path(value)
            if export_db_name.is_dir():
                raise click.BadParameter(f"{value} is a directory")
            if export_db_name.is_file():
                # verify it's actually an osxphotos export_db
                # export_db_get_version will raise an error if it's not valid
                osxphotos_ver, export_db_ver = export_db_get_version(value)
            return value
        except Exception:
            self.fail(f"{value} exists but is not a valid osxphotos export database. ")


class TemplateString(click.ParamType):
    """Validate an osxphotos template language (OTL) template string"""

    name = "OTL_TEMPLATE"

    def convert(self, value, param, ctx):
        try:
            cwd = os.getcwd()
            _, unmatched = PhotoTemplate(photo=PhotoInfoNone()).render(
                value,
                options=RenderOptions(export_dir=cwd, dest_path=cwd, filepath=cwd),
            )
            if unmatched:
                self.fail(f"Template '{value}' contains unknown field(s): {unmatched}")
            return value
        except ValueError as e:
            self.fail(e)


class TimeString(click.ParamType):
    """A timestring in format HH:MM:SS, HH:MM:SS.fff, HH:MM"""

    name = "TIMESTRING"

    def convert(self, value, param, ctx):
        try:
            return time_string_to_datetime(value)
        except ValueError:
            self.fail(
                f"Invalid time format: {value}. "
                "Valid format for time: 'HH:MM:SS', 'HH:MM:SS.fff', 'HH:MM'"
            )


class DateOffset(click.ParamType):
    """A date offset string in the format ±D days, ±W weeks, ±Y years, ±D where D is days"""

    name = "DATEOFFSET"

    def convert(self, value, param, ctx):
        # if it's a single number treat it as days
        # but pytimeparse2 treats is as seconds so need to verify it's just a number and if so,
        # convert it to seconds
        value = value.strip()
        if re.match(r"^[+-]?\s*?\d+$", value):
            # just a number
            # strip any whitespace, e.g. for "+ 1" or "- 1"
            value = "".join(value.split())
            try:
                return datetime.timedelta(days=int(value))
            except ValueError:
                self.fail(
                    f"Invalid date offset format: {value}. "
                    "Valid format for date/time offset: '±D days', '±W weeks', '±M months', '±D' where D is days "
                )

        offset = pytimeparse2.parse(value)
        if offset is not None:
            offset = offset / 86400
            return datetime.timedelta(days=offset)

        self.fail(
            f"Invalid date offset format: {value}. "
            "Valid format for date/time offset: '±D days', '±W weeks', '±M months', '±D' where D is days "
        )


class TimeOffset(click.ParamType):
    """A time offset string in the format [+-]HH:MM[:SS[.fff[fff]]] or +1 days, -2 hours, -18000, etc"""

    name = "TIMEOFFSET"

    def convert(self, value, param, ctx):
        offset = pytimeparse2.parse(value)
        if offset is not None:
            return datetime.timedelta(seconds=offset)

        self.fail(
            f"Invalid time offset format: {value}. "
            "Valid format for date/time offset: '±HH:MM:SS', '±H hours' (or hr), '±M minutes' (or min), '±S seconds' (or sec), '±S' (where S is seconds)"
        )


class UTCOffset(click.ParamType):
    """A UTC offset timezone in format ±[hh]:[mm], ±[h]:[mm], or ±[hh][mm]"""

    name = "UTC_OFFSET"

    def convert(self, value, param, ctx):
        try:
            offset_seconds = utc_offset_string_to_seconds(value)
            return Timezone(offset_seconds)
        except Exception:
            self.fail(
                f"Invalid timezone format: {value}. "
                "Valid format for timezone offset: '±HH:MM', '±H:MM', or '±HHMM'"
            )
