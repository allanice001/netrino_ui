from __future__ import absolute_import, print_function
from __future__ import unicode_literals

import logging
import traceback

import tachyon.ui
import json
import sys

from tachyon.common import RestClient
from collections import OrderedDict
from netrino.ui import model as modelui
from .controllers import *

import nfw


@nfw.app.resources()
class ServiceRequest(object):

    def __init__(self, app):
        app.router.add(nfw.HTTP_GET, '/infrastructure/network/sr/create',
                       self.create, 'network:admin')
        app.router.add(nfw.HTTP_POST, '/infrastructure/network/sr/create',
                       self.create, 'network:admin')
        app.router.add(nfw.HTTP_GET, '/infrastructure/network/sr',
                       self.get, 'network:admin')
        app.router.add(nfw.HTTP_GET, '/infrastructure/network/sr/view',
                       self.getjson, 'network:admin')
        app.router.add(nfw.HTTP_GET, '/infrastructure/network/sr/view/{id}',
                       self.get, 'network:admin')
        app.router.add(nfw.HTTP_GET, '/infrastructure/network/sr/edit/{id}/activate',
                       self.activate, 'network:admin')
        app.router.add(nfw.HTTP_GET, '/infrastructure/network/sr/edit/{id}/deactivate',
                       self.deactivate, 'network:admin')

        app.context['menu'].add(
            '/Infrastructure/Network/Service Requests', '/infrastructure/network/sr', 'network:admin')

    def create(self, req, resp):
        createSR(req, resp)

    def get(self, req, resp, id=None):
        viewSR(req, resp, id=id)

    def getjson(self, req, resp):
        getSelect2(req, resp, service_requests)

    def activate(self, req, resp, id):
        activateSR(req, resp, id=id)

    def deactivate(self, req, resp, id):
        deactivateSR(req, resp, id=id)


@nfw.app.resources()
class InterfaceGroups(object):

    def __init__(self, app):
        app.router.add(nfw.HTTP_GET, '/infrastructure/network/igroup/create',
                       self.create, 'network:admin')
        app.router.add(nfw.HTTP_POST, '/infrastructure/network/igroup/create',
                       self.create, 'network:admin')
        app.router.add(nfw.HTTP_GET, '/infrastructure/network/igroup',
                       self.get, 'network:admin')
        app.router.add(nfw.HTTP_GET, '/infrastructure/network/igroup/view',
                       self.getjson, 'network:admin')
        app.router.add(nfw.HTTP_GET, '/infrastructure/network/igroup/view/{id}',
                       self.get, 'network:admin')
        app.router.add(nfw.HTTP_GET, '/infrastructure/network/igroup/edit/{id}',
                       self.edit, 'network:admin')
        app.router.add(nfw.HTTP_POST, '/infrastructure/network/igroup/edit/{id}',
                       self.edit, 'network:admin')
        app.router.add(nfw.HTTP_GET, '/infrastructure/network/igroup/delete/{id}',
                       self.delete, 'network:admin')

        app.context['menu'].add(
            '/Infrastructure/Network/Interface Groups', '/infrastructure/network/igroup', 'network:admin')

    def create(self, req, resp):
        createIGroup(req, resp)

    def get(self, req, resp, id=None):
        viewIGroup(req, resp, id=id)

    def getjson(self, req, resp, id=None):
        api = RestClient(req.context['restapi'])
        response_headers, result = api.execute(
            nfw.HTTP_GET, "/infrastructure/network/igroups?view=select2")
        return json.dumps(result, indent=4)

    def edit(self, req, resp, id):
        editIGroup(req, resp, id=id)

    def delete(self, req, resp, id):
        deleteIGroup(req, resp, id=id)


@nfw.app.resources()
class Service(object):

    def __init__(self, app):
        app.router.add(nfw.HTTP_GET, '/infrastructure/network/service',
                       self.get, 'network:admin')
        app.router.add(nfw.HTTP_GET, '/infrastructure/network/service/view/{id}',
                       self.get, 'network:admin')
        app.router.add(nfw.HTTP_GET, '/infrastructure/network/service/create',
                       self.create, 'network:admin')
        app.router.add(nfw.HTTP_POST, '/infrastructure/network/service/create',
                       self.create, 'network:admin')
        app.router.add(nfw.HTTP_GET, '/infrastructure/network/service/edit/{id}',
                       self.edit, 'network:admin')
        app.router.add(nfw.HTTP_POST, '/infrastructure/network/service/edit/{id}',
                       self.edit, 'network:admin')
        app.router.add(nfw.HTTP_GET, '/infrastructure/network/service/delete/{id}',
                       self.delete, 'network:admin')

        app.context['menu'].add(
            '/Infrastructure/Network/Services', '/infrastructure/network/service', 'network:admin')

    def get(self, req, resp, id=None):
        return viewService(req, resp, id)

    def create(self, req, resp):
        createService(req, resp)

    def edit(self, req, resp, id):
        editService(req, resp, id)

    def delete(self, req, resp, id):
        deleteService(req, resp, id=id)


@nfw.app.resources()
class NetworkDevice(object):

    def __init__(self, app):
        app.router.add(nfw.HTTP_GET, '/infrastructure/network/device/create',
                       self.create, 'network:admin')
        app.router.add(nfw.HTTP_POST, '/infrastructure/network/device/create',
                       self.create, 'network:admin')
        app.router.add(nfw.HTTP_GET, '/infrastructure/network/device',
                       self.get, 'network:admin')
        app.router.add(nfw.HTTP_GET, '/infrastructure/network/device/{id}/ports',
                       self.getports, 'network:admin')
        app.router.add(nfw.HTTP_GET, '/infrastructure/network/device/{id}/ports/igroup',
                       self.portsigroup, 'network:admin')
        app.router.add(nfw.HTTP_GET, '/infrastructure/network/device/view/{id}',
                       self.get, 'network:admin')
        app.router.add(nfw.HTTP_GET, '/infrastructure/network/device/edit/{id}',
                       self.edit, 'network:admin')
        app.router.add(nfw.HTTP_POST, '/infrastructure/network/device/edit/{id}',
                       self.edit, 'network:admin')
        app.router.add(nfw.HTTP_GET, '/infrastructure/network/device/delete/{id}',
                       self.delete)
        app.router.add(nfw.HTTP_POST, '/infrastructure/network/device/delete/{id}',
                       self.delete)

        app.context['menu'].add(
            '/Infrastructure/Network/Devices', '/infrastructure/network/device', 'network:admin')

    def get(self, req, resp, id=None):
        return viewDevice(req, resp, id)

    def create(self, req, resp):
        if req.method == 'GET':
            createDevice(req, resp)
        elif req.method == 'POST':
            result = createDevicePost(req, resp)
            viewDevice(req, resp)

    def getports(self, req, resp, id):
        result = getPorts(req, id)
        return result

    def portsigroup(self, req, resp, id):
        portsIGroup(req, resp, id)

    def edit(self, req, resp, id):
        if req.method == 'GET':
            editDevice(req, resp, id=id)
        elif req.method == 'POST':
            result = updateDevice(req, id)
            viewDevice(req, resp, id=id, errors=result)

    def delete(self, req, resp, device_id=None):
        if req.method == 'GET':
            confirmRMdevice(req, resp, id=id)
        elif req.method == 'POST':
            result = deleteDevice(req, id)
            viewDevice(req, resp, errors=result)


@nfw.app.resources()
class Themes(object):

    def __init__(self, app):
        self.css = app.context['css']
        self.css['.netrino-form'] = {}
        self.css['.netrino-form']['max-width'] = '530px'
        self.css['.netrino-form']['margin'] = '0 auto'
        self.css['.netrino-form']['padding'] = '15px'
        app.context['css'] = self.css
