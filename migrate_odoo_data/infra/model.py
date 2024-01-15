from rpc_inherit import OdooXmlrpc


class MigrateModel:
    def __init__(self, source, target, model, sync_fields, from_id=1, have_active_field=True, create_gap=True,
                 patch=1000, field_mapping=None, default_vals=None, have_parent=False, create_mapping_file=False):
        self.source = source
        self.target = target
        self.model = model
        self.sync_fields = sync_fields
        self.from_id = from_id
        self.have_active_field = have_active_field
        self.create_gap = create_gap
        self.patch = patch
        self.field_mapping = field_mapping
        self.default_vals = default_vals
        self.have_parent = have_parent
        self.create_mapping_file = create_mapping_file

    def _source_ids(self):
        """
        Function to search records in source DB.
        :return: list id
        """

        if self.have_active_field:
            ids = self.source.search(
                [('id', '>=', self.from_id), '|', ('active', '=', True), ('active', '=', False)],
                order='id asc'
            )
        else:
            ids = self.source.search([('id', '>=', self.from_id)], order='id asc')
        print("Total %s record: %s" % (self.model, len(ids)))
        return ids

    def _source_datas(self):
        """
        Function to read data in source DB.
        :return: list data
        """

        if self.have_active_field:
            datas = self.source.search_read(
                [('id', '>=', self.from_id), '|', ('active', '=', True), ('active', '=', False)],
                order='id asc', fields=self.sync_fields, load=''
            )
        else:
            datas = self.source.search_read([('id', '>=', self.from_id)], order='id asc',
                                            fields=self.sync_fields, load='')
        print("Total %s record: %s" % (self.model, len(datas)))
        return datas

    def _old_ids(self):
        """
        Function to read default data created in target DB.
        :return: list data
        """

        if self.have_active_field:
            datas = self.source.search_read(
                [('id', '<', self.from_id), '|', ('active', '=', True), ('active', '=', False)],
                order='id asc', fields=self.sync_fields, load=''
            )
        else:
            datas = self.source.search_read([('id', '<', self.from_id)], order='id asc',
                                            fields=self.sync_fields, load='')
        print("Total %s record: %s" % (self.model, len(datas)))
        return datas

    def _old_data(self):
        """
        Function to read default data changed in source DB.
        :return: list data
        """

        if self.have_active_field:
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
        # TODO: Cần thêm tình huống xử lý lệch id các trường related

        """
        Function to process data before create in target DB.
        :return: list data to create, list id to delete
        """

        if not self.create_gap:
            return self._source_datas(), []

        datas = self._source_datas()
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
        return new_datas, to_delete

    def write(self):
        """
        Function to write value to the match id record in target DB.
        :return: not return
        """

        datas = self._old_data()
        for data in datas:
            self.target.browse(data['id']).write(data)

    def create(self):
        """
        Function to create new record and delete gap in target DB.
        :return: not return
        """

        if self.create_mapping_file:
            return

        new_datas = self._process_datas()[0]
        for i in range(0, len(new_datas), self.patch):
            print("Creating %s records from %s to %s" % (self.model, i, i + self.patch))
            self.target.create(new_datas[i:i + self.patch])

        gap_ids = self._process_datas()[1]
        if len(gap_ids) > 0:
            print("Deleting gap records")
            self.target.browse(gap_ids).unlink()

    def create_and_mapping(self):
        """
        Function to create new record in target DB and create file mapping.
        :return: not return
        """

        if not self.create_mapping_file:
            return

        source_ids = self._source_ids()
        new_datas = self._process_datas()[0]
        new_ids = self.target.create(new_datas)
        mapping_dict = dict(zip(source_ids, new_ids))

        file_name = self.model.replace(".", "_")
        with open(f'{file_name}.txt', 'w') as f:
            print(mapping_dict, file=f)
