# dsl_registry/gql_schema_to_dsl.py

import os
import yaml
from graphql import build_schema

SCHEMA_PATH = "data/schema.graphql"
DSL_OUTPUT_DIR = "generated_dsls"

os.makedirs(DSL_OUTPUT_DIR, exist_ok=True)

from graphql import GraphQLNonNull, GraphQLList

def type_to_str(graphql_type):
    if isinstance(graphql_type, GraphQLNonNull):
        return f"{type_to_str(graphql_type.of_type)}!"
    elif isinstance(graphql_type, GraphQLList):
        return f"[{type_to_str(graphql_type.of_type)}]"
    elif hasattr(graphql_type, "name"):
        return graphql_type.name
    return str(graphql_type)

def extract_type_definition(graphql_type, visited=None):
    if visited is None:
        visited = set()
    result = {}
    if not hasattr(graphql_type, "fields"):
        return {}
    for field_name, field in graphql_type.fields.items():
        field_type = type_to_str(field.type)
        result[field_name] = field_type
        inner_type = getattr(field.type, "of_type", None)
        if inner_type and hasattr(inner_type, "fields") and inner_type.name not in visited:
            visited.add(inner_type.name)
            result.update({inner_type.name: extract_type_definition(inner_type, visited)})
    return result

def generate_dsl(name, type_, field, schema):
    description = field.description or f"{type_} {name}"
    args = field.args
    args_str = ", ".join([f"{k}: ${k}" for k in args])
    var_defs = ", ".join([f"${k}: {str(args[k].type)}" for k in args])
    query_template = (
        f"{type_} {f'({var_defs})' if var_defs else ''} {{ {name}{f'({args_str})' if args_str else ''} {{ ... }} }}"
    )

    related_types = []
    type_definitions = {}
    return_type = getattr(field.type, "of_type", None) or field.type
    if hasattr(return_type, "fields"):
        related_types.append(return_type.name)
        type_definitions[return_type.name] = extract_type_definition(return_type)

    for arg in args.values():
        input_type = getattr(arg.type, "of_type", None) or arg.type
        if hasattr(input_type, "fields"):
            related_types.append(input_type.name)
            type_definitions[input_type.name] = extract_type_definition(input_type)

    dsl_data = {
        "name": name,
        "type": type_,
        "description": description,
        "query_template": query_template,
        "variables": list(args.keys()),
        "related_types": related_types,
        "type_definitions": type_definitions,
    }

    file_path = os.path.join(DSL_OUTPUT_DIR, f"{type_}_{name}.yaml")
    with open(file_path, "w") as f:
        yaml.dump(dsl_data, f, sort_keys=False, allow_unicode=True)
    print(f"✅ Generated: {file_path}")

def main():
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_text = f.read()
    schema = build_schema(schema_text)

    for root_type, type_name in [("query", "Query"), ("mutation", "Mutation")]:
        graphql_type = schema.get_type(type_name)
        if graphql_type:
            for name, field in graphql_type.fields.items():
                generate_dsl(name, root_type, field, schema)

if __name__ == "__main__":
    main()
