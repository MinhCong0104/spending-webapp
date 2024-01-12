from rpc_inherit import OdooXmlrpc


class MigrateModel:
    def __init__(self):
        self.source = None
        self.target = None
        self.model = None
        self.sync_fields = []
        self.from_id = 1
        self.active = True
        self.create_gap = True
        self.patch = 1000
        self.field_mapping = {}
        self.default_vals = {}
        self.have_parent = False

    def _read_source(self):
        if self.active:
            datas = self.source.search_read(
                [('id', '>=', self.from_id), '|', ('active', '=', True), ('active', '=', False)],
                order='id asc', fields=self.sync_fields, load=''
            )
        else:
            datas = self.source.search_read([('id', '>=', self.from_id)], order='id asc',
                                            fields=self.sync_fields, load='')
        print("Total %s record: %s" % (self.model, len(datas)))
        return datas

    def _read_old(self):
        if self.active:
            datas = self.source.search_read(
                [('id', '<', self.from_id), '|', ('active', '=', True), ('active', '=', False)],
                order='id asc', fields=self.sync_fields, load=''
            )
        else:
            datas = self.source.search_read([('id', '<', self.from_id)], order='id asc',
                                            fields=self.sync_fields, load='')
        print("Total %s record: %s" % (self.model, len(datas)))
        return datas

    def _process_datas(self):
        datas = self._read_source()
        new_datas = []
        to_delete = []
        previous_id = self.from_id - 1

        for data in datas:
            if data['id'] > previous_id + 1:
                for i in range(previous_id + 1, data['id']):
                    new_datas.append(dict(self.default_vals, **{'name': 'Record %s' % i}))
                    to_delete.append(i)

            previous_id = data.pop('id')
            new_datas.append(data)
        return [new_datas, to_delete]

    def _create_datas(self):
        new_datas = self._process_datas()[0]
        for i in range(0, len(new_datas), self.patch):
            print("Creating %s records from %s to %s" % (self.model, i, i + self.patch))
            self.target.create(new_datas[i:i + self.patch])

    def _delete_gap(self):
        gap_ids = self._process_datas()[1]
        print("Deleting gap records")
        self.target.browse(gap_ids).unlink()

