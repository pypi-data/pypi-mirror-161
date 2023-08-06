"""
sfftk-migrate
==============

This is a simple tool to allow users to easily migrate older versions of EMDB-SFF files to the latest (supported version).
It has only one dependency: `lxml` which effects part of the migrations.

Presently it only works with XML (.sff) EMDB-SFF files.

How does it work?
-----------------

Each migration consists of two components:

1. a Python module which implements a `migrate` function, and

2. an XSL stylesheet which defines how the `source` is transformed into the `target`

The `migrate` function in (1) has the following signature:

.. code-block:: python

    def migrate(infile, outfile, stylesheet, args, encoding='utf-8', **params):
        ...

where `infile` and `outfile` are the names of the source and target files, `stylesheet` is the
XSL file, `args` is the argument namespace, `encoding` defines what encoding the outfile will
be writing in, and `**params` is a dictionary of any params specified in the XSL file.

Please reference https://www.w3schools.com/xml/xsl_intro.asp on how XSL works.

Migrations are effected using the `migrate.do_migration` function which has the following signature:

.. code-block:: python

    def do_migration(args, value_list=None, version_list=VERSION_LIST):
        ...


Lessons learned in using `lxml`
---------------------------------

* etree.parse() takes XML files/file objects and returns an ElementTree

* etree.XML() takes a string and returns an Element regardless of the content

* etree.ElementTree(root_element) converts an element into an ElementTree

* etree.XSLT() takes an ElementTree or Element object and returns a transformer object;
a transformer object should take an ElementTree (but seems to also take Element objects)

* the result of a transformation is an _XSLTResultTree which behaves like an ElementTree but submits to str()

from: https://lxml.de/xpathxslt.html#xslt-result-objects
It is possible to pass parameters, in the form of XPath expressions, to the XSLT template:

>>> xslt_tree = etree.XML('''\
... <xsl:stylesheet version="1.0"
...     xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
...     <xsl:param name="a" />
...     <xsl:template match="/">
...         <foo><xsl:value-of select="$a" /></foo>
...     </xsl:template>
... </xsl:stylesheet>''')
>>> transform = etree.XSLT(xslt_tree)
>>> doc_root = etree.XML('<a><b>Text</b></a>')

The parameters are passed as keyword parameters to the transform call. First, let's try passing in a simple integer expression:

>>> result = transform(doc_root, a="5")
>>> str(result)
'<?xml version="1.0"?>\n<foo>5</foo>\n'

"""

import os

SFFTK_MIGRATIONS_VERSION = '0.1.1'
VERSION_LIST = [
    '0.7.0.dev0',
    '0.8.0.dev1'
]
TEST_DATA_PATH = os.path.join(os.path.dirname(__file__))

XSL = os.path.join(TEST_DATA_PATH, 'data', 'xsl')
XML = os.path.join(TEST_DATA_PATH, 'data', 'xml')

MIGRATIONS_PACKAGE = 'sfftk_migrate.migrations'
STYLESHEETS_DIR = os.path.join(os.path.dirname(__file__), 'stylesheets')

ENDIANNESS = {
    "little": "<",
    "big": ">",
}
MODE = {
    "int8": "b",
    "uint8": "B",
    "int16": "h",
    "uint16": "H",
    "int32": "i",
    "uint32": "I",
    "int64": "q",
    "uint64": "Q",
    "float32": "f",
    "float64": "d"
}


