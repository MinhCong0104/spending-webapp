import datetime
from mongoengine import Document, ReferenceField, DecimalField, DateTimeField, StringField


class JournalAccount(Document):
    name = StringField(required=True)
    account = ReferenceField("Account", required=True)
    debit = DecimalField(required=True, default=0)
    credit = DecimalField(required=True, default=0)

    created_at = DateTimeField(required=True)
    updated_at = DateTimeField(required=False)

    client = ReferenceField("Client", required=True)
    user = ReferenceField("User", required=True)
    journal = ReferenceField("Journal")

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.datetime.utcnow()
        self.updated_at = datetime.datetime.utcnow()
        return super(JournalAccount, self).save(*args, **kwargs)

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
        "collection": "JournalAccounts",
        "indexes": ["journal", "client", "user"],
        "allow_inheritance": True,
        "index_cls": False,
    }
