"""
core
====

The `core` module defines core functions required to perform the migration.
"""

import importlib
import os

from lxml import etree

from . import VERSION_LIST, XSL, MIGRATIONS_PACKAGE, STYLESHEETS_DIR
from .utils import _print


def get_stylesheet(source, target, prefix="migrate"):
    """Provides the stylesheet used to perform a migration from the specified `source` to `target` versions.

    The name of the stylesheet is constructed using the template `{prefix}_v{source}_to_v{target}.xsl`

    :param str source: a valid version string
    :param str target: a valid version string
    :param str prefix: the file name prefix [default: 'migrate']
    :return: the name of the stylesheet file
    :raises: OSError
    """
    stylesheet = os.path.join(STYLESHEETS_DIR,
                              "{prefix}_v{source}_to_v{target}.xsl".format(prefix=prefix, source=source, target=target))
    try:
        assert os.path.exists(os.path.join(STYLESHEETS_DIR, stylesheet))
    except AssertionError:
        raise OSError("requested stylesheet was not found")
    return stylesheet


def get_module(source, target, prefix="migrate"):
    """Provides the module that effects the migration for `source` and `target` versions.

    :param str source: a valid version string
    :param str target: a valid version string
    :param str prefix: the file name prefix [default: 'migrate']
    :return: the module implementing the migration
    """
    module_name = "{package}.{prefix}_v{source}_to_v{target}".format(
        package=MIGRATIONS_PACKAGE,
        prefix=prefix,
        source=source.replace('.', '_'),
        target=target.replace('.', '_'),
    )
    module = importlib.import_module(module_name)
    return module


def get_output_name(input, target, prefix="tmp_"):
    """Provides a meaningful output name given the input file name

    :param str input: the full path to the input file
    :param str target: a valid version string
    :return: the full path to the output file
    :rtype: str
    """
    dirname = os.path.dirname(input)
    basename = os.path.basename(input)
    _input = basename.split('.')
    root = '.'.join(_input[:-1])
    ext = _input[-1]
    output = os.path.join(dirname, '{prefix}{root}_v{target}.{ext}'.format(
        prefix=prefix,
        root=root,
        target=target,
        ext=ext,
    ))
    return output


def get_migration_path(source, target, version_list=VERSION_LIST):
    """Given the source, target versions and VERSION_LIST determine the migration path,
    which is a subset of the `VERSION_LIST`

    :param str source: a valid version string
    :param str target: a valid version string
    :param list version_list: a list of ordered versions from oldest to latest
    :return: a list of tuples of valid version strings
    """
    try:
        start = version_list.index(source)
    except ValueError:
        raise ValueError(
            "invalid migration start: '{}' not found in VERSION_LIST={}".format(source, version_list))
    try:
        end = version_list.index(target)
    except ValueError:
        raise ValueError(
            "invalid migration end: '{}' not found in VERSION_LIST={}".format(target, version_list))
    migration_path = [(version_list[i], version_list[i + 1]) for i in range(start, end)]
    return migration_path


def get_source_version(fn, path="/segmentation/version"):
    """Provides the version of the specified document

    :param str fn: filename as a string
    :param str path: the XPath description to the version string
    :return: version
    :rtype: str
    """
    source_tree = etree.parse(fn)
    source_version = source_tree.xpath("{path}/text()".format(path=path))[0]
    return source_version


def list_versions():
    """
    List the EMDB-SFF versions that are migratable to the current version
    :return: status
    :return: version_count
    """
    version_count = len(VERSION_LIST)
    for version in VERSION_LIST[:-1]:
        _print('* {version}'.format(version=version))
    return os.EX_OK, version_count
