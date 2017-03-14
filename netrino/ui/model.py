from __future__ import absolute_import
from __future__ import unicode_literals

import logging

import nfw

from netrino.common import model as common

log = logging.getLogger(__name__)


class IGroup(nfw.bootstrap3.Form, common.IGroup):
    pass

class NetworkService(nfw.bootstrap3.Form, common.NetworkService):
    pass