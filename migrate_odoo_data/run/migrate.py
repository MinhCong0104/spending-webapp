# -*- coding: utf-8 -*-

import xmlrpc.client
from migrate_partner import run_migrate_partner

from rpc_inherit import OdooXmlrpc


# From
source = OdooXmlrpc('https://demo-odoo16.bachasoftware.com/')
source.login('DEMO_ERP_1101', 'congtm.bhsoft@gmail.com', 'Mc010401')

# To
target = OdooXmlrpc('http://127.0.0.1:1717')
target.login('CORE', 'thanhbt1.bhsoft@gmail.com', '1')

# run_migrate_partner(source, target)
