import datetime
from mongoengine import Document, StringField, DateTimeField, FloatField, ReferenceField, IntField


class Transaction(Document):
    entry_no = StringField(required=False)
    status = StringField(required=True)
    timestamp = DateTimeField(required=True)
    source = StringField()
    source_type = StringField()
    source_identifier = StringField()
    type = StringField()
    tags = StringField()
    function = StringField()
    product = StringField()

    classification = StringField()
    classification_id = StringField()
    behaviour = StringField()

    amount = FloatField()
    asset = StringField()
    fee = FloatField()
    fee_type = StringField()
    cost_basis = FloatField()
    cost_currency = StringField()
    sale_value = FloatField()
    sale_currency = StringField()
    fee_value = FloatField()
    fee_currency = StringField()
    unit_price = FloatField()
    unit_currency = StringField()

    trade_id = StringField()
    memo = StringField()

    contract_name = StringField()
    contract_id = StringField()
    smart_contract = StringField()

    tx_hash = StringField()
    from_wallet_name = StringField()
    from_wallet = StringField(required=True)
    to_wallet_name = StringField()
    to_wallet = StringField(required=True)
    ledger_id = IntField()
    label = StringField()
    description = StringField()

    created_at = DateTimeField(required=True)
    updated_at = DateTimeField(required=False)

    client = ReferenceField("Client", required=False)
    number_series = ReferenceField("NumberSeries", required=False)

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.datetime.utcnow()
        self.updated_at = datetime.datetime.utcnow()
        return super(Transaction, self).save(*args, **kwargs)

    @classmethod
    def from_mongo(cls, data: dict, id_str=False):
        """We must convert _id into "id". """
        if not data:
            return data
        id = data.pop("_id", None) if not id_str else str(data.pop("_id", None))
        if "_cls" in data:
            data.pop("_cls", None)
        return cls(**dict(data, id=id))

    meta = {
        "collection": "Transactions",
        "indexes": ["entry_no", "timestamp", "from_wallet", "to_wallet", "client"],
        "allow_inheritance": True,
        "index_cls": False,
    }
