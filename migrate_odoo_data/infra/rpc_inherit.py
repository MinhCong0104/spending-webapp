# -*- coding: utf-8 -*-

from xmlrpc.client import Unmarshaller, ResponseError, ExpatParser, Transport, SafeTransport, ServerProxy
from odoorpc import error, tools, ODOO
from odoorpc.env import Environment
from odoorpc.db import DB
from odoorpc.report import Report


# Inherit xmlrpc class and method to use error.RPCError from odoo-rpc
def getparser(use_datetime=False, use_builtin_types=False):
    target = UnmarshallerInherit(use_datetime=use_datetime, use_builtin_types=use_builtin_types)
    parser = ExpatParser(target)
    return parser, target


class UnmarshallerInherit(Unmarshaller):
    # the function that raise error
    def close(self):
        if self._type is None or self._marks:
            raise ResponseError()
        if self._type == "fault":
            raise error.RPCError(self._stack[0]['faultString'])
        return tuple(self._stack)


class TransportInherit(Transport):
    def getparser(self):
        return getparser(use_datetime=self._use_datetime,
                         use_builtin_types=self._use_builtin_types)


class SafeTransportInherit(SafeTransport):
    def getparser(self):
        return getparser(use_datetime=self._use_datetime,
                         use_builtin_types=self._use_builtin_types)


# Inherit odoo-rpc class to call Serverproxy from xmlrpc
class xmlrpcDB(DB):
    # inherit to get list function, other function will raise AttributeError from OdooXmlrpc json function.
    def __init__(self, odoo):
        super().__init__(odoo)
        self._db_connector = ServerProxy('{}/xmlrpc/2/db'.format(odoo.host))

    def list(self):
        return self._db_connector.list()


class OdooXmlrpc(ODOO):

    def __init__(self, host='localhost', use_datetime=False, use_builtin_types=False, context=None):
        self._host = host
        self._env = None
        self._login = None
        self._password = None
        self._db = xmlrpcDB(self)
        self._report = Report(self)
        # this part is for error handling
        (handler, extra_kwargs) = (SafeTransportInherit, {"context": context}) if 'https' in host else (TransportInherit, {})
        transport = handler(use_datetime=use_datetime,
                            use_builtin_types=use_builtin_types,
                            **extra_kwargs)
        # end of error handling
        self._connector = ServerProxy('{}/xmlrpc/2/common'.format(host), transport=transport)  # use to log in
        self._object = ServerProxy('{}/xmlrpc/2/object'.format(host), transport=transport)  # use to execute function
        # Dictionary of configuration options
        self._config = tools.Config(
            self,
            {'auto_commit': True,
             'auto_context': True,
             'timeout': 120})

    def json(self, url, params):
        raise AttributeError('Trying to call json function in xml rpc connection.')

    def http(self, url, data=None, headers=None):
        raise NotImplementedError('Not implemented for xmlrpc.')

    def login(self, db, login='admin', password='admin'):
        # xmlprc equivalent:
        # common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        # uid = common.authenticate(db, user_name, password, {})
        uid = self._connector.authenticate(db, login, password, {})
        if uid:
            context = {}  # Todo: try to get user context from xml rpc
            self._env = Environment(self, db, uid, context=context)
            self._login = login
            self._password = password
        else:
            raise error.RPCError("Wrong login ID or password")

    def logout(self):
        raise NotImplementedError('Not implemented for xmlrpc.')

    def execute(self, model, method, *args):
        # xmlrpc equivalent:
        # models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        # res = models.execute(db, uid, password, model, method, args)
        self._check_logged_user()
        args_to_send = [self.env.db, self.env.uid, self._password,
                        model, method]
        args_to_send.extend(args)
        data = self._object.execute(*args_to_send)
        return data

    def execute_kw(self, model, method, args=None, kwargs=None):
        # xmlrpc equivalent:
        # models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        # res = models.execute_kw(db, uid, password, model, method, args, kwargs)
        self._check_logged_user()
        args = args or []
        kwargs = kwargs or {}
        args_to_send = [self.env.db, self.env.uid, self._password,
                        model, method]
        args_to_send.extend([args, kwargs])
        data = self._object.execute_kw(*args_to_send)
        return data

    def exec_workflow(self, model, record_id, signal):
        pass  # Depreciated after v11.

    def save(self, name, rc_file='~/.odoorpcrc'):
        raise NotImplementedError('Not implemented for xmlrpc.')

    @classmethod
    def load(cls, name, rc_file='~/.odoorpcrc'):
        raise NotImplementedError('Not implemented for xmlrpc.')

    @classmethod
    def list(cls, rc_file='~/.odoorpcrc'):
        raise NotImplementedError('Not implemented for xmlrpc.')

    @classmethod
    def remove(cls, name, rc_file='~/.odoorpcrc'):
        raise NotImplementedError('Not implemented for xmlrpc.')

