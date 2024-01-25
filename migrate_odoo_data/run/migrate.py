# -*- coding: utf-8 -*-

import xmlrpc.client
from migrate_odoo_data.infra.model import MigrateModel
from migrate_odoo_data.infra.rpc_inherit import OdooXmlrpc


# From
source = OdooXmlrpc('https://demo-odoo16.bachasoftware.com/')
source.login('DEMO_ERP_1101', 'congtm.bhsoft@gmail.com', 'Mc010401')

# To
target = OdooXmlrpc('http://127.0.0.1:1717')
target.login('CORE', 'thanhbt1.bhsoft@gmail.com', '1')


partner_field = ['active', 'name', 'image_1920', 'is_company', 'type', 'street', 'street2', 'city', 'state_id',
                 'zip', 'country_id', 'phone', 'mobile', 'email', 'vat', 'lang', 'website', 'invoice_currency',
                 'num_invoice', 'customer_code', 'customer_rank', 'status', 'parent_id']
migrate_partner = MigrateModel(source=source, target=target, model="res.partner", from_id=8, sync_fields=partner_field,
                               have_active_field=True, create_gap=True, patch=100, have_parent=True, default_vals=None,
                               field_mapping=None, create_mapping_file=False)
migrate_partner.create()
migrate_partner.write()

