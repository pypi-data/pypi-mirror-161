import pytest
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import relationship
from sqlalchemy.types import Boolean
from sqlalchemy.types import Date
from sqlalchemy.types import DateTime
from sqlalchemy.types import Integer
from sqlalchemy.types import String
from sqlalchemy.types import Text
from sqlalchemy.types import VARCHAR
from sqlalchemy_utils import get_mapper
from sqlalchemy_utils.types import ChoiceType
from sqlalchemy_utils.types import EmailType
from sqlalchemy_utils.types import URLType

import sqlalchemy_metajson.metajson as metajson
from sqlalchemy_metajson.get_type import get_type

test_names = [
    "Testing Space",
    "Testing_UnderScore",
    "TESTINGALLCAPS",
    "testingalllower",
    "T3s71ngM1X3DC4S3",
]


@pytest.fixture
def default_info():
    return {"arguments": [], "isList": False, "kind": "FieldDefinition"}


@pytest.fixture
def default_fields():
    return {
        "directives": {},
        "fieldOrder": ["edges"],
        "fields": {
            "edges": {
                "arguments": [],
                "directives": {},
                "isList": True,
                "kind": "FieldDefinition",
                "type": "Edge",
            }
        },
        "interfaces": [],
        "kind": "ObjectTypeDefinition",
        "type": "Object",
    }


@pytest.fixture
def base():
    return declarative_base()


@pytest.fixture
def view_meta_factory():
    class ViewMetaFactory(object):
        def create_view_meta(self, attributes):
            return type("ViewMeta", (object,), attributes)

    return ViewMetaFactory()


@pytest.fixture
def table_factory(base, view_meta_factory):
    class TableFactory(object):
        def create_table(
            self, class_name, table_name, view_meta_attributes={}, table_cols=[]
        ):
            attributes = {}
            attributes["__tablename__"] = table_name
            attributes["id"] = Column(Integer, primary_key=True)
            attributes["ViewMeta"] = view_meta_factory.create_view_meta(
                view_meta_attributes
            )
            for name, col in table_cols:
                attributes[name] = col

            return type(class_name, (base,), attributes)

    return TableFactory()


@pytest.mark.parametrize(
    "unformatted,formatted",
    [
        ("ONETOONE", "OneToOne"),
        ("ONETOMANY", "OneToMany"),
        ("MANYTOONE", "ManyToOne"),
        ("MANYTOMANY", "ManyToMany"),
    ],
)
def test_format_direction(unformatted, formatted):
    assert metajson.format_direction(unformatted) == formatted


@pytest.mark.parametrize(
    "name,field_type,expected_type",
    [
        ("id", Integer, "ID"),
        ("int", Integer, "Int"),
        ("Text", Text, "String"),
        ("VARCHAR", VARCHAR, "String"),
        ("String", String, "String"),
        ("DateTime", DateTime, "String"),
        ("Date", Date, "String"),
        # ("phone", PhoneNumberType, "String"),
        ("email", EmailType, "String"),
        ("url", URLType, "String"),
        ("boolean", Boolean, "Boolean"),
        ("enum", ChoiceType([("test", "test")]), "Enum"),
        ("none", None, "None"),
    ],
)
def test_get_type(name, field_type, expected_type):
    assert get_type(name, Column(field_type).type) == expected_type


@pytest.mark.parametrize(
    "name, lower",
    [
        ("alllower", "alllower"),
        ("ALLUPPER", "aLLUPPER"),
        ("T3s71ngM1X3DC4S3", "t3s71ngM1X3DC4S3"),
        ("a", "a"),
        ("A", "a"),
        ("3", "3"),
        ("_", "_"),
        (",", ","),
        ("", ""),
    ],
)
def test_lower_first_char(name, lower):
    assert metajson.lower_first_char(name) == lower


@pytest.mark.parametrize("name", test_names)
def test_get_model_name(table_factory, name):
    assert name == table_factory.create_table(name, name).__tablename__


@pytest.mark.parametrize(
    "snake_case,camel_case,leading_caps",
    [
        ("nounderscore", "Nounderscore", True),
        ("nounderscore", "nounderscore", False),
        ("one_underscore", "OneUnderscore", True),
        ("one_underscore", "oneUnderscore", False),
        ("more_than_one_underscore", "MoreThanOneUnderscore", True),
        ("more_than_one_underscore", "moreThanOneUnderscore", False),
    ],
)
def test_snake_to_camel_case(snake_case, camel_case, leading_caps):
    assert (
        metajson.snake_to_camel_case(snake_case, leading_caps=leading_caps)
        == camel_case
    )


@pytest.mark.parametrize("name", test_names)
def test_create_connection_and_edge_class(name):
    connection, edge = metajson.create_connection_and_edge_class(name)
    assert connection["directives"] == {}
    assert connection["fieldOrder"] == ["edges"]
    assert connection["fields"]["edges"]["arguments"] == []
    assert connection["fields"]["edges"]["directives"] == {}
    assert not connection["fields"]["edges"]["isList"]
    assert connection["fields"]["edges"]["kind"] == "FieldDefinition"
    assert connection["fields"]["edges"]["type"] == name + "Edge"
    assert connection["interfaces"] == []
    assert connection["kind"] == "ObjectTypeDefinition"
    assert connection["type"] == "Object"
    assert edge["directives"] == {}
    assert edge["fieldOrder"] == ["node"]
    assert edge["fields"]["node"]["arguments"] == []
    assert edge["fields"]["node"]["directives"] == {}
    assert not edge["fields"]["node"]["isList"]
    assert edge["fields"]["node"]["kind"] == "FieldDefinition"
    assert edge["fields"]["node"]["type"] == name


@pytest.mark.parametrize(
    "field_type, output_type, directives",
    [
        (String, "String", {}),
        (VARCHAR, "String", {}),
        (Text, "String", {}),
        (DateTime, "String", {}),
        (Date, "String", {}),
        (EmailType, "String", {}),
        (URLType, "String", {}),
        (URLType, "String", {"directives": "Hyperlink"}),
        (Integer, "Int", {}),
        (Boolean, "Boolean", {}),
        (ChoiceType([("one", "two")]), "Enum", {}),
    ],
)
def test_get_col_field_info(base, field_type, output_type, default_info, directives):
    column = Column(field_type, info=directives)
    result = metajson.get_col_field_info(column)

    assert result["type"] == output_type
    assert result["arguments"] == default_info["arguments"]
    assert result["isList"] == default_info["isList"]
    assert result["kind"] == default_info["kind"]

    if "directives" in column.info:
        assert result["directives"] == column.info["directives"]
    else:
        assert result["directives"] == directives

    if "choices" in result:
        assert result["choices"][field_type.choices[0][1]] == field_type.choices[0][0]


@pytest.mark.parametrize(
    "parent_name, parent_attributes, child_attributes, expected_type, expected_inverse_side",
    [
        # One To Many
        (
            "parent",
            [
                (
                    "children",
                    relationship(
                        "child", backref="parent", info={"directives": {"Test": "Test"}}
                    ),
                )
            ],
            [("parent_id", Column(Integer, ForeignKey("parent.id")))],
            "OneToMany",
            "parent",
        ),
        # Many To One
        (
            "step_parent",
            [
                ("child", relationship("child", backref="step_parent")),
                ("child_id", Column(Integer, ForeignKey("child.id"))),
            ],
            [],
            "ManyToOne",
            "stepParent",
        ),
        # One To One (Not working)
        # ("single_parent", [("child", relationship("child", uselist=False, back_populates="single_parent")),
        #     ("child_id", Column(Integer, ForeignKey("child.id")))],
        #     [("single_parent", relationship("single_parent", back_populates="child", uselist=False))], "OneToOne",
        #       "singleParent"),
        # Many To Many
        ("relative", [], [], "ManyToMany", "relative"),
    ],
)
def test_get_rel_field_info(
    base,
    parent_name,
    parent_attributes,
    child_attributes,
    expected_type,
    expected_inverse_side,
    table_factory,
    default_info,
):
    if parent_name == "relative":
        association_table = Table(
            "association",
            base.metadata,
            Column("relative_id", Integer, ForeignKey("relative.id")),
            Column("child_id", Integer, ForeignKey("child.id")),
        )
        parent_attributes.append(
            (
                "children",
                relationship("child", backref="relative", secondary=association_table),
            )
        )

    parent_table = table_factory.create_table(
        parent_name, parent_name, {}, parent_attributes
    )
    child_rel_name = parent_attributes[0][0]
    table_factory.create_table("child", "child", {}, child_attributes)

    parent_model_mapper = inspect(parent_table)
    name, rel = parent_model_mapper.relationships.items()[0]

    rel_info_result, to_many_result = metajson.get_rel_field_info({"child": name}, rel)

    assert rel_info_result["isList"] == default_info["isList"]
    assert rel_info_result["arguments"] == default_info["arguments"]
    assert rel_info_result["kind"] == default_info["kind"]

    child_connection_name = child_rel_name + "Connection"

    assert (
        rel_info_result["type"] == child_rel_name
        if not to_many_result
        else child_connection_name
    )

    if "directives" in rel.info:
        for key, value in rel.info.items():
            assert key in rel_info_result
            assert rel_info_result[key] == value

    assert rel_info_result["directives"]["Relationship"]["target"] == child_rel_name
    assert rel_info_result["directives"]["Relationship"]["type"] == expected_type
    assert (
        rel_info_result["directives"]["Relationship"]["inverseSide"]
        == expected_inverse_side
    )


def test_get_tables(base, table_factory):
    # Test 1: No tables
    assert base.metadata.tables == metajson.get_tables(base)

    # Test 2: There exists a table
    table_factory.create_table("sample_table", "sample_table")

    assert base.metadata.tables == metajson.get_tables(base)

    # Test 3: There exists more than one table
    table_factory.create_table("sample_table2", "sample_table2")

    assert base.metadata.tables == metajson.get_tables(base)


@pytest.mark.parametrize(
    "table_name, table_attributes, expected_inverse_side",
    [
        ("parent", [("children", relationship("child", backref="parent"))], "parent"),
        (
            "parent_test",
            [("children", relationship("child", backref="parent_test"))],
            "parentTest",
        ),
    ],
)
def test_get_inverse_side(
    base, table_factory, table_name, table_attributes, expected_inverse_side
):
    parent_table = table_factory.create_table(
        table_name, table_name, {}, table_attributes
    )
    table_factory.create_table(
        "child",
        "child",
        {},
        [(table_name + "_id", Column(Integer, ForeignKey(table_name + ".id")))],
    )

    parent_model_mapper = inspect(parent_table)
    name, rel = parent_model_mapper.relationships.items()[0]
    assert metajson.get_inverse_side(rel) == expected_inverse_side


def test_get_direction(base, table_factory):
    parent_table = table_factory.create_table(
        "parent", "parent", {}, [("children", relationship("child"))]
    )
    table_factory.create_table(
        "child", "child", {}, [("parent_id", Column(Integer, ForeignKey("parent.id")))]
    )

    parent_model_mapper = inspect(parent_table)
    name, rel = parent_model_mapper.relationships.items()[0]
    assert metajson.get_direction(rel) == rel.direction.name


def test_get_model_meta(base, table_factory, default_fields):
    my_table = table_factory.create_table("sample_table", "sample_table")
    table_model_mapper = get_mapper(my_table)
    table_name = table_model_mapper.class_.__tablename__
    default_fields["fields"]["edges"]["type"] = (
        table_name + default_fields["fields"]["edges"]["type"]
    )

    meta_results = metajson.get_model_meta(
        table_model_mapper, table_name, default_fields
    )

    assert meta_results["name"] == table_name
    assert meta_results["fields"] == default_fields
    assert meta_results["directives"] == getattr(
        table_model_mapper.class_.ViewMeta, "directives", {}
    )
    assert meta_results["fieldOrder"] == getattr(
        table_model_mapper.class_.ViewMeta, "field_order", []
    )
    assert meta_results["type"] == "Object"
    assert meta_results["kind"] == "ObjectTypeDefinition"
    assert meta_results["interfaces"] == []


def test_get_name_overrides(base, table_factory):
    table_name = "test_table"
    override_table_name = "override_table"
    override_name = "overridden"
    normal_table = table_factory.create_table(table_name, table_name)  # noqa:F841
    override_table = table_factory.create_table(  # noqa:F841
        override_table_name, override_table_name, {"name_override": override_name}
    )
    names = metajson.get_name_overrides(base)
    assert names[table_name] == metajson.snake_to_camel_case(table_name, True)
    assert names[override_table_name] == metajson.snake_to_camel_case(override_name)


@pytest.mark.parametrize(
    "parent_name, parent_attributes, child_name, child_attributes",
    [
        (
            "parent",
            [("children", relationship("child", backref="parent"))],
            "child",
            [("parent_id", Column(Integer, ForeignKey("parent.id")))],
        ),
        (
            "parent_test",
            [("children", relationship("child", backref="parent_test"))],
            "child",
            [("parent_test_id", Column(Integer, ForeignKey("parent_test.id")))],
        ),
        (
            "parent",
            [("children", relationship("child_test", backref="parent"))],
            "child_test",
            [("parent_id", Column(Integer, ForeignKey("parent.id")))],
        ),
        (
            "parent_test",
            [("children", relationship("child_test", backref="parent_test"))],
            "child_test",
            [("parent_test_id", Column(Integer, ForeignKey("parent_test.id")))],
        ),
        (
            "parent",
            [("children", relationship("child_id", backref="parent"))],
            "child_id",
            [("parent_id", Column(Integer, ForeignKey("parent.id")))],
        ),
        (
            "parent_id",
            [("children", relationship("child", backref="parent_id"))],
            "child",
            [("parent_id_id", Column(Integer, ForeignKey("parent_id.id")))],
        ),
        (
            "step_parent",
            [
                ("child_id", Column(Integer, ForeignKey("child.id"))),
                ("child", relationship("child", backref="step_parent")),
            ],
            "child",
            [],
        ),
    ],
)
def test_get_model_fields(
    base, table_factory, parent_name, parent_attributes, child_name, child_attributes
):
    parent_table = table_factory.create_table(
        parent_name, parent_name, {}, parent_attributes
    )
    table_factory.create_table(child_name, child_name, {}, child_attributes)

    parent_model_mapper = inspect(parent_table)
    names = metajson.get_name_overrides(base)

    for col_name, col in parent_model_mapper.columns.items():
        if "_id" in col_name:
            continue
        break

    col_info = metajson.get_col_field_info(col)
    rel_name, rel = parent_model_mapper.relationships.items()[0]
    rel_info, to_many = metajson.get_rel_field_info(names, rel)

    result_model_field, result_connection_and_edge = metajson.get_model_fields(
        names, parent_model_mapper
    )

    assert result_model_field[col_name] == col_info
    assert result_model_field[rel_name] == rel_info
    assert result_connection_and_edge == to_many
