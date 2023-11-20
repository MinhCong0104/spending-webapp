from mongoengine import Document, StringField, IntField, ReferenceField, BooleanField


class NumberSeries(Document):
    prefix = StringField(required=True)
    start = IntField(required=True, default=0)
    pad_zeros = IntField(required=True, default=4)
    reference_type = StringField(required=True)
    default = BooleanField(default=False)
    client = ReferenceField("Client", required=True)

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
        "collection": "NumberSeries",
        "indexes": ["reference_type", "prefix", "client"],
        "allow_inheritance": True,
        "index_cls": False,
    }
