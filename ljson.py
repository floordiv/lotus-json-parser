from pprint import pprint

import lotus.core.lexer
from lotus.core.operators import TOKENS
from lotus.core.tokentypes import (BRACES, SQUARE_BRACES,
                                   VARIABLE, pytypes2lotus)


class Parser:
    def __init__(self, string_json, context=None):
        if context is None:
            context = {'true': True, 'false': False, 'null': None}

        self.json = string_json
        self.context = context

        self.token_types2parsers = {
                BRACES: self.parse_dict,
                SQUARE_BRACES: self.parse_list,
        }

    def parse(self, context=None):
        if context is not None:
            self.context = context

        main_lexema = lotus.core.lexer.tokenize(self.json, ignore_newlines=True)[0]

        if main_lexema.vtype not in self.token_types2parsers:
            raise Exception('unknown type: ' + str(main_lexema.vtype))

        return self.token_types2parsers[main_lexema.vtype](main_lexema)

    def get_rid_of_commas(self, tokens):
        return [token for token in tokens if token.vtype != TOKENS[',']]

    def key_value_from_duo(self, list_of_3_elements):
        if not list_of_3_elements:
            return

        key, _, value = list_of_3_elements

        return key, value

    def parse_dict(self, dict_parenthesis):
        result = {}
        values = self.get_rid_of_commas(dict_parenthesis.value)

        while values:
            key, value = self.key_value_from_duo(values[:3])
            key, value = self.process_token(key).value, self.process_token(value)

            if not isinstance(value, (list, dict)):
                value = value.value

            result[key] = value
            values = values[3:]

        return result

    def parse_list(self, list_parenthesis):
        tokens = self.get_rid_of_commas(list_parenthesis.value)

        return [self.process_token(token).value for token in tokens]

    def process_token(self, token):
        if token.type == VARIABLE:
            token.value = self.context[token.value]
            token.type = pytypes2lotus[type(token.value)]
        elif token.vtype in self.token_types2parsers:
            token = self.token_types2parsers[token.vtype](token)

        return token


some_json = """
{
 "some key": "some value",
 "another": 5,
  5: [6, 7],
  "nested dict": {
                "ok": "right"
                 }
}
"""
parser = Parser(some_json)
pprint(parser.parse())
