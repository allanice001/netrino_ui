from __future__ import print_function
import nfw
import re
import sys
import json
from pyipcalc import *
from jinja2 import Template
from collections import OrderedDict
from tachyon.common import RestClient
from tachyon.ui import view, edit, create, datatable
from netrino.ui import model


def getFields(snippet, activate_snippet, deactivate_snippet):
    fields = re.findall('{{ ?(.*?) ?}}', snippet)
    if activate_snippet:
        afields = re.findall('{{ ?(.*?) ?}}', activate_snippet)
    else:
        afields = None
    if deactivate_snippet:
        dfields = re.findall('{{ ?(.*?) ?}}', deactivate_snippet)
    else:
        dfields = None
    if not fields:
        fields = []
    if afields:
        fields.extend(afields)
    if dfields:
        fields.extend(dfields)
    if fields:
        fields = ','.join(list(set(fields)))
    else:
        fields = None
    return fields


def viewIGroup(req, resp, id=None):
    if id:
        api = RestClient(req.context['restapi'])
        headers, response = api.execute(
            nfw.HTTP_GET, "/infrastructure/network/igroups/%s" % (id,))
        form = model.IGroup(response, validate=False, readonly=True)
        view(req, resp, content=form, id=id, title='View Interface Group')
    else:
        title = 'Interface Groups'
        fields = OrderedDict()
        fields['name'] = 'Interface Group Name'
        dt = datatable(
            req, 'igroups', '/infrastructure/network/igroups?view=datatable', fields, view_button=True)
        view(req, resp, content=dt, title=title)


def editIGroup(req, resp, id):
    if req.method == nfw.HTTP_POST:
        form = model.IGroup(req.post, validate=True, readonly=True)
        api = RestClient(req.context['restapi'])
        headers, response = api.execute(nfw.HTTP_PUT, "/infrastructure/network/igroups/%s" %
                                        (id,), form)
    else:
        api = RestClient(req.context['restapi'])
        headers, response = api.execute(
            nfw.HTTP_GET, "/infrastructure/network/igroups/%s" % (id,))
        form = model.IGroup(response, validate=False)
        edit(req, resp, content=form, id=id, title='Edit Interface Group')


def createIGroup(req, resp):
    if req.method == nfw.HTTP_POST:
        try:
            form = model.IGroup(req.post, validate=True)
            api = RestClient(req.context['restapi'])
            headers, response = api.execute(
                nfw.HTTP_POST, "/infrastructure/network/igroups", form)
            if 'id' in response:
                id = response['id']
                viewIGroup(req, resp, id=id)
        except nfw.HTTPBadRequest as e:
            form = model.User(req, validate=False)
            create(req, resp, content=form, title='Create User', error=[e])
    else:
        form = model.IGroup(req.post, validate=False)
        create(req, resp, content=form, title='Create Interface Group')


def deleteIGroup(req, resp, id):
    try:
        api = RestClient(req.context['restapi'])
        headers, response = api.execute(
            nfw.HTTP_DELETE, "/infrastructure/network/igroups/%s" % (id,))
        viewIGroup(req, resp)
    except nfw.HTTPBadRequest as e:
        edit(req, resp, content=form, id=id, title='Edit Interface Group')


def viewService(req, resp, id=None):
    return_format = req.headers.get('X-Format')
    if id:
        api = RestClient(req.context['restapi'])
        headers, service = api.execute(
            nfw.HTTP_GET, "/infrastructure/network/services/%s" % (id,))
        if return_format == "fields":
            fields = service['fields'].split(',')
            return json.dumps(fields, indent=4)
        templateFile = 'netrino.ui/service/createservice.html'
        t = nfw.jinja.get_template(templateFile)
        renderValues = {}
        renderValues['view'] = 'view'
        renderValues['serviceID'] = id
        renderValues['serviceName'] = service['name']
        renderValues['interfaceGroup'] = service['interface_group']
        renderValues['userRole'] = service['user_role']
        renderValues['snippet'] = service['config_snippet']
        renderValues['activate'] = service['activate_snippet']
        renderValues['deactivate'] = service['deactivate_snippet']
        form = t.render(**renderValues)
        title = service['name']
        view(req, resp, id=id, content=form, title=title)
    else:
        if return_format == "select2":
            api = RestClient(req.context['restapi'])
            headers, response = api.execute(
                nfw.HTTP_GET, "/infrastructure/network/services?view=datatable")
            result = []
            for r in response:
                result.append({'id': r['id'], 'text': r['name']})
            return json.dumps(result, indent=4)
        else:
            title = 'Network Services'
            fields = OrderedDict()
            fields['name'] = 'Service Name'
            # TODO:
            fields['user_role'] = 'Roles'
            fields['interface_group'] = 'Interface Group'
            dt = datatable(
                req, 'services', '/infrastructure/network/services?view=datatable', fields, view_button=True)
            view(req, resp, content=dt, title=title)


def editService(req, resp, id, **kwargs):
    if req.method == nfw.HTTP_POST:
        try:
            api = RestClient(req.context['restapi'])
            values = req.post
            snippet = values.get('config_snippet', '')
            activate_snippet = values.get('activate_snippet', None)
            deactivate_snippet = values.get('deactivate_snippet', None)
            fields = getFields(snippet, activate_snippet, deactivate_snippet)
            form = model.NetworkService(req.post, validate=True)
            form['fields'] = fields
            headers, response = api.execute(
                nfw.HTTP_PUT, "/infrastructure/network/services/%s" % (id,), form)
            if 'id' in response:
                id = response['id']
                viewService(req, resp, id=id)
        except nfw.HTTPBadRequest as e:
            req.method = nfw.HTTP_GET
            editService(req, resp, error=[e])
    else:
        api = RestClient(req.context['restapi'])
        headers, service = api.execute(
            nfw.HTTP_GET, "/infrastructure/network/services/%s" % (id,))
        templateFile = 'netrino.ui/service/createservice.html'
        t = nfw.jinja.get_template(templateFile)
        renderValues = {}
        renderValues['serviceID'] = id
        renderValues['serviceName'] = service['name']
        renderValues['interfaceGroup'] = service['interface_group']
        renderValues['userRole'] = service['user_role']
        renderValues['snippet'] = service['config_snippet']
        renderValues['activate'] = service['activate_snippet']
        renderValues['deactivate'] = service['deactivate_snippet']
        form = t.render(**renderValues)
        title = service['name']
        edit(req, resp, id=id, content=form, title=title, **kwargs)


def createService(req, resp, **kwargs):
    if req.method == nfw.HTTP_POST:
        try:
            api = RestClient(req.context['restapi'])
            values = req.post
            snippet = values.get('config_snippet', '')
            activate_snippet = values.get('activate_snippet', None)
            deactivate_snippet = values.get('deactivate_snippet', None)
            fields = getFields(snippet, activate_snippet, deactivate_snippet)
            form = model.NetworkService(req.post, validate=True)
            form['fields'] = fields
            headers, response = api.execute(
                nfw.HTTP_POST, "/infrastructure/network/services", form)
            if 'id' in response:
                id = response['id']
                viewService(req, resp, id=id)
        except nfw.HTTPBadRequest as e:
            req.method = nfw.HTTP_GET
            createService(req, resp, error=[e])
    else:
        renderValues = {}
        if req.post.get('name'):
            renderValues['serviceName'] = req.post.get('name')
            renderValues['interfaceGroup'] = req.post.get('interface_group')
            renderValues['userRole'] = req.post.get('user_role')
            renderValues['snippet'] = req.post.get('config_snippet')
            renderValues['activate'] = req.post.get('activate_snippet')
            renderValues['deactivate'] = req.post.get('deactivate_snippet')
        templateFile = 'netrino.ui/service/createservice.html'
        t = nfw.jinja.get_template(templateFile)
        form = t.render(**renderValues)
        title = 'Create a Network Service'
        create(req, resp, content=form,
               title='Create Network Service', **kwargs)


def deleteService(req, resp, id):
    try:
        api = RestClient(req.context['restapi'])
        headers, response = api.execute(
            nfw.HTTP_DELETE, "/infrastructure/network/services/%s" % (id,))
        viewService(req, resp)
    except Exception, e:  # hierdie gebeur nie met api.execute nie
        editService(req, resp, id, error=[e])


def viewDevice(req, resp, id=None, **kwargs):
    renderValues = {}
    renderValues['resource'] = 'Device'
    renderValues['window'] = '#window_content'
    fields = OrderedDict()
    if id:
        templateFile = 'netrino.ui/device/view.html'
        fields['port'] = 'Interface'
        #fields['customername'] = 'Customer'
        #fields['service'] = 'Service'
        fields['alias'] = 'IP'
        fields['prefix_len'] = 'Prefix Length'
        fields['descr'] = 'Description'
        fields['mac'] = 'Mac'
        fields['igroupname'] = 'Interface Group'
        fields['present'] = 'Present'
        fields['customername'] = 'Customer'
        fields['service'] = 'Service'
        apiurl = "/infrastructure/network/devices/" + id + "/ports"
        dt = datatable(req, 'devices', apiurl, fields)
        edit_url = "/ui/infrastructure/network/device/edit/" + id
        back_url = "/ui/infrastructure/network/device/"
        api = RestClient(req.context['restapi'])
        response_headers, device = api.execute(
            nfw.HTTP_GET, "/infrastructure/network/devices/" + id)
        renderValues['title'] = device['name']
        description = '<form action="../add/'
        description += id
        description += '" method="post">'
        description += 'As discovered on '
        description += str(device['last_discover'])
        description += '''. <button name="refreshdevice">Refresh</button>
                </form>'''
        renderValues['description'] = description
        response_headers, igroups = api.execute(
            nfw.HTTP_GET, "/infrastructure/network/igroups")  # This must be done by browser rather
        renderValues['igroups'] = igroups
        renderValues['device_id'] = id
        renderValues['edit_url'] = edit_url
        renderValues['back_url'] = back_url
        renderValues['window'] = '#window_content'
        renderValues['back'] = True
        renderValues['description'] = description
        renderValues['create_url'] = ''
        dt += ('<button class="btn btn-primary" ' +
               'data-url="infrastructure/network/device/' +
               id + '/ports/igroup">' +
               'Assign Interface Groups</button>')
    else:
        return_format = req.headers.get('X-Format')
        if return_format == "select2":
            api = RestClient(req.context['restapi'])
            headers, response = api.execute(
                nfw.HTTP_GET, "/infrastructure/network/devices")
            result = []
            for r in response:
                result.append({'id': r['id'], 'text': r['name']})
            return json.dumps(result, indent=4)
        else:
            fields['name'] = 'Device Name'
            fields['os'] = 'OS'
            fields['os_ver'] = 'OS Version'
            fields['last_discover'] = 'Last Updated'
            dt = datatable(
                req, 'devices', '/infrastructure/network/devices?view=datatable',
                fields, view_button=True)
            renderValues['title'] = 'Network Devices'

    view(req, resp, content=dt, **renderValues)


def portsIGroup(req, resp, id, **kwargs):
    back_url = 'infrastructure/network/devices/" + id + "/ports"'
    fields = OrderedDict()
    fields['port'] = 'Interface'
    fields['igroupname'] = 'Interface Group'
    apiurl = "/infrastructure/network/devices/" + id + "/ports"
    dt = datatable(req, 'devices', apiurl, fields, view_button=True)
    back_url = "/ui/infrastructure/network/device/view/%s" % (id,)
    renderValues = {}
    renderValues['back_url'] = back_url
    renderValues['window'] = '#window_content'
    renderValues['dt'] = dt
    templateFile = 'netrino.ui/device/portigroup.html'
    t = nfw.jinja.get_template(templateFile)
    content = t.render(**renderValues)
    view(req, resp, content=content, **renderValues)


def createDevice(req, resp):
    title = 'Add a Network Device (or Devices)'
    renderValues = {'title': title}
    renderValues['back_url'] = 'infrastructure/network/device'
    renderValues['window'] = '#window_content'
    renderValues['submit_url'] = 'infrastructure/network/device/create'
    renderValues['formid'] = 'device'
    renderValues['resource'] = 'Device'

    templateFile = 'netrino.ui/device/create.html'
    t = nfw.jinja.get_template(templateFile)
    form = t.render(**renderValues)

    create(req, resp, content=form, **renderValues)


def editDevice(req, resp, id):
    title = 'Update Device'
    renderValues = {'title': title}
    renderValues['window'] = '#window_content'

    api = RestClient(req.context['restapi'])
    response_headers, device = api.execute(
        nfw.HTTP_GET, "/infrastructure/network/devices/" + id)
    if device['id']:
        renderValues['device_ip'] = dec2ip(int(id), 4)
        renderValues['id'] = id
        renderValues['commstring'] = device['snmp_comm']
        renderValues['title'] = "Refresh " + device['name']
        renderValues[
            'back_url'] = 'infrastructure/network/device/view/' + id
        renderValues[
            'submit_url'] = 'infrastructure/network/device/edit/' + id
        renderValues[
            'delete_url'] = 'infrastructure/network/device/delete/' + id
        renderValues['formid'] = 'device'
        renderValues['resource'] = 'Device'
    else:
        raise nfw.HTTPBadRequest("Device not found")  # Device not found

    templateFile = 'netrino.ui/device/create.html'
    t = nfw.jinja.get_template(templateFile)
    form = t.render(**renderValues)

    edit(req, resp, content=form, **renderValues)


def createDevicePost(req, resp):
    api = RestClient(req.context['restapi'])
    values = req.post
    subnet = values.get('device_ip')
    data = {'snmp_comm': values.get('snmp_community')}
    issubnet = re.search('/', subnet)
    if not issubnet:
        subnet += "/32"
        try:
            subnet = IPNetwork(subnet)
        except e:
            raise(nfw.Error(e))
    results = []
    for ip in subnet:
        ver = ip._version
        ip = ip.ip_network
        data['id'] = ip2dec(ip, 4)
        response_headers, result = api.execute(
            nfw.HTTP_POST, "/infrastructure/network/devices", obj=data)
        results.append(result)
    return results

#
# To Handle the POST of edit device:
# Nog besig met die
#


def updateDevice(req, device_id):
    id = device_id
    api = RestClient(req.context['restapi'])
    response_headers, device = api.execute(
        nfw.HTTP_PUT, "/infrastructure/network/devices/" + id)


def confirmRMdevice(req, resp, id):
    api = RestClient(req.context['restapi'])
    response_headers, device = api.execute(
        nfw.HTTP_GET, "/infrastructure/network/devices/" + device_id)
    if not id in device:
        raise nfw.HTTPBadRequest("Device not found: %s" % device_id)
    request_headers = {}
    request_headers['X-Search-Specific'] = 'device=' + \
        device_id + ',status=ACTIVE'
    response_headers, result = api.execute(
        nfw.HTTP_GET, "/infrastructure/network/service_requests/", headers=request_headers)
    num_serv = len(result)
    templateFile = 'netrino.ui/device/rmdevice.html'
    renderValues = {'title': "Remove " + device[device_id]['name']}
    if num_serv > 0:
        warn = (dec2ip(int(device_id), 4), str(num_serv))
        renderValues['warn'] = warn
    renderValues['device_id'] = device_id
    t = nfw.jinja.get_template(templateFile)
    form = t.render(**renderValues)
    edit(req, resp, content=form, id=id, **renderValues)


def deleteDevice(req, device_id):
    api = RestClient(req.context['restapi'])
    response_headers, result = api.execute(
        nfw.HTTP_DELETE, "/infrastructure/network/devices/" + device_id)
    return result


def getPorts(req, id):
    api = RestClient(req.context['restapi'])
    response_headers, response = api.execute(
        nfw.HTTP_GET, "/infrastructure/network/devices/%s/ports" % (id,))
    return_format = req.headers.get('X-Format')
    if return_format == "select2":
        result = []
        for r in response:
            result.append({'id': r['port'], 'text': r['port']})
        return json.dumps(result, indent=4)
    else:
        return json.dumps(response, indent=4)


def createSR(req, resp, **kwargs):
    if req.method == nfw.HTTP_POST:
        api = RestClient(req.context['restapi'])
        values = req.post
        postValues = {}
        for value in values:
            if value == 'device':
                devices = values.get(value)
                deviceIDs = devices.split(',')
            else:
                postValues[value] = values.get(value)

        for device in deviceIDs:
            postValues['device'] = int(device)
            headers, response = api.execute(
                nfw.HTTP_POST, "/infrastructure/network/service_requests", obj=postValues)
        viewSR(req, resp)
    else:
        title = 'Create a service request'
        renderValues = {'title': title}
        renderValues['window'] = '#window_content'
        renderValues['submit_url'] = 'infrastructure/network/sr/create'
        renderValues['back_url'] = 'infrastructure/network/sr'
        renderValues['formid'] = 'service_request'
        renderValues['app'] = req.get_app()
        templateFile = 'netrino.ui/service_requests/create.html'
        t = nfw.jinja.get_template(templateFile)
        form = t.render(**renderValues)

        create(req, resp, content=form, **renderValues)


def viewSR(req, resp, id=None, **kwargs):
    renderValues = {}
    renderValues['window'] = '#window_content'
    if id:
        api = RestClient(req.context['restapi'])
        headers, response = api.execute(
            nfw.HTTP_GET, "/infrastructure/network/service_requests/%s" % (id,))
        templateFile = 'netrino.ui/service_requests/view.html'
        t = nfw.jinja.get_template(templateFile)
        response = response[0]
        renderValues = response
        if response['status'] in ["SUCCESS", "INACTIVE", "UNKNOWN"]:
            activate_url = ("infrastructure/network/sr/" +
                            "edit/" + id + "/activate")
            renderValues['activate_url'] = activate_url
        elif response['status'] == "ACTIVE":
            deactivate_url = ("infrastructure/network/sr/" +
                              "edit/" + id + "/deactivate")
            renderValues['deactivate_url'] = deactivate_url
        back_url = "infrastructure/network/service_requests/"
        renderValues['back_url'] = back_url
        renderValues['title'] = "View Service Request"
        content = t.render(**renderValues)
        log.debug("MYDEBUG: %s" % (str(renderValues),))
        view(req, resp, content=content, **renderValues)
    else:
        fields = OrderedDict()
        fields['creation_date'] = 'Creation Date'
        fields['customer'] = 'Customer'
        fields['device'] = 'Device'
        fields['service'] = 'Service'
        fields['status'] = 'Status'
        content = datatable(
            req, 'service_requests', '/infrastructure/network/service_requests',
            fields, view_button=True)
        renderValues['title'] = "Service Requests"

    view(req, resp, content=content, **renderValues)


def activateSR(req, resp, id=id):
    api = RestClient(req.context['restapi'])
    headers, response = api.execute(
        nfw.HTTP_PUT, "/infrastructure/network/service_requests/%s" % (id,))
    viewSR(req, resp, id=id)


def deactivateSR(req, resp, id=id):
    api = RestClient(req.context['restapi'])
    headers, response = api.execute(
        nfw.HTTP_DELETE, "/infrastructure/network/service_requests/%s" % (id,))
    viewSR(req, resp, id=id)
