import os
from gstorm.helpers.Logging import log, LogLevel


def inmemory_cleanup(src):
    src_path = os.path.join(os.getcwd(), src)
    output = []
    with open(src_path, 'r') as src_file:
        for line in src_file:
            is_whitespace = not line.strip()
            if is_whitespace:
                output.append(line)
                continue
            line = line.rstrip()  # clean
            line = line.split('#')[0].rstrip()  # remove comment
            # append if not empty
            if line:
                output.append(line + '\n')
        output.append('\n')
    return output


def scalar_map(field_typename):
    return {
        'Boolean': 'Boolean',
        'Integer': 'Int',
        'Float': 'Float',
        'String': 'String',
        'Text': 'Text',
        'Json': 'map',
        'Jsonb': 'map',
        'Date': 'Date',
        'Time': 'Time',
        'Datetime': 'DateTime'
    }[field_typename]


def get_field_kind(field_typename):
    scalar_types = [
        'Boolean',
        'Integer',
        'Float',
        'String',
        'Text',
        'Json',
        'Jsonb',
        'Date',
        'Time',
        'Datetime'
    ]
    if field_typename in scalar_types:
        return 'SCALAR'
    else:
        return 'OBJECT'


'''
Syntactic analizer for a graphql schema

things to consider:

# ! 1. general structure of a type
type TYPE_NAME @opts {
  ...
}
# ! 2. general structure of an enum
enum ENUM_TYPE @opts {
  ...
}
# ! 3. All basic types
type MyType {
  enabled: Boolean
  quantity: Int
  weight: Float
  name: String
  description: Text
  config: Json
  shipAt: Datetime
}
# ! 4. Complex type relations
# ? 4.1 ComplexType1.ListOf.ComplexType2 (Cannot be a list of BasicType)
# ? 4.2 ComplexType1.hasOne.ComplexType2 (Cannot be a hasOne of BasicType)
# ? 4.3 ComplexType1.ComplexType2 (ComplexType2 Must exist)
type User {
  name: String!
  address: Address @has_one
  posts: [Blogpost]
}

type Address {
  street: String
  city: String
  number: Integer
}

type Blogpost {
  author: User
  title: String @unique
}

type UserSkill {
  user: User
  skill: Skill
  level: Integer!
}

type Skill {
  name: String
}
'''


def gql_schema_parse(schema_file_lines):
    state = 'TYPE_SEARCH'
    schema = {}  # dict of typenames
    # context
    current_type = None
    current_field = None
    for line in schema_file_lines:
        line = line.strip()
        tokens = line.split()
        if (state == 'TYPE_SEARCH'):
            if len(tokens) == 0:
                continue
            if tokens[0] == 'type':
                state = 'PARSING_TYPE'
                current_type = {}
                current_type['name'] = tokens[1]
                current_type['kind'] = 'TYPE'
                current_type['fields'] = []
            elif tokens[0] == 'enum':
                state = 'PARSING_ENUM'
                current_type = {}
                current_type['name'] = tokens[1]
                current_type['kind'] = 'ENUM'
                current_type['enumValues'] = []
            else:
                continue
        elif (state == 'PARSING_TYPE'):
            if len(tokens) == 0:
                # blank line inside the type
                continue
            elif tokens[0] == '}':
                # end of type definition
                state = 'TYPE_SEARCH'
                schema[current_type['name']] = current_type
                current_type = None
            else:
                # type body (should be a field definition)
                field_name = tokens[0].strip(':')
                field_is_required = '!' in tokens[1]
                field_is_list = '[' in tokens[1] and ']' in tokens[1]
                field_typename = tokens[1].strip('!').strip('[]').strip('!')
                field_kind = get_field_kind(field_typename)
                field_has_one = False if len(
                    tokens) < 3 else '@has_one' == tokens[2]
                field_is_unique = False if len(
                    tokens) < 3 else '@unique' == tokens[2]
                if len(tokens) < 3 or not '@default' in tokens[2]:
                    field_default = None
                else:
                    field_default = tokens[3][:-1]
                current_field = {}
                # current_field['required'] = field_is_required
                # current_field['is_unique'] = field_is_unique
                current_field['unique'] = field_is_unique
                current_field['has_one'] = field_has_one
                current_field['default'] = field_default
                current_field['name'] = field_name
                current_field['type'] = {
                    'name': field_typename if field_kind == 'OBJECT' else scalar_map(field_typename),
                    'kind': 'LIST' if field_is_list else field_kind
                }
                current_type['fields'].append(current_field)
                current_field = None
        elif (state == 'PARSING_ENUM'):
            if len(tokens) == 0:
                # blank line inside the enum
                continue
            elif tokens[0] == '}':
                # end of enum definition
                state = 'TYPE_SEARCH'
                schema[current_type['name']] = current_type
                current_type = None
            else:
                # enum body (should be a EnumValue definition)
                current_type['enumValues'].append(tokens[0].strip())
    # we now know every schema type, we need to update the fields type kind to ENUM if needed:
    for typename, item in schema.items():
        if item['kind'] == 'ENUM':
            continue
        for index, field in enumerate(item['fields']):
            if not field['type']['name'] in schema:
                # may be an error, but leave it to the validation function
                continue
            if (
                field['type']['kind'] == 'OBJECT'
                and schema[field['type']['name']]['kind'] == 'ENUM'
            ):
                schema[typename]['fields'][index]['type']['kind'] = 'ENUM'
    return schema


def load_schema_from_file(src):
    try:
        clean_schema_lines = inmemory_cleanup(src)
        return gql_schema_parse(clean_schema_lines)
    except FileNotFoundError:
        log(LogLevel.ERROR, f'File {src} not found')
        return


def prettify_query(query):
    tabs = 0
    pretty_query = ''
    parsing_string = False
    inside_brackets = False
    for i, ch in enumerate(query):
        # get context
        prev_ch = query[i-1] if i > 0 else ''
        next_ch = query[i+1] if i < len(query) - 1 else ''
        if not inside_brackets and ch == '{':
            inside_brackets = True
        elif not inside_brackets:
            pretty_query += ch
            continue
        if not parsing_string and ch == '"':
            parsing_string = True
            pretty_query += ch
            continue
        if parsing_string and ch != '"':
            pretty_query += ch
            continue
        if parsing_string and ch == '"':
            parsing_string = False
            pretty_query += ch
            continue
        tabs += 1 if ch in ['{', '('] else (-1 if next_ch in ['}', ')'] else 0)
        if ch != ' ' or prev_ch == ':':
            pretty_query += ch
            continue
        if next_ch in ['{', '(']:
            pretty_query += ch  # add whitespace normally
        elif next_ch in ['}', ')']:
            pretty_query += f"\n{'  ' * tabs}"
        else:
            pretty_query += f"\n{'  ' * tabs}"
    return pretty_query
