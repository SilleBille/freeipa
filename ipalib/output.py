# Authors:
#   Jason Gerard DeRose <jderose@redhat.com>
#
# Copyright (C) 2009  Red Hat
# see file 'COPYING' for use and warranty information
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; version 2 only
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

"""
Simple description of return values.
"""

from inspect import getdoc
from types import NoneType
from plugable import ReadOnly, lock


class Output(ReadOnly):
    """
    Simple description of a member in the return value ``dict``.
    """

    type = None
    validate = None
    doc = None

    def __init__(self, name, type=None, doc=None):
        self.name = name
        if type is not None:
            self.type = type
        if doc is not None:
            self.doc = doc
        lock(self)

    def __repr__(self):
        return '%s(%r, %r, %r)' % (
            self.__class__.__name__, self.name, self.type, self.doc,
        )


class Entry(Output):
    type = dict
    doc = 'A dictionary representing an LDAP entry'


emsg = """%s.validate_output() => %s.validate():
  output[%r][%d]: need a %r; got a %r: %r"""

class ListOfEntries(Output):
    type = (list, tuple)
    doc = 'A list of LDAP entries'

    def validate(self, cmd, entries):
        assert isinstance(entries, self.type)
        for (i, entry) in enumerate(entries):
            if not isinstance(entry, dict):
                raise TypeError(emsg % (cmd.name, self.__class__.__name__,
                    self.name, i, dict, type(entry), entry)
                )


result = Output('result', doc='All commands should at least have a result')

summary = Output('summary', (unicode, NoneType),
    'User-friendly description of action performed'
)

value = Output('value', unicode,
    "The primary_key value of the entry, e.g. 'jdoe' for a user"
)

standard = (result, summary)

standard_entry = (
    Entry('result'),
    value,
    summary,
)

standard_list_of_entries = (
    ListOfEntries('result'),
    Output('count', int, 'Number of entries returned'),
    Output('truncated', bool, 'True if not all results were returned'),
    summary,
)

standard_delete = (
    Output('result', bool, 'True means the operation was successful'),
    value,
    summary,
)

standard_value = standard_delete
