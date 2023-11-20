import datetime
from mongoengine import Document, StringField, ReferenceField, DateTimeField


class Address(Document):
    name = StringField(required=True)
    address = StringField(required=True)
    address_type = StringField(required=True)
    created_at = DateTimeField(required=True)
    updated_at = DateTimeField(required=False)

    client = ReferenceField("Client", required=True)

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.datetime.utcnow()
        self.updated_at = datetime.datetime.utcnow()
        return super(Address, self).save(*args, **kwargs)

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
        "collection": "Addresses",
        "indexes": ["client", "address_type"],
        "allow_inheritance": True,
        "index_cls": False,
    }
