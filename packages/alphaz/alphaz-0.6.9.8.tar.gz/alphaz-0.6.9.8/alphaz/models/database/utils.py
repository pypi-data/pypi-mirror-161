import importlib, json, typing

from marshmallow import Schema
from marshmallow import fields as cfields
from marshmallow_sqlalchemy import ModelConverter, fields

from ...config.main_configuration import CONFIGURATION

from ..logger import AlphaLogger

SCHEMAS = {}
MODULES = {}
LOG = None


def __get_nested_schema(mapper, parent=None):
    auto_schema = get_auto_schema(mapper.entity)

    from core import core

    mapper_name = str(mapper).split("class ")[1].split("->")[0]
    schema_name = mapper_name + "Schema"

    columns = []
    if hasattr(mapper, "columns"):
        for column in mapper.columns:
            columns.append(column.name)

    # Dynamic schema class creation
    properties = {"Meta": type("Meta", (object,), {"fields": columns})}
    schema = type(schema_name, (core.ma.Schema,), properties)
    return auto_schema


def get_auto_schema(
    model, relationship: bool = True, disabled_relationships: typing.List[str] = []
):
    from core import core

    if CONFIGURATION.DEBUG_SCHEMA:
        core.log.debug(f"Getting auto schema for <{model.__name__}>")

    properties = {
        "Meta": type(
            "Meta",
            (object,),
            {
                "model": model,
                "include_fk": True,
                "load_instance": True,
                "include_relationships": relationship,
            },
        )
    }
    schema = type(
        f"{model.__name__}Schema", (core.ma.SQLAlchemyAutoSchema,), properties
    )
    return schema


def __pdr(disabled_relationship):
    if type(disabled_relationship) != str and hasattr(disabled_relationship, "key"):
        relationship_name = disabled_relationship.key
        try:
            table_name = disabled_relationship.parent.local_table.name
        except:
            table_name = None
        return (table_name, relationship_name)
    elif type(disabled_relationship) != str:
        return (
            disabled_relationship if disabled_relationship is not None else (None, None)
        )
    return (None, disabled_relationship)


def __pdr_list_to_dict(l: list) -> dict:
    output = {}
    if type(l) == list:
        for sl in l:
            if type(sl) == list:
                out = __pdr_list_to_dict(sl[1:]) if len(sl) != 1 else None
                if not sl[0] in output:
                    output[__pdr(sl[0])] = out
                else:
                    for k, v in out.items():
                        output[__pdr(sl[0])][__pdr(k)] = v
            elif type(sl) == dict:
                for key, value in sl.items():
                    out = __pdr_list_to_dict(value)
                    if not key in output:
                        output[__pdr(key)] = out
                    else:
                        for k, v in out.items():
                            output[__pdr(key)][__pdr(k)] = v
            else:
                output[__pdr(sl)] = None
    elif type(l) == dict:
        for key, value in l.items():
            out = __pdr_list_to_dict(value)
            if not key in output:
                output[__pdr(key)] = out
            else:
                for k, v in out.items():
                    output[__pdr(key)][__pdr(k)] = v
    elif __pdr(l) != (None, None):
        output[__pdr(l)] = None
    return output


def __pdr_flat(pdr, content="", level=1):
    if type(pdr) == tuple:
        content += f"l{level}-{pdr[0]}-{pdr[1]}".replace("None", "a")
        return content
    for tp, value in pdr.items():
        sub_value = value
        if value is not None:
            sub_value = __pdr_flat(value, content, level + 1)
        content += f"l{level}-{tp[0]}-{tp[1]}_{sub_value}".replace("None", "a")
    return content


def generate_schema(
    class_obj,
    relationship: bool = True,
    disabled_relationships: typing.List[str] = None,
    parents: typing.List[str] = None,
):
    parents = parents or []
    disabled_relationships = disabled_relationships or []
    disabled_relationships = __pdr_list_to_dict(disabled_relationships)
    disabled_relationships_keys = __pdr_flat(disabled_relationships)

    # schema_key = "-".join([f"{x}:{str(y)}" for x, y in locals().items()])
    schema_key = (
        f"{class_obj.__tablename__}-{disabled_relationships_keys}-{str(parents)}"
    )
    if schema_key in SCHEMAS and not CONFIGURATION.DEBUG_SCHEMA:
        return SCHEMAS[schema_key]

    schema_name = f"{class_obj.__name__}Schema"
    schema_full_name = (
        schema_name
        if not relationship
        else f"{schema_name}_{disabled_relationships_keys}"
    )
    if schema_full_name in parents:
        if CONFIGURATION.DEBUG_SCHEMA:
            from core import core

            core.log.debug(f"Schema {schema_full_name} in parents {str(parents)}")
        relationship = False
        # return None

    auto_schema = get_auto_schema(class_obj, relationship=relationship)

    cols, related, related_list = {}, {}, {}
    for key, value in auto_schema._declared_fields.items():
        if type(value) == fields.Related and relationship:
            related[key] = value
        elif type(value) == fields.RelatedList and relationship:
            related_list[key] = value
        else:
            cols[key] = value

    columns, nesteds, list_nesteds = [], {}, {}
    for key, value in class_obj.__dict__.items():
        if key.startswith("__"):
            continue
        if not hasattr(value, "is_attribute") or not value.is_attribute:
            continue

        if hasattr(value, "visible") and getattr(value, "visible"):
            columns.append(key)
        elif hasattr(value, "entity") and relationship:
            skip, disabled_relationships_child = False, []

            for (disabled_relationship, childs,) in disabled_relationships.items():
                if skip:
                    continue

                is_table = (
                    disabled_relationship[0] is None
                    or disabled_relationship[0] == class_obj.__tablename__
                )
                is_field = key == disabled_relationship[1]
                is_no_child = childs is None or len(childs) == 0
                if is_field and is_table and is_no_child:
                    skip = True
                    if CONFIGURATION.DEBUG_SCHEMA:
                        from core import core

                        core.log.debug(
                            f"Disable {key=} for {schema_full_name} with parents {str(parents)}"
                        )
                elif is_field and is_table:
                    disabled_relationships_child = childs
            if skip:
                continue

            entity = value.entity.entity

            columns.append(key)
            # if parent is None or not schema_full_name in SCHEMAS:
            # nested_schema = __get_nested_schema(value.entity, parent=class_obj)
            # nested_schema = get_schema(value.entity.entity)
            # else:
            if CONFIGURATION.DEBUG_SCHEMA:
                from core import core

                core.log.debug(
                    f"Parent {schema_full_name} has a child named {key} with parents {str(parents)}"
                )
            if not schema_full_name in parents:
                parents.append(schema_full_name)

            nested_schema = generate_schema(
                entity,
                relationship=relationship,
                disabled_relationships=disabled_relationships_child,
                parents=parents,
            )  # SCHEMAS[schema_full_name]

            if nested_schema is not None:
                if key in related:
                    nesteds[key] = nested_schema
                elif key in related_list:
                    list_nesteds[key] = nested_schema

    # g_s = ModelConverter()
    # flds = {x:y for x,y in g_s.fields_for_model(class_obj).items() if x in columns}

    for key, value in nesteds.items():
        cols[key] = fields.Nested(value)
    for key, value in list_nesteds.items():
        cols[key] = cfields.List(fields.Nested(value))
    generated_schema = Schema.from_dict(cols)

    SCHEMAS[schema_key] = generated_schema
    return generated_schema


def get_schema(
    class_obj,
    default: bool = False,
    relationship: bool = True,
    disabled_relationships: typing.List[str] = None,
):
    """ Get Schema for a model

    Args:
        class_obj ([type]): [description]
        parent ([type], optional): [description]. Defaults to None.

    Returns:
        [type]: [description]
    """
    disabled_relationships = disabled_relationships or []

    schema_name = f"{class_obj.__name__}Schema"

    if default:
        module_name = class_obj.__module__
        if not module_name in MODULES:
            mod = importlib.import_module(module_name)
            class_obj.log.info(f"Importing module <{module_name}>")
        else:
            mod = MODULES[module_name]
        if hasattr(mod, schema_name):
            return getattr(mod, schema_name)
        else:
            class_obj.log.error(
                f"Cannot find a default schema in module <{module_name}>"
            )
    generated_schema = generate_schema(
        class_obj,
        relationship=relationship,
        disabled_relationships=disabled_relationships,
    )
    return generated_schema
