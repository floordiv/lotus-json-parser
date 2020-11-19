from typing import List

import lotus.core.utils as utils
from lotus.core.operators import (OPERATORS_PRIORITY, TOKENS,
                                  SPECIAL_CHARACTERS, MINIMAL)
from lotus.core.tokens import Token
from lotus.core.tokentypes import (OPERATOR, NO_TYPE,
                                   INTEGER, FLOAT,
                                   VARIABLE, NEWLINE,
                                   KEYWORD, PARENTHESIS,
                                   BRACES, SQUARE_BRACES,
                                   FCALL, STRING, pytypes2lotus,
                                   keywords)

parenthesis_closers = {
    '(': ')',
    '{': '}',
    '[': ']',
}
parenthesis_type_by_opener = {
    '(': PARENTHESIS,
    '{': BRACES,
    '[': SQUARE_BRACES,
}


def lex(expression, ignore_newlines=False):
    tokens = [Token(NO_TYPE, '')]

    for letter in expression:
        if letter == ' ':
            if tokens[-1].value in keywords:
                tokens.append(Token(NO_TYPE, ''))
            elif tokens[-1].value[0] in tuple('"\'') and tokens[-1].value[-1] not in tuple('"\''):
                tokens[-1].value += letter

            continue
        elif letter == '\n':
            if ignore_newlines:
                continue

            tokens.append(Token(NEWLINE, '\n'))
            tokens.append(Token(NO_TYPE, ''))
            continue

        if letter in SPECIAL_CHARACTERS:
            # used to avoid of splitting "var.somevar" as ['var', '.', 'somevar']
            if letter == '.' and utils.valid_name(tokens[-1].value):
                tokens[-1].type = VARIABLE
                tokens[-1].value += letter
                continue

            if tokens[-1].type != OPERATOR or tokens[-1].value + letter not in TOKENS:
                if tokens[-1].value == '':
                    tokens[-1] = Token(OPERATOR, letter)
                else:
                    tokens.append(Token(OPERATOR, letter))
                    tokens[-1].vtype = TOKENS[tokens[-1].value]

                continue
        elif tokens[-1].type == OPERATOR:
            tokens[-1].vtype = TOKENS[tokens[-1].value]
            tokens.append(Token(NO_TYPE, letter))
            continue

        tokens[-1].value += letter

    return [token for token in tokens if token.value != '']


def provide_token_types(tokens: List[Token]):
    """
    provide token types only for untyped tokens
    """

    for token in filter(lambda _token: _token.type == NO_TYPE, tokens):
        token.value: str  # I hate charm. Looks like this helped. but not much

        if token.type == OPERATOR:
            token.vtype = TOKENS[token.value]
            token.priority = OPERATORS_PRIORITY.get(token.value, MINIMAL)
            continue

        if token.value.isdigit():
            token.type = INTEGER
            token.value = int(token.value)
        elif utils.isfloat(token.value):
            token.type = FLOAT
            token.value = float(token.value)
        elif token.value in keywords:
            token.type = KEYWORD
        elif utils.valid_name(token.value):
            token.type = VARIABLE
        elif token.value[0] in tuple('\'"'):
            token.type = STRING
            token.value = token.value[1:-1]
        else:
            raise TypeError(f'bad value: {token.value}')

        if token.type == KEYWORD:
            token.value = keywords[token.value]

    return tokens


def parse_unary(tokens):
    unary_tokens = parse_unary_signs(tokens)

    for unary_token in filter(lambda _token: _token.type == PARENTHESIS, unary_tokens):
        unary_token.value = parse_unary(unary_token.value)

    return unary_tokens


def parse_unary_signs(tokens):
    final_tokens = []
    unary_signs = []

    for index, token in enumerate(tokens):
        if token.type == OPERATOR and (len(final_tokens) == 0 or final_tokens[-1].type == OPERATOR):
            unary_signs.append(token.value)
            continue
        elif token.type != OPERATOR and unary_signs:
            token.unary = get_final_unary_sign(unary_signs)
            unary_signs = []

        final_tokens.append(token)

    return final_tokens + unary_signs


def process_token(token, context, unary_sign=None):
    if token.type == VARIABLE:
        token.value = context[token.value]
        token.type = pytypes2lotus[type(token.value)]

    return apply_unary_sign(token, to_sign=unary_sign)


def apply_unary_sign(token, to_sign=None):
    if to_sign is None:
        to_sign = token.unary

    token.value = -token.value if to_sign == '-' else token.value

    return token


def get_final_unary_sign(signs):
    if [sign for sign in signs if sign not in tuple('+-')]:  # if some of the unary signs are not + or -
        raise SyntaxError('bad unary operator!')

    reversed_signs = signs[::-1]  # unary sign is parsing from right to left
    previous_sign = reversed_signs[0]

    for sign in reversed_signs[1:]:
        if sign == '-' and previous_sign == '-':
            previous_sign = '+'
        elif sign == '+' and previous_sign == '-':
            previous_sign = '-'
        else:
            previous_sign = sign

    return previous_sign


def parse_parenthesis(tokens):
    cooked_tokens = []
    brace_opener = None
    brace_closer = None
    opened_nested_braces = 0
    temp = []

    for index, token in enumerate(tokens):
        if brace_opener:
            if token.value == brace_opener:
                opened_nested_braces += 1
            elif token.value == brace_closer:
                if opened_nested_braces:
                    temp.append(token)
                    opened_nested_braces -= 1
                    continue

                recursively_parsed_nested_parenthesis = parse_parenthesis(temp)
                cooked_tokens.append(Token(PARENTHESIS, recursively_parsed_nested_parenthesis))
                cooked_tokens[-1].vtype = parenthesis_type_by_opener[brace_opener]
                temp = []
                brace_opener = None

                continue

            temp.append(token)
        elif token.type == OPERATOR and token.value in parenthesis_closers.keys():
            brace_opener = token.value
            brace_closer = parenthesis_closers[brace_opener]
        else:
            cooked_tokens.append(token)

    return parse_unary_signs(cooked_tokens)


def tokenize(raw, ignore_newlines=False):
    lexemes = lex(raw, ignore_newlines=ignore_newlines)
    parsed_lexemes = parse_parenthesis(provide_token_types(lexemes))

    return parsed_lexemes

# pprint(tokenize("""
# if (5 == 5) {
#     print('good', end="right");
#     a = 5;
# }
# """))
# pprint(tokenize("""
# func hello_world(ok, bro) {
#     print('yup');
#     return 5+5-5;
# }
# """))
