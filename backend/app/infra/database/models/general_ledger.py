import datetime
from mongoengine import Document, StringField, DateTimeField, ReferenceField, BooleanField, DecimalField


class GeneralLedger(Document):
    name = StringField(required=True)
    date = DateTimeField(required=True)
    account = ReferenceField("Account", required=True)
    debit = DecimalField(required=True, default=0.0)
    credit = DecimalField(required=True, default=0.0)

    reference_name = StringField(required=True)
    reference_type = StringField(required=True)

    reverted = BooleanField(default=False)

    created_at = DateTimeField(required=True)
    updated_at = DateTimeField(required=False)

    journal = ReferenceField("Journal", required=True)
    client = ReferenceField("Client", required=True)
    user = ReferenceField("User", required=True)

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.datetime.utcnow()
        self.updated_at = datetime.datetime.utcnow()
        return super(GeneralLedger, self).save(*args, **kwargs)

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
        "collection": "GeneralLedgers",
        "indexes": ["name", "date", "account", "user", "client", "journal"],
        "allow_inheritance": True,
        "index_cls": False,
    }
