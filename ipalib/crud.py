# Authors:
#   Jason Gerard DeRose <jderose@redhat.com>
#
# Copyright (C) 2008  Red Hat
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
Base classes for standard CRUD operations.
"""

import backend, frontend, parameters, output


class Create(frontend.Method):
    """
    Create a new entry.
    """

    has_output = output.standard_entry

    def get_args(self):
        if self.obj.primary_key:
            yield self.obj.primary_key.clone(attribute=True)

    def get_options(self):
        if self.extra_options_first:
            for option in super(Create, self).get_options():
                yield option
        for option in self.obj.params_minus(self.args):
            yield option.clone(attribute=True)
        if not self.extra_options_first:
            for option in super(Create, self).get_options():
                yield option


class PKQuery(frontend.Method):
    """
    Base class for `Retrieve`, `Update`, and `Delete`.
    """

    def get_args(self):
        if self.obj.primary_key:
            yield self.obj.primary_key.clone(attribute=True, query=True)


class Retrieve(PKQuery):
    """
    Retrieve an entry by its primary key.
    """

    has_output = output.standard_entry


class Update(PKQuery):
    """
    Update one or more attributes on an entry.
    """

    has_output = output.standard_entry

    def get_options(self):
        if self.extra_options_first:
            for option in super(Update, self).get_options():
                yield option
        for option in self.obj.params_minus_pk():
            yield option.clone(attribute=True, required=False, autofill=False)
        if not self.extra_options_first:
            for option in super(Update, self).get_options():
                yield option


class Delete(PKQuery):
    """
    Delete one or more entries.
    """

    has_output = output.standard_delete


class Search(frontend.Method):
    """
    Retrieve all entries that match a given search criteria.
    """

    has_output = output.standard_list_of_entries

    def get_args(self):
        yield parameters.Str('criteria?')

    def get_options(self):
        if self.extra_options_first:
            for option in super(Search, self).get_options():
                yield option
        for option in self.obj.params_minus(self.args):
            yield option.clone(
                attribute=True, query=True, required=False, autofill=False
            )
        if not self.extra_options_first:
            for option in super(Search, self).get_options():
                yield option


class CrudBackend(backend.Connectible):
    """
    Base class defining generic CRUD backend API.
    """

    def create(self, **kw):
        """
        Create a new entry.

        This method should take key word arguments representing the
        attributes the created entry will have.

        If this methods constructs the primary_key internally, it should raise
        an exception if the primary_key was passed.  Likewise, if this method
        requires the primary_key to be passed in from the caller, it should
        raise an exception if the primary key was *not* passed.

        This method should return a dict of the exact entry as it was created
        in the backing store, including any automatically created attributes.
        """
        raise NotImplementedError('%s.create()' % self.name)

    def retrieve(self, primary_key, attributes):
        """
        Retrieve an existing entry.

        This method should take a two arguments: the primary_key of the
        entry in question and a list of the attributes to be retrieved.
        If the list of attributes is None then all non-operational
        attributes will be returned.

        If such an entry exists, this method should return a dict
        representing that entry.  If no such entry exists, this method
        should return None.
        """
        raise NotImplementedError('%s.retrieve()' % self.name)

    def update(self, primary_key, **kw):
        """
        Update an existing entry.

        This method should take one required argument, the primary_key of the
        entry to modify, plus optional keyword arguments for each of the
        attributes being updated.

        This method should return a dict representing the entry as it now
        exists in the backing store.  If no such entry exists, this method
        should return None.
        """
        raise NotImplementedError('%s.update()' % self.name)

    def delete(self, primary_key):
        """
        Delete an existing entry.

        This method should take one required argument, the primary_key of the
        entry to delete.
        """
        raise NotImplementedError('%s.delete()' % self.name)

    def search(self, **kw):
        """
        Return entries matching specific criteria.

        This method should take keyword arguments representing the search
        criteria.  If a key is the name of an entry attribute, the value
        should be treated as a filter on that attribute.  The meaning of
        keys outside this namespace is left to the implementation.

        This method should return and iterable containing the matched
        entries, where each entry is a dict.  If no entries are matched,
        this method should return an empty iterable.
        """
        raise NotImplementedError('%s.search()' % self.name)
