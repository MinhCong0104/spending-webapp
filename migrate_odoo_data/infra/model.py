from rpc_inherit import OdooXmlrpc


class MigrateModel:
    def __init__(self, source, target, model, sync_fields, from_id=1, have_active_field=True, create_gap=True,
                 patch=1000, field_mapping=None, default_vals=None, have_parent=False, create_mapping_file=False):
        self.source = source
        self.target = target
        # self.model = model
        # self.sync_fields = sync_fields
        # self.from_id = from_id
        # self.have_active_field = have_active_field
        # self.create_gap = create_gap
        # self.patch = patch
        # self.field_mapping = field_mapping
        # self.default_vals = default_vals
        # self.have_parent = have_parent
        # self.create_mapping_file = create_mapping_file

    def search(self, model, from_id=1, domain=False, can_archive=True):
        """
        Function to search records created in source DB.
        :param model: str name of model
        :param from_id: search record from id
        :param can_archive: bool - True if model have active fields and False if not
        :param domain: if input domain, search by this domain and ignore from_id, can_archive
        :return: list id -> []
        """

        if domain:
            return self.source.env[model].search(domain,  order='id asc')

        if can_archive:
            return self.source.env[model].search(
                [('id', '>=', from_id), '|', ('active', '=', True), ('active', '=', False)],
                order='id asc'
            )

        return self.source.env[model].search([('id', '>=', from_id)], order='id asc')

    def read(self, model, fields, from_id=1, domain=False, can_archive=True):
        """
        Function to read records created in source DB.
        :param model: str name of model
        :param from_id: search record from id
        :param can_archive: bool - True if model have active fields and False if not
        :param domain: if input domain, search by this domain and ignore from_id, can_archive
        :param fields: fields to read data
        :return: list data -> [{}]
        """

        if domain:
            return self.source.env[model].search_read(domain, fields, order='id asc', load='')

        if can_archive:
            return self.source.env[model].search_read(
                [('id', '>=', from_id), '|', ('active', '=', True), ('active', '=', False)],
                fields, order='id asc', load=''
            )

        return self.source.env[model].search_read([('id', '>=', from_id)], fields, order='id asc', load='')

    def search_default(self, model, from_id, domain=False, can_archive=True):
        """
        Function to search records default in source DB.
        :param model: str name of model
        :param from_id: search record from id
        :param can_archive: bool - True if model have active fields and False if not
        :param domain: if input domain, search by this domain and ignore from_id, can_archive
        :return: list id -> []
        """

        if domain:
            return self.source.env[model].search(domain,  order='id asc')

        if can_archive:
            return self.source.env[model].search(
                [('id', '<', from_id), '|', ('active', '=', True), ('active', '=', False)],
                order='id asc'
            )

        return self.source.env[model].search([('id', '<', from_id)], order='id asc')

    def read_default(self, model, fields, from_id=1, domain=False, can_archive=True):
        """
        Function to read records default in source DB.
        :param model: str name of model
        :param from_id: search record from id
        :param can_archive: bool - True if model have active fields and False if not
        :param domain: if input domain, search by this domain and ignore from_id, can_archive
        :param fields: fields to read data
        :return: list data -> [{}]
        """

        if domain:
            return self.source.env[model].search_read(domain, fields, order='id asc', load='')

        if can_archive:
            return self.source.env[model].search_read(
                [('id', '<', from_id), '|', ('active', '=', True), ('active', '=', False)],
                fields, order='id asc', load=''
            )

        return self.source.env[model].search_read([('id', '<', from_id)], fields, order='id asc', load='')

    def _process_datas(self, create_gap, datas, from_id=1, default_vals={}):
        # TODO: Cần thêm tình huống xử lý lệch id các trường related

        """
        Function to search records in source DB.
        :param create_gap:
        :param from_id:
        :param default_vals:
        :return: list data -> [{}]
        """

        if not create_gap:
            return datas, []

        new_datas = []
        to_delete = []
        previous_id = from_id - 1

        for data in datas:
            if data['id'] > previous_id + 1:
                for i in range(previous_id + 1, data['id']):
                    new_datas.append(dict(default_vals, **{'name': 'Record %s' % i}))
                    to_delete.append(i)

            previous_id = data.pop('id')
            new_datas.append(data)
        return new_datas, to_delete

    def write(self, datas):
        """
        Function to write value to the match id record in target DB.
        :param datas:
        :return: not return
        """

        for data in datas:
            self.target.browse(data['id']).write(data)

    def create(self, datas, create_mapping_file=False):
        """
        Function to create new record and delete gap in target DB.
        :return: not return
        """

        if create_mapping_file:
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
