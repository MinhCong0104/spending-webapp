import datetime
from mongoengine import Document, StringField, ReferenceField, DateTimeField


class Account(Document):
    name = StringField(required=True)
    account_type = StringField(required=True)
    root_type = StringField(required=True)
    created_at = DateTimeField(required=True)
    updated_at = DateTimeField(required=False)

    client = ReferenceField("Client", required=True)
    user = ReferenceField("User", required=True)

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.datetime.utcnow()
        self.updated_at = datetime.datetime.utcnow()
        return super(Account, self).save(*args, **kwargs)

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
        "collection": "Accounts",
        "indexes": ["client", "user", "account_type", "root_type"],
        "allow_inheritance": True,
        "index_cls": False,
    }
