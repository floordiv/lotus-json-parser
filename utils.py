from string import punctuation

from oldlotus.core.tokens import NEWLINE, SEMICOLON


bad_name_characters = punctuation.replace('_', '').replace('.', '')
escape_characters = {
    '\\n': '\n',
    '\\r': '\r',
    '\\b': '\b',
    '\\t': '\t',
    '\\a': '\a',
    '\\f': '\f',
    '\\v': '\v',
    '\\\'': '\'',
    '\\\"': '\"'
}


def isfloat(string):
    try:
        float(string)

        return True
    except ValueError:
        return False


def valid_name(string):
    if not string or not isinstance(string, str):
        return False

    return not string[0].isdigit() and all([char not in bad_name_characters for char in string])


def split(text, splitby=' ', skipby='"\'', skipby_close_is_same=True):
    """
    splits by ONE LETTER, but you can set multiple, and it will split it by them
    """

    result = ['']
    in_skipper = False
    prev_skipper_opener = None
    close_skipper = lambda char: char == prev_skipper_opener if skipby_close_is_same else char != prev_skipper_opener

    for letter in text:
        if letter in splitby and not in_skipper:
            result.append('')
        else:
            if letter in skipby:
                if in_skipper and close_skipper(letter):
                    in_skipper = False
                elif not in_skipper:
                    in_skipper = True
                    prev_skipper_opener = letter

            result[-1] += letter

    return result


def parse_func_args(args_tokens):
    args = []
    kwargs = {}

    for tokens in split_tokens(args_tokens, 'COMMA'):
        if len(tokens) == 1:    # this is arg
            args.append(tokens[0].value)
        elif len(tokens) == 3:  # this is kwarg
            var, _, val = tokens
            kwargs[var.value] = val.value
        else:
            raise SyntaxError('SyntaxError: bad argument')

    return args, kwargs


def get_array_ending(string: str, opener: str, closer=None) -> (str, int):
    """
    expr: a string with opener
    opener: single char, which starts an array
    closer: single char, which ends an array

    :returns: in-brace expression, brace-expression-end-index
    """

    openers_opened = 0

    for index, letter in enumerate(string):
        if letter == opener:
            openers_opened += 1
        elif letter == closer:
            openers_opened -= 1

        if openers_opened == 0:
            return string[1:index], index

    return string[1:-1], len(string) - 1


def get_string_ending(string: str) -> (str, int):
    for index, letter in enumerate(string[1:], start=1):
        if letter == string[0] and string[index - 1] != '\\':  # if letter is string opener
            return string[1:index].replace('\\\'', '\''), index

    return string[1:-1].replace('\\\'', '\''), len(string) - 1


def split_tokens(tokens, splitby=(NEWLINE, SEMICOLON)):
    split_tokens_result = [[]]

    for token in tokens:
        if token.type in splitby or token.vtype in splitby:
            split_tokens_result.append([])

        split_tokens_result[-1].append(token)

    return split_tokens_result


def process_escape_characters(raw):
    for raw_character, to_replace in escape_characters.items():
        raw = raw.replace(raw_character, to_replace)

    return raw


def remove_newlines_from_the_end(source):
    if not [True for token in source[-1] if token.type != NEWLINE]:
        source = source[:-1]

    return source


def lstrip(source, strip_by=(NEWLINE,)):
    while source[0].type in strip_by or source[0].vtype in strip_by or source[0].value in strip_by:
        source = source[1:]

    return source
