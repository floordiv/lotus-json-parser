from typing import List
from collections.abc import Iterable

from lotus.core.tokentypes import (NEWLINE, FUNC_ASSIGN, VAR_ASSIGN,
                                   FUNC_KEYWORD, PARENTHESIS, BRACES,
                                   VARIABLE, OPERATOR, ANY, FOR_LOOP,
                                   FOR_KEYWORD, IF_STMNT, ELIF_STMNT,
                                   ELSE_STMNT, IF_KEYWORD, ELIF_KEYWORD,
                                   ELSE_KEYWORD)
from lotus.core.operators import TOKENS


class MatchToken:
    def __init__(self, *match_token_types, vtypes=()):
        if not isinstance(vtypes, Iterable):
            vtypes = (vtypes,)

        self.types = match_token_types
        self.vtypes = vtypes

    def match(self, another_token):
        if ANY in self.types or another_token.type in self.types:
            return True

        return another_token.vtype in self.vtypes


constructions = {
    FUNC_ASSIGN: (MatchToken(FUNC_KEYWORD), MatchToken(VARIABLE), MatchToken(PARENTHESIS), MatchToken(BRACES)),
    VAR_ASSIGN:  (MatchToken(VARIABLE), MatchToken(OPERATOR, vtypes=TOKENS['=']), MatchToken(ANY)),
    FOR_LOOP:    (MatchToken(FOR_KEYWORD), MatchToken(PARENTHESIS), MatchToken(BRACES)),
    IF_STMNT:    (MatchToken(IF_KEYWORD), MatchToken(PARENTHESIS), MatchToken(BRACES)),
    ELIF_STMNT:  (MatchToken(ELIF_KEYWORD), MatchToken(PARENTHESIS), MatchToken(BRACES)),
    ELSE_STMNT:  (MatchToken(ELSE_KEYWORD), MatchToken(BRACES))
}


def match(original, match_list: List[MatchToken], ignore=()):
    current_match_token_index = 0
    matched = []

    for token in original:
        if token.type in ignore or token.vtype in ignore:
            continue

        if not match_list[current_match_token_index].match(token):
            return False

        matched.append(token)

    if not matched:
        # if all the tokens were ignored
        return False

    return matched


def startswith(tokens, constructs):
    for construction_name, construction_match_tokens in constructs.items():
        match_result = match(tokens[:len(construction_match_tokens)], construction_match_tokens, ignore=(NEWLINE,))

        if match_result:
            return construction_name, match_result

    return None, False


def detect_type(tokens):
    ...
