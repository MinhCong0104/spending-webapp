# -*- coding: utf-8 -*-
from datetime import datetime
from model import MigrateModel


def migrate_partner(o_source, o_target, from_id=8):

    sync_fields = ['active', 'name', 'image_1920', 'is_company', 'type', 'street', 'street2', 'city', 'state_id',
                   'zip', 'country_id', 'phone', 'mobile', 'email', 'vat', 'lang', 'website', 'invoice_currency',
                   'num_invoice', 'customer_code', 'customer_rank', 'status', 'parent_id']
    SourcePartner = o_source.env['res.partner']
    TargetPartner = o_target.env['res.partner'].with_context(tracking_disable=True)

    # Cập nhật thông tin partner 7
    print('Updating partner with id 7')
    partner7 = SourcePartner.search_read([('id', '=', 7)], fields=sync_fields)[0]
    TargetPartner.browse(7).write(partner7)

    partner_datas = SourcePartner.search_read(
        [('id', '>=', from_id), '|', ('active', '=', True), ('active', '=', False)],
        order='id asc', fields=sync_fields, load=''
    )
    print("Total partners: %s" % len(partner_datas))

    new_partner_datas = []
    to_delete = []
    parent_dict = {}
    previous_id = from_id - 1
    for partner_data in partner_datas:
        if partner_data['id'] > previous_id + 1:
            for i in range(previous_id + 1, partner_data['id']):
                new_partner_datas.append({'name': 'Partner %s' % i})
                to_delete.append(i)

        parent_id = partner_data.pop('parent_id')
        if parent_id:
            if not parent_dict.get(parent_id):
                parent_dict[parent_id] = [partner_data['id']]
            else:
                parent_dict[parent_id].append(partner_data['id'])

        if partner_data['type'] == "private":
            partner_data['type'] = "other"

        if partner_data['state_id'] and 1387 <= partner_data['state_id'] <= 1410:
            partner_data['state_id'] = partner_data['state_id'] + 16
        elif partner_data['state_id'] == 1411:
            partner_data['state_id'] = 1393

        currency_mapping = {21: 20, 1: 124, 25: 24, 37: 36, 2: 1, 23: 22}
        partner_data['invoice_currency'] = currency_mapping[partner_data['invoice_currency']] if partner_data['invoice_currency'] else False

        previous_id = partner_data.pop('id')
        new_partner_datas.append(partner_data)

    # create batch partner
    for i in range(0, len(new_partner_datas), 100):
        print("Creating partners from %s to %s" % (i, i + 100))
        TargetPartner.create(new_partner_datas[i:i + 100])
    print("Deleting gap partners")
    TargetPartner.browse(to_delete).unlink()

    # Cập nhật thông tin admin cũ
    print('Updating partner with id 3 - Admin')
    partner3 = SourcePartner.search_read([('id', '=', 3), ('active', '=', False)], fields=sync_fields)[0]
    partner3['active'] = True
    TargetPartner.browse(3).write(partner3)

    print('Updating parent_id of partners')
    for parent_id, partner_ids in parent_dict.items():
        TargetPartner.browse(partner_ids).write({'parent_id': parent_id})

    print("--------------------------------------------------")

def migrate_partner_category(o_source, o_target):

    SourceCategory = o_source.env['res.partner.category']
    TargetCategory = o_target.env['res.partner.category'].with_context(tracking_disable=True)

    sync_field = ['name', 'color', 'parent_id', 'child_ids', 'active', 'parent_path', 'partner_ids']

    category_datas = SourceCategory.search_read(['|', ('active', '=', True), ('active', '=', False)],
                                                order='id asc', fields=sync_field, load='')
    print("Total partner categories: %s" % len(category_datas))

    new_category_datas = []
    to_delete = []
    previous_id = 0
    for category_data in category_datas:
        if category_data['id'] > previous_id + 1:
            for i in range(previous_id + 1, category_data['id']):
                new_category_datas.append({'name': 'Category %s' % i})
                to_delete.append(i)

        previous_id = category_data.pop('id')
        new_category_datas.append(category_data)

    # create batch category
    print("Creating categories...")
    TargetCategory.create(new_category_datas)
    print("Deleting gap partners")
    TargetCategory.browse(to_delete).unlink()
    print("--------------------------------------------------")

def migrate_partner_title(o_source, o_target, from_id=6):

    SourceTitle = o_source.env['res.partner.title']
    TargetTitle = o_target.env['res.partner.title'].with_context(tracking_disable=True)

    title_datas = SourceTitle.search_read([('id', '>=', from_id)], order='id asc', fields=['name', 'shortcut'], load='')
    print("Total partner titles: %s" % len(title_datas))

    new_title_datas = []
    to_delete = []
    previous_id = from_id-1
    for title_data in title_datas:
        if title_data['id'] > previous_id + 1:
            for i in range(previous_id + 1, title_data['id']):
                new_title_datas.append({'name': 'Title %s' % i})
                to_delete.append(i)

        previous_id = title_data.pop('id')
        new_title_datas.append(title_data)

    # create batch title
    for i in range(0, len(new_title_datas), 1000):
        print("Creating partner titles from %s to %s" % (i, i + 1000))
        TargetTitle.create(new_title_datas[i:i + 1000])
    print("Deleting gap partners title")
    TargetTitle.browse(to_delete).unlink()
    print("--------------------------------------------------")

def run_migrate_partner(o_source, o_target):
    migration_start = datetime.now()
    print(f'Start migrating partner at {migration_start}')

    migrate_partner(o_source, o_target)
    migrate_partner_category(o_source, o_target)
    migrate_partner_title(o_source, o_target)

    print(f'End migrating partner, total time: {datetime.now() - migration_start}')
    print("=" * 100)
