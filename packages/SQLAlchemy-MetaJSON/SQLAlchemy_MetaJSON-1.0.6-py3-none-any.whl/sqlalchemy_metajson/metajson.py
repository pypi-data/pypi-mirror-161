"""
Main Module of metajson library. Generates and builds all of json
object from all of the information in the sqlalchemy declarative
base.
"""
from collections import abc
import json
from functools import reduce
from sqlalchemy_utils import get_mapper

from sqlalchemy_metajson.get_type import get_type

enums = {}


def lower_first_char(string):
    return string[:1].lower() + string[1:] if string else ""


def snake_to_camel_case(string, leading_caps=False):
    string = reduce(
        (lambda str1, str2: str1 + str2),
        map(lambda str: str.capitalize(), string.split("_")),
    )
    if not leading_caps:
        return lower_first_char(string)
    return string


def merge_dictionaries(dictionary, merge_dictionary):
    for key, value in merge_dictionary.items():
        if key in dictionary and isinstance(dictionary[key], dict)\
                and isinstance(merge_dictionary[key], abc.Mapping):
            merge_dictionaries(dictionary[key], merge_dictionary[key])
        else:
            dictionary[key] = merge_dictionary[key]

#
# def create_connection_and_edge_class(name):
#     connection = {}
#     edge = {}
#     # connection["description"] = ""
#     connection["directives"] = {}
#     connection["fieldOrder"] = ["edges"]
#     connection["fields"] = {}
#     connection["fields"]["edges"] = {}
#     connection["fields"]["edges"]["arguments"] = []
#     # connection["fields"]["edges"]["description"] = None
#     connection["fields"]["edges"]["directives"] = {}
#     connection["fields"]["edges"]["isList"] = False
#     connection["fields"]["edges"]["kind"] = "FieldDefinition"
#     connection["fields"]["edges"]["type"] = name + "Edge"
#     connection["interfaces"] = []
#     connection["kind"] = "ObjectTypeDefinition"
#     connection["type"] = "Object"
#     # edge["description"] = ""
#     edge["directives"] = {}
#     edge["fieldOrder"] = ["node"]
#     edge["fields"] = {}
#     edge["interfaces"] = []
#     edge["kind"] = "ObjectTypeDefinition"
#     edge["type"] = "Object"
#     edge["fields"]["node"] = {}
#     edge["fields"]["node"]["arguments"] = []
#     # edge["fields"]["edges"]["description"] = None
#     edge["fields"]["node"]["directives"] = {}
#     edge["fields"]["node"]["isList"] = False
#     edge["fields"]["node"]["kind"] = "FieldDefinition"
#     edge["fields"]["node"]["type"] = name
#
#     return connection, edge


def choices_to_mapping(choices):

    choice_mapping = {}
    for choice in choices:
        choice_mapping[choice[0]] = choice[1]
    return choice_mapping


def get_col_field_info(col, schema_name, name, default_field_attributes):
    field_info = {}
    type = get_type(col.name, col.type)
    field_info["type"] = type
    field_info["fieldName"] = schema_name

    field_info["required"] = not col.nullable and not col.default

    if type == "enum":
        field_info["choiceOrder"] = [choice[0] for choice in col.type.choices]
        field_info["choices"] = choices_to_mapping(col.type.choices)

    #field_info["arguments"] = []
    metadata = col.info["metadata"] if "metadata" in col.info else {}

    merge_dictionaries(field_info, metadata)
    #field_info["kind"] = "FieldDefinition"
    #field_info["isList"] = False

    for key, value in default_field_attributes.items():
        if key not in metadata:
            field_info[key] = value(col, name)

    return field_info


def get_inverse_side(rel):
    inverse_name = rel.back_populates
    return snake_to_camel_case(inverse_name)


def format_direction(direction):
    split = direction.lower().split("to")
    return f"{split[0].capitalize()}To{split[1].capitalize()}"


def get_direction(rel):
    return rel.direction.name


def is_rel_required(rel):
    for col in rel._user_defined_foreign_keys:
        return not col.nullable and not col.default
    return False

def get_rel_field_info(names_overrides, rel, schema_name, name, default_field_attributes):
    field_info = {}
    relationship_directive = {}
    field_info["fieldName"] = schema_name
    rel_name = get_model_name(rel.mapper, names_overrides)
    relationship_directive["target"] = rel_name

    direction = get_direction(rel)
    to_many = "TOMANY" in direction
    relationship_directive["type"] = format_direction(direction)

    relationship_directive["backref"] = get_inverse_side(rel)

    field_info["type"] = relationship_directive

    # field_info["type"] = rel_name + "Connection" if to_many else rel_name
    field_info["arguments"] = []

    field_info["required"] = is_rel_required(rel)

    metadata = rel.info["metadata"] if "metadata" in rel.info else {}
    merge_dictionaries(field_info, metadata)

    for key, value in default_field_attributes.items():
        if key not in metadata:
            field_info[key] = value(rel, name)

    # field_info["kind"] = "FieldDefinition"
    # field_info["isList"] = False

    return field_info, to_many


def get_model_meta(model, model_name, model_fields, default_model_attributes):
    model_meta = {}
    model_meta["modelName"] = model_name
    model_meta["fields"] = model_fields
    #model_meta["fieldOrder"] = getattr(model.class_.ViewMeta, "field_order", [])
    #model_meta["type"] = "Object"
    #model_meta["kind"] = "ObjectTypeDefinition"
    #model_meta["description"] = ""
    #model_meta["interfaces"] = []

    view_meta = getattr(model.class_, "ViewMeta", None)

    metadata = getattr(view_meta, "metadata", {})

    for key, value in default_model_attributes.items():
        if key not in metadata:
            model_meta[key] = value(model)

    merge_dictionaries(model_meta, metadata)

    return model_meta


#
# def get_hybrid_fields(info):
#     field_info = {}
#     field_info["kind"] = "FieldDefinition"
#     field_info["arguments"] = []
#     field_info["isList"] = False
#     field_info["type"] = info["type"] if "type" in info else {}
#     field_info["directives"] = info["directives"] if "directives" in info else {}
#     return field_info


def get_model_fields(name_overrides, model_mapper, excluded_classes, default_field_attributes):
    model_fields = {}
    #create_connection_and_edge = False

    for name, col in model_mapper.columns.items():
        if "_id" in name:
            continue
        schema_name = snake_to_camel_case(name)
        model_fields[schema_name] = get_col_field_info(col, schema_name, name, default_field_attributes)

    for name, rel in model_mapper.relationships.items():
        if rel.mapper.class_ in excluded_classes:
            continue
        schema_name = snake_to_camel_case(name)
        model_fields[schema_name], to_many = get_rel_field_info(
            name_overrides, rel, schema_name, name, default_field_attributes
        )
        # if to_many:
        #     create_connection_and_edge = True
    # for name, hybrid in model._sa_class_manager._all_sqla_attributes():
    #     if not isinstance(hybrid, hybrid_property):
    #         continue
    #     model_fields[to_camel_case(name)] = get_hybrid_fields(hybrid.info)
    return model_fields #, create_connection_and_edge


def get_model_name(mapper, name_overrides = {}):
    model_name = mapper.class_.__name__

    return model_name if model_name not in name_overrides else name_overrides[model_name]


def get_tables(db):
    return db.metadata.tables


def get_name_overrides(db):
    tables = get_tables(db)
    names = {}
    for name, table in tables.items():
        try:
            model_mapper = get_mapper(table)
        except ValueError:
            continue

        view_meta = getattr(model_mapper.class_, "ViewMeta", None)
        name_override = getattr(view_meta, "name_override", None)

        if name_override:
            names[get_model_name(model_mapper)] = name_override
    return names


def exclude_model(model_mapper):
    view_meta = getattr(model_mapper.class_, "ViewMeta", None)
    return view_meta and getattr(view_meta, 'exclude', False)


def meta_json(db, **kwargs):
    """
    Main main of library. Takes in as input a SQLAlchemy declarative
    base object and returns a json object with the meta data extracted
    from the db.

    :param db:  sqlalchemy declarative base from which the meta
                information is extracted
    :param **kwargs: can handle default attributes at model and field level
    :return:    json object holding the extracted meta information
    """
    top_level = {"version": "v0.0.1"}

    tables = get_tables(db)
    meta = {}
    name_overrides = get_name_overrides(db)
    excluded_classes = []

    default_model_attributes = {}
    default_field_attributes = {}

    for key, value in kwargs.items():
        type, attribute_name = key.split("_")
        if type == "model":
            default_model_attributes[attribute_name] = value
        elif type == "field":
            default_field_attributes[attribute_name] = value

    for name, table in tables.items():
        try:
            model_mapper = get_mapper(table)
        except ValueError:
            continue
        if exclude_model(model_mapper):
            excluded_classes.append(model_mapper.class_)
            continue

        model_name = get_model_name(model_mapper, name_overrides)

        model_fields = get_model_fields(name_overrides, model_mapper, excluded_classes, default_field_attributes)

        meta[model_name] = get_model_meta(model_mapper, model_name, model_fields, default_model_attributes)

    top_level["definitions"] = meta
    return json.dumps(top_level)
