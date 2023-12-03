from app.shared.utils.general import ExtendedEnum


class UserStatus(str, ExtendedEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DELETED = "deleted"


class Type(str, ExtendedEnum):
    SPEND = "Assets"
    INCOME = "Revenue"
    SAVE = "Expenses"


class Status(str, ExtendedEnum):
    DONE = "Done"
    DRAFT = "Draft"


class Period(str, ExtendedEnum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"
