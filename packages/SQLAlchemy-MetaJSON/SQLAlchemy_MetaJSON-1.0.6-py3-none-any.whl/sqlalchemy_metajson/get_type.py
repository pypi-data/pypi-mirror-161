from sqlalchemy.types import Boolean
from sqlalchemy.types import Date
from sqlalchemy.types import DateTime
from sqlalchemy.types import Integer
from sqlalchemy.types import String
from sqlalchemy.types import Text
from sqlalchemy.types import Time
from sqlalchemy.types import Float
from sqlalchemy.types import VARCHAR
from sqlalchemy.types import JSON
from sqlalchemy_utils.types import ChoiceType
from sqlalchemy_utils.types import EmailType
from sqlalchemy_utils.types import PhoneNumberType
from sqlalchemy_utils.types import URLType
from sqlalchemy_utils.types import CurrencyType
from sqlalchemy.types import DECIMAL


def get_type(name, field_type):
    if name == "id":
        return "ID"
    if isinstance(field_type, Integer):
        return "int"
    if isinstance(field_type, Text):
        return "text"
    if isinstance(field_type, Date)\
            or isinstance(field_type, DateTime)\
            or isinstance(field_type, Time):
        return "date"
    if isinstance(field_type, PhoneNumberType):
        return "phone"
    if isinstance(field_type, EmailType):
        return "email"
    if isinstance(field_type, URLType):
        return "url"
    if isinstance(field_type, DECIMAL):
        return "decimal"
    if isinstance(field_type, CurrencyType):
        return "currency"
    if isinstance(field_type, VARCHAR) or isinstance(field_type, String):
        return "string"
    if isinstance(field_type, Boolean):
        return "boolean"
    if isinstance(field_type, ChoiceType):
        return "enum"
    if isinstance(field_type, JSON):
        return "json"
    if isinstance(field_type, Float):
        return "float"
    raise TypeError(field_type)


class TypeError(Exception):
    def __init__(self, field_type):
        self.field_type = field_type
        self.message = f"Type: {field_type} not found in type registry"


