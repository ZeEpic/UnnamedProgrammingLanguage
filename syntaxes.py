import math
from typing import Union

from attr import dataclass

import syntax_analyzer
from lexer import Token


def does_token_match(token: str, tokens: list[Token], index: int) -> bool:
    if 0 <= index < len(tokens):
        if tokens[index].name == token:
            return True
    return False


def matches(pattern: list[str], tokens: list[Token]) -> bool:
    for index, x in enumerate(pattern):
        if x == "ANY":
            continue
        elif x == "EXPR":
            return True
        elif not does_token_match(x, tokens, index):
            return False
    return True


@dataclass
class Syntax:
    pattern = []


@dataclass
class VariableSyntax(Syntax):
    pattern = ["VAL", "IDENTIFIER", "EQUALS", "EXPR"]
    id: str
    equals: list[Syntax]


@dataclass
class BooleanSyntax(Syntax):
    pattern = ["ANY", "COMPARISON", "ANY"]
    comparing: tuple[Token, Token]
    operator: str


@dataclass
class IfStatement(Syntax):
    pattern = ["IF", "EXPRESSION", "FLOW", "CODE"]
    comparison: BooleanSyntax
    code: list[Token]


@dataclass
class ParameterSyntax(Syntax):
    pattern = []
    parameters: list[list[Token]]


@dataclass
class FunctionCall(Syntax):
    pattern = ["IDENTIFIER", "EXPRESSION"]
    id: str
    parameters: list[list[Token]]


@dataclass
class PrintStatement(Syntax):
    pattern = ["PRINT", "EXPRESSION"]
    what: list[Token]


@dataclass
class MathematicalSyntax(Syntax):
    pattern = ["ANY", "OPERATOR", "ANY"]
    parts: list[Token]


@dataclass
class FunctionDefine(Syntax):
    pattern = ["IDENTIFIER_LIST", "SEND", "EXPR"]
    ids: list[list[Token]]
    code: list[Syntax]


@dataclass
class FilterSyntax(Syntax):
    pattern = ["FILTER", "CODE"]
    code: list[Syntax]


@dataclass
class TransformSyntax(Syntax):
    pattern = ["TRANSFORM", "CODE"]
    code: list[Syntax]


@dataclass
class ForEachSyntax(Syntax):
    pattern = ["DO", "CODE"]
    code: list[Syntax]


def tokens_till(till: str, tokens: list[Token]) -> tuple[list[Token], int]:
    result = []
    for index, token in enumerate(tokens):
        if token.name == till:
            return result, index
        result.append(token)
    return result, len(tokens)


def split(deliminator: str, tokens: list[Token]) -> list[list[Token]]:
    result = []
    part = []
    for token in tokens:
        if token.name == deliminator:
            result.append(part)
            part = []
        else:
            part.append(token)
    result.append(part)
    return result


def is_math(tokens: list[Token]) -> bool:
    separated = split("OPERATOR", tokens)
    return len(separated) == math.ceil(len(tokens) / 2)


def make_syntax(tokens: list[Token]) -> Union[Syntax, None]:
    if matches(VariableSyntax.pattern, tokens):
        return VariableSyntax(tokens[1].data, syntax_analyzer.analyze_expression(tokens[3:]))
    elif matches(PrintStatement.pattern, tokens):
        return PrintStatement(tokens[1].data)
    elif matches(FilterSyntax.pattern, tokens):
        return FilterSyntax(syntax_analyzer.analyze_scope(tokens[1].data))
    elif matches(ForEachSyntax.pattern, tokens):
        return ForEachSyntax(syntax_analyzer.analyze_scope(tokens[1].data))
    elif matches(TransformSyntax.pattern, tokens):
        return TransformSyntax(syntax_analyzer.analyze_scope(tokens[1].data))
    elif matches(FunctionCall.pattern, tokens):
        return FunctionCall(tokens[0].data, tokens[1].data[0].parameters)
    elif matches(IfStatement.pattern, tokens):
        boolean_expr = tokens[1].data
        if len(boolean_expr) == 0:
            raise SyntaxError(f"You must specify a boolean expression for an if statement ({tokens[1]}).")
        if not isinstance(boolean_expr[0], BooleanSyntax):
            raise SyntaxError(f"You may only use boolean expressions in an if statement ({tokens[1].data}).")
        return IfStatement(boolean_expr, tokens[3].data)
    elif matches(BooleanSyntax.pattern, tokens):
        return BooleanSyntax((tokens[0], tokens[2]), tokens[1].data)
    elif is_math(tokens):
        return MathematicalSyntax(tokens)
    else:
        return None
