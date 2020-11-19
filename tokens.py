from typing import List

from lotus.core.priorities import MINIMAL, MAXIMAL
from lotus.core.tokentypes import PARENTHESIS, FCALL


class Token:
    def __init__(self, token_type, value, priority=MINIMAL):
        self.type = token_type
        self.vtype = None
        self.value = value
        self.priority = priority

        self.unary = '+'
        self.processed = False

    def __str__(self):
        token_type = self.type

        if self.vtype:
            token_type += ':' + self.vtype

        return f'{token_type}({self.unary if self.unary == "-" else ""}{repr(self.value)})'

    __repr__ = __str__


class Parenthesis:
    def __init__(self, tokens=()):
        self.tokens = self.value = list(tokens)

        self.type = PARENTHESIS
        self.priority = MAXIMAL

        self.unary = '+'
        self.processed = False

    def __str__(self):
        return f'{self.unary if self.unary == "-" else ""}{self.type}({str(self.tokens)[1:-1]})'

    __repr__ = __str__


class Function:
    def __init__(self, name, args, kwargs, body, context, executor):
        self.name = name
        self.args, self.kwargs = args, kwargs
        self.body = body
        self.context = context
        self.executor = executor

        self.type = FCALL
        self.priority = MAXIMAL
        self.unary = '+'
        self.processed = False

    def __call__(self, *args, **kwargs):
        func_args_len, given_args_len = len(self.args), len(args)

        if func_args_len != given_args_len:
            raise TypeError(f'{self.name}(): {func_args_len} args expected, got {given_args_len} instead')

        for arg_name, given_arg_value in zip(self.args, args):
            self.context[arg_name] = given_arg_value

        for kw_var, kw_val in {**self.kwargs, **kwargs}.items():
            if kw_var not in self.kwargs:
                raise TypeError(f'{self.name}(): unexpected kwarg: {kw_var}')

            self.context[kw_var] = kw_val

        return self.executor(self.body)

    def __str__(self):
        return f'{self.type}(args={self.args}, kwargs={self.kwargs})'

    __repr__ = __str__


class Branch:
    def __init__(self, if_stmnt, *elif_stmnt, else_stmnt=None):
        self.if_stmnt: BranchLeaf = if_stmnt
        self.elif_stmnt: List[BranchLeaf] = list(elif_stmnt)
        self.else_stmnt: BranchLeaf = else_stmnt

    def get_branch(self, math_executor, context):
        for branch in [self.if_stmnt] + self.elif_stmnt:
            if math_executor(branch.expr, context=context):
                return branch

        return self.else_stmnt


class BranchLeaf:
    def __init__(self, expr, body):
        self.expr = expr
        self.body = body
