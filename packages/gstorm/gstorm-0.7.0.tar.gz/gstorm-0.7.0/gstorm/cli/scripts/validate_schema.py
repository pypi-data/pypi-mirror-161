import os
from pprint import pformat
import click
from gstorm.helpers.Logging import log, LogLevel
from gstorm.helpers.gql_schema_helpers import load_schema_from_file


def gql_schema_validate(schema):
    errors = []
    for typename, item in schema.items():
        log(LogLevel.INFO, f'\nvalidating type {typename}')
        # ! Style validation
        if typename[0].islower() or '_' in typename:
            # * No lowercasing Types
            errors.append({
                'type': item['name'],
                'field': field['name'],
                'message': f'Typename "{typename}" should be in CapitalCase'
            })
        if item['kind'] == 'TYPE':
            # ! validate every field
            for field in item['fields']:
                log(LogLevel.INFO, f'\tvalidating field {field["name"]}')
                # ! Style validation
                if field['name'][0].isupper():
                    # * NO Capitalizing fields
                    errors.append({
                        'type': item['name'],
                        'field': field['name'],
                        'message': f'Field "{field["name"]}" should not be capitalized'
                    })
                elif '_' in field['name']:
                    errors.append({
                        'type': item['name'],
                        'field': field['name'],
                        'message': f'Field "{field["name"]}" should be in camelCase'
                    })
                # ! Schema validation
                if field['type']['kind'] == 'SCALAR':
                    # u all right, fam
                    continue
                elif field['type']['kind'] == 'LIST':
                    # first of all, this type exists?
                    if not field['type']['name'] in schema:
                        errors.append({
                            'type': item['name'],
                            'field': field['name'],
                            'message': f'LIST type "{field["type"]["name"]}" does not exist'
                        })
                        continue
                    # validate List Referring type has a field with corresponding type
                    referred_type = schema[field['type']['name']]
                    referred_fields = [
                        ref_field for ref_field in referred_type['fields']
                        if ref_field['type']['name'] == typename
                        and not ref_field['has_one']
                    ]
                    if len(referred_fields) == 0:
                        errors.append({
                            'type': item['name'],
                            'field': field['name'],
                            'message': 'LIST Has no corresponding object in referred type'
                        })
                    # elif len(referred_fields) > 1:
                    #   errors.append({
                    #     'type': item['name'],
                    #     'field': field['name'],
                    #     'message': 'LIST has too many referred types (Should be only one)'
                    #   })
                elif field['type']['kind'] == 'OBJECT' and field['has_one']:
                    # first of all, this type exists?
                    if not field['type']['name'] in schema:
                        errors.append({
                            'type': item['name'],
                            'field': field['name'],
                            'message': f'OBJECT type "{field["type"]["name"]}" does not exist'
                        })
                        continue
                    # validate Object Referring type has a field with corresponding type
                    referred_type = schema[field['type']['name']]
                    referred_fields = [
                        ref_field for ref_field in referred_type['fields']
                        if ref_field['type']['name'] == typename
                        and not ref_field['has_one']
                    ]
                    if len(referred_fields) == 0:
                        errors.append({
                            'type': item['name'],
                            'field': field['name'],
                            'message': 'HAS_ONE has no corresponding object in referred type'
                        })
                    # elif len(referred_fields) > 1:
                    #   errors.append({
                    #     'type': item['name'],
                    #     'field': field['name'],
                    #     'message': 'HAS_ONE has too many referred types (Should be only one)'
                    #   })
                elif field['type']['kind'] == 'OBJECT' and not field['has_one']:
                    # first of all, this type exists?
                    if not field['type']['name'] in schema:
                        errors.append({
                            'type': item['name'],
                            'field': field['name'],
                            'message': f'Object field type "{field["type"]["name"]}" does not exist'
                        })
                        continue
                    # validate List Referring type has a field with corresponding type
                    referred_type = schema[field['type']['name']]
                    referred_fields_has_one = [
                        ref_field for ref_field in referred_type['fields']
                        if ref_field['type']['name'] == typename
                        and ref_field['has_one']
                    ]
                    referred_fields_list = [
                        ref_field for ref_field in referred_type['fields']
                        if ref_field['type']['name'] == typename
                        and ref_field['type']['kind'] == 'LIST'
                    ]
                    if (
                        len(referred_fields_has_one) > 0
                        and len(referred_fields_list) > 0
                    ):
                        errors.append({
                            'type': item['name'],
                            'field': field['name'],
                            'message': 'OBJECT reference is both HAS_ONE and LIST in referred type'
                        })
                    elif (
                        len(referred_fields_has_one) == 0
                        and len(referred_fields_list) == 0
                    ):
                        errors.append({
                            'type': item['name'],
                            'field': field['name'],
                            'message': f'field {field["name"]} has no corresponding LIST or HAS_ONE'
                        })
        elif item['kind'] == 'ENUM':
            # ! validate Enumeration usage
            schema_object_types = {tn2: i2 for tn2,
                                   i2 in schema.items() if i2['kind'] == 'TYPE'}
            referring_types = [
                1 for typename2, item2 in schema_object_types.items()
                if len([
                    1 for field in item2['fields']
                    if field['type']['name'] == item['name']
                ]) > 0
            ]
            if len(referring_types) == 0:
                errors.append({
                    'type': item['name'],
                    'field': '',
                    'message': 'ENUM does not have any referring type (should be at least one)'
                })
    return errors


@click.command()
@click.option('--src', default=None, help='Graphql schema file to analyze')
def validate_schema(src: str):
    """Validates graphql schema relations

    Parameters
    ----------
    src : str
      relative path to schema file (.graphql)
      ex: "gstorm-cli validate-schema --src=graphql/doc/schema.graphql"
    """
    # ! THIS
    schema = load_schema_from_file(src)
    from pprint import pprint
    pprint(schema)
    # ! UNTIL HERE
    validation_errors = gql_schema_validate(schema)
    if len(validation_errors) > 0:
        log(LogLevel.ERROR,
            f'\n\n{len(validation_errors)} ERROR FOUND INSPECTING THE SCHEMA:')
        log(LogLevel.ERROR, pformat(validation_errors))
        log(LogLevel.ERROR, '\n\n')
    else:
        log(LogLevel.SUCCESS, '\n\nNo errors found in the schema :)\n\n')
