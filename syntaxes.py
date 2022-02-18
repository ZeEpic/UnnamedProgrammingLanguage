from typing import Union

from attr import dataclass

from lexer import Token


def matches(pattern: list[str], tokens: list[Token]) -> bool:
    for index, x in enumerate(pattern):
        if x == "ANY":
            continue
        elif x == "EXPR":
            return True
        elif x != tokens[index].name:
            return False
    return True


@dataclass
class Syntax:
    pattern = []


@dataclass
class VariableSyntax(Syntax):
    pattern = ["VAL", "IDENTIFIER", "EQUALS", "EXPR"]
    id: str
    equals: list[Token]


@dataclass
class IfStatement(Syntax):
    pattern = ["IF", "ANY", "OPERATOR", "ANY", "FLOW", "CODE"]
    comparing: list[Token]
    operator: Token
    code: list[Token]


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
class FunctionDefine(Syntax):
    pattern = ["IDENTIFIER_LIST", "SEND", "EXPR"]
    ids: list[str]
    code: list[Token]


syntaxes: list[type] = [VariableSyntax, IfStatement, FunctionCall, PrintStatement, FunctionDefine]


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
            part[:] = []
        else:
            part.append(token)
    return result


def make_syntax(tokens: list[Token]) -> Union[Syntax, None]:
    till_send = tokens_till("SEND", tokens)
    if matches(FunctionDefine.pattern, tokens):
        return FunctionDefine([x.name for x in till_send[0]], tokens[till_send[1] + 1:])
    elif matches(VariableSyntax.pattern, tokens):
        return VariableSyntax(tokens[1].data, tokens[3:])
    elif matches(FunctionCall.pattern, tokens):
        return FunctionCall(tokens[0].data, split("SEPARATOR", tokens[1:]))
    return None
