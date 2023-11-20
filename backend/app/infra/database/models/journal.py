import datetime
from mongoengine import Document, StringField, ReferenceField, DateTimeField, ListField, DateField


class Journal(Document):
    entry_no = StringField(unique=True, required=True)
    journal_type = StringField(required=True)
    status = StringField(required=True)
    date = DateField(required=True)

    reference_number = StringField()
    reference_date = DateTimeField()
    user_remark = StringField()
    # attachment = StringField()

    created_at = DateTimeField(required=True)
    updated_at = DateTimeField(required=False)

    number_series = ReferenceField("NumberSeries", required=True)
    accounts = ListField(ReferenceField("JournalAccount"), required=True)
    client = ReferenceField("Client", required=True)
    user = ReferenceField("User", required=True)
    transaction = ReferenceField("Transaction", required=True)

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.datetime.utcnow()
        self.updated_at = datetime.datetime.utcnow()
        return super(Journal, self).save(*args, **kwargs)

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
        "collection": "Journals",
        "indexes": ["entry_no", "journal_type", "status", "user", "client"],
        "allow_inheritance": True,
        "index_cls": False,
    }
