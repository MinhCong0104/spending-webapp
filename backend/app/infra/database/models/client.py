import datetime
from mongoengine import (
    Document,
    StringField,
    EmailField,
    DateTimeField,
    BooleanField,
    ReferenceField,
)


class Client(Document):
    email = EmailField(unique=True, required=True)
    fullname = StringField(required=True)
    company_name = StringField()
    country = StringField(default="SG")
    currency = StringField(default="USD")

    is_active = BooleanField(default=False)
    is_setup_complete = BooleanField(default=False)
    fiscal_year_start = DateTimeField()
    fiscal_year_end = DateTimeField()

    created_at = DateTimeField(required=True)
    updated_at = DateTimeField(required=False)

    owner = ReferenceField("User", required=True)

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.datetime.utcnow()
        self.updated_at = datetime.datetime.utcnow()
        return super(Client, self).save(*args, **kwargs)

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
        "collection": "Clients",
        "indexes": ["email", "owner"],
        "allow_inheritance": True,
        "index_cls": False,
    }
