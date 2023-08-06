import re
import pydash as __


def scream_case(value):
    return __.strings.snake_case(value).upper()


def capitalize(txt=''):
    return txt and txt[0].upper() + txt[1:]


def remove_capital(word):
    return f'{word[0].lower()}{word[1:]}'


def contains_digits(d):
    _digits = re.compile(r'\d')
    return bool(_digits.search(d))


def objPathToTypeParam(fieldPath):
    '''
    from: "brightBeer.name"
    to: "brightBeerName"
    '''
    fieldTags = fieldPath.split('.')
    if len(fieldTags) == 1:
        typeParam = fieldTags[0]
    else:
        typeParam = f'{fieldTags[0]}{capitalize(fieldTags[1])}'
    return typeParam
