# Authors: Jason Gerard DeRose <jderose@redhat.com>
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
Engine to map ipalib plugins to wehjit widgets.
"""

from controllers import Command
from ipalib import crud

class ParamMapper(object):
    def __init__(self, api, app):
        self._api = api
        self._app = app
        self.__methods = dict()
        for name in dir(self):
            if name.startswith('_'):
                continue
            attr = getattr(self, name)
            if not callable(attr):
                continue
            self.__methods[name] = attr

    def __call__(self, param, cmd):
        key = param.__class__.__name__
        if key in self.__methods:
            method = self.__methods[key]
        else:
            method = self.Str
        return method(param, cmd)

    def Str(self, param, cmd):
        return self._app.new('TextRow',
            label=param.label,
            name=param.name,
            required=param.required,
            value=param.default,
        )

    def Password(self, param, cmd):
        return self._app.new('PasswordRow',
            name=param.name,
            required=param.required,
        )

    def Flag(self, param, cmd):
        return self._app.new('SelectRow',
            name=param.name,
            label=param.label,
        )


class Engine(object):
    def __init__(self, api, app):
        self.api = api
        self.app = app
        self.param_mapper = ParamMapper(api, app)
        self.pages = dict()
        self.jsonurl = self.api.Backend.jsonserver.url.rstrip('/')
        self.info_pages = []

    def add_object_menuitems(self, menu, name):
        obj = self.api.Object[name]
        for cmd in obj.methods():
            p = self.pages[cmd.name]
            menu.add(
                menu.new('MenuItem',
                    label=p.title,
                    href=p.url,
                )
            )

    def build(self):
        for cmd in self.api.Object.user.methods():
            self.pages[cmd.name] = self.build_page(cmd)
        for page in self.pages.itervalues():
            page.menu.label = 'Users'
            self.add_object_menuitems(page.menu, 'user')

        # Add in the info pages:
        page = self.app.new('PageApp', id='api', title='api')
        page.view.add(
            self.app.new('API', api=self.api)
        )
        self.info_pages.append(page)

        for kind in self.api:
            self.build_info_page(kind)
        for page in self.info_pages:
            for p in self.info_pages:
                page.menuset.add(
                    self.app.new('MenuItem',
                        href=p.url,
                        label=p.title,
                    )
                )

    def build_info_page(self, kind):
        # Add in the Object page:
        plugins = tuple(self.api[kind]())
        page = self.app.new('PageApp', id=kind, title=kind)
        info = self.app.new('IPAPlugins', kind=kind, plugins=plugins)
        quick_jump = self.app.new('QuickJump',
            options=tuple((p.name, p.name) for p in plugins)
        )
        page.view.add(info)
        page.actions.add(quick_jump)
        self.info_pages.append(page)
        if kind in self.app.widgets:
            info.add(
                self.app.new(kind)
            )
        return page

    def build_page(self, cmd):
        page = self.app.new('PageCmd',
            cmd=cmd,
            id=cmd.name,
            title=cmd.summary.rstrip('.'),
        )
        page.form.action = page.url
        page.form.method = 'GET'
        page.form.add(
            self.app.new('Hidden', name='__mode__', value='output')
        )
        page.notification = self.app.new('Notification')
        page.view.add(page.notification)
        page.prompt = self.make_prompt(cmd)
        page.show = self.make_show(cmd)
        self.conditional('input', page.actions, self.app.new('Submit'))
        self.conditional('input', page.view, page.prompt)
        self.conditional('output', page.view, page.show)
        return page

    def conditional(self, mode, parent, *children):
        conditional = self.app.new('Conditional', mode=mode)
        conditional.add(*children)
        parent.add(conditional)

    def make_prompt(self, cmd):
        table = self.app.new('FieldTable')
        for param in self._iter_params(cmd.params):
            table.add(
                self.param_mapper(param, cmd)
            )
        return table

    def make_show(self, cmd):
        return self.app.new('Output')

    def _iter_params(self, namespace):
        for param in namespace():
            if param.exclude and 'webui' in param.exclude:
                continue
            yield param
