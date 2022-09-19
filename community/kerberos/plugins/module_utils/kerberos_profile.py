#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Utils for manipulation of Kerberos profile
"""
import os

from insights.core.context import Context
from insights.parsers.krb5 import Krb5Configuration


class Krb5ProfileMergeConflictError(BaseException):
    """
    Exception for if we can't merge two krb5 profiles or sections
    """


def merge_krb5_profiles(d1, d2, on_conflict='update'):
    """
    Merges two dicts representing krb5 profiles
    """

    common_sections = set(d1.keys()).union(d2.keys())

    result = {}

    for section in common_sections:
        v1 = d1.get(section, None)
        v2 = d2.get(section, None)

        if v1 is not None and v2 is not None:

            if isinstance(v1, dict) and isinstance(v2, dict):
                # Recursively merge dicts
                result[section] = merge_krb5_profiles(v1, v2, on_conflict=on_conflict)
            else:
                # We have a conflict
                if on_conflict == 'update':
                    result[section] = v2
                elif on_conflict == 'error':
                    raise Krb5ProfileMergeConflictError(
                        f"Conflict in key {section}. "
                        f"Values are \"{v1}\" and \"{v2}\""
                    )
                else:
                    raise NotImplementedError(
                        f"on_conflict cannot be \"{on_conflict}\""
                    )

        else:
            result[section] = v1 or v2

    return result


def parse_profile(path):
    """
    Parse a KDC profile. Follows include and includedir directives
    """
    with open(path) as f:
        lines = f.readlines()

    parse_result = Krb5Configuration(
        context=Context(
            content=lines
        )
    )

    if parse_result.module:
        raise NotImplementedError("module directive not yet supported")

    data = parse_result.data

    # TODO - FILENAME or DIRNAME should be an absolute path. The named file or
    # directory must exist and be readable. Including a directory includes all
    # files within the directory whose names consist solely of alphanumeric
    # characters, dashes, or underscores.
    subfiles = []

    # TODO - to make testing easier, we allowed relative paths, although
    # krb5 won't.
    def make_absolute(subfile):
        if not os.path.exists(subfile):
            return os.path.normpath(os.path.join(
                os.path.dirname(path), subfile
            ))

        return subfile

    for f in parse_result.include:
        subfiles.append(f)

    for subdir in parse_result.includedir:

        for file in os.listdir(make_absolute(subdir)):
            subfiles.append(os.path.join(subdir, file))

    # TODO - the order is important here if there are conflicts
    for subfile in subfiles:
        data = merge_krb5_profiles(
            data,
            parse_profile(make_absolute(subfile)),
            on_conflict='error'
        )

    return data


def generate_profile(data):
    return "\n".join([
        generate_profile_section(section_name, section_data)
        for section_name, section_data in data.items()
    ])


def generate_profile_section(section_name, section_data):
    if len(section_data):
        return "\n".join([
            f"[{section_name}]",
        ] + [
            generate_profile_setting(key, value)
            for key, value in section_data.items()
        ])

    else:
        return ""


def generate_profile_setting(key, value):
    value_str = generate_profile_setting_value(value)
    return f"{key} = {value_str}"


def generate_profile_setting_value(value):
    if isinstance(value, dict):
        settings_str = "\n".join([
            generate_profile_setting(key, subvalue)
            for key, subvalue in value.items()
        ])
        return "{\n    %s\n}" % settings_str
    elif isinstance(value, (str, int)):
        return str(value)
    else:
        raise NotImplementedError(
            f"Conversion of {type(value)} {value} into str"
        )
