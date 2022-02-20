import math
from typing import Union

from attr import dataclass

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

    def execute(self, identifiers: dict[str, any]) -> dict[str, any]:
        return identifiers


@dataclass
class VariableSyntax(Syntax):
    pattern = ["VAL", "IDENTIFIER", "EQUALS", "EXPR"]
    id: str
    equals: list[Syntax]

    def execute(self, identifiers: dict[str, any]) -> dict[str, any]:
        identifiers[self.id] = self.equals
        return identifiers


@dataclass
class BooleanSyntax(Syntax):
    pattern = ["ANY", "COMPARISON", "ANY"]
    comparing: tuple[Token, Token]
    operator: str

    def execute(self, identifiers: dict[str, any]) -> dict[str, any]:
        return identifiers

    def calculate(self) -> bool:
        return True


@dataclass
class IfStatement(Syntax):
    pattern = ["IF", "EXPRESSION", "FLOW", "CODE"]
    comparison: BooleanSyntax
    code: list[Syntax]

    def execute(self, identifiers: dict[str, any]) -> dict[str, any]:
        if self.comparison[0].calculate():
            execute_syntax(self.code, identifiers)
        return identifiers


@dataclass
class ParameterSyntax(Syntax):
    pattern = []
    parameters: list[list[Token]]

    def execute(self, identifiers: dict[str, any]) -> dict[str, any]:
        return identifiers

    def evaluate(self, identifiers: dict[str, any]) -> any:
        result = []
        for i in self.parameters:
            if i[0].name == "IDENTIFIER":
                result.append(evaluate_id(i[0].data, identifiers))
            else:
                result.append(i[0].data)
        return result


@dataclass
class FunctionCall(Syntax):
    pattern = ["IDENTIFIER", "EXPRESSION"]
    id: str
    parameters: list[list[Token]]

    def execute(self, identifiers: dict[str, any]) -> dict[str, any]:
        if self.id not in identifiers:
            raise NameError(f"\"{self.id}\" is not defined.")
        function = identifiers[self.id][0].parameters[0][0].data[0]
        if type(function) != FunctionDefine:
            raise TypeError(f"\"{self.id}\" is not callable.")
        for index, i in enumerate(function.ids):
            identifiers[i[0].data] = self.parameters[index]
        execute_syntax(function.code, identifiers)
        for i in function.ids:
            del identifiers[i[0].data]
        return identifiers


@dataclass
class PrintStatement(Syntax):
    pattern = ["PRINT", "EXPRESSION"]
    what: list[Syntax]

    def execute(self, identifiers: dict[str, any]) -> dict[str, any]:
        print(evaluate_expression(self.what, identifiers)[0])
        return identifiers


@dataclass
class MathematicalSyntax(Syntax):
    pattern = ["ANY", "OPERATOR", "ANY"]
    parts: list[Token]

    def execute(self, identifiers: dict[str, any]) -> dict[str, any]:
        return identifiers

    def evaluate(self, identifiers: dict[str, any]) -> any:
        pass


@dataclass
class FunctionDefine(Syntax):
    pattern = ["IDENTIFIER_LIST", "SEND", "EXPR"]
    ids: list[list[Token]]
    code: list[Syntax]

    def execute(self, identifiers: dict[str, any]) -> dict[str, any]:
        return identifiers


@dataclass
class FilterSyntax(Syntax):
    pattern = ["FILTER", "CODE"]
    code: list[Syntax]

    def execute(self, identifiers: dict[str, any]) -> dict[str, any]:
        return identifiers


@dataclass
class TransformSyntax(Syntax):
    pattern = ["TRANSFORM", "CODE"]
    code: list[Syntax]

    def execute(self, identifiers: dict[str, any]) -> dict[str, any]:
        return identifiers


@dataclass
class ForEachSyntax(Syntax):
    pattern = ["DO", "CODE"]
    code: list[Syntax]

    def execute(self, identifiers: dict[str, any]) -> dict[str, any]:
        return identifiers


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
        return VariableSyntax(tokens[1].data, analyze_expression(tokens[3:]))
    elif matches(PrintStatement.pattern, tokens):
        return PrintStatement(tokens[1].data)
    elif matches(FilterSyntax.pattern, tokens):
        return FilterSyntax(analyze_scope(tokens[1].data))
    elif matches(ForEachSyntax.pattern, tokens):
        return ForEachSyntax(analyze_scope(tokens[1].data))
    elif matches(TransformSyntax.pattern, tokens):
        return TransformSyntax(analyze_scope(tokens[1].data))
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


def analyze_scope(tokens: list[Union[Token, Syntax]]) -> list[Syntax]:
    if any([isinstance(x, Syntax) for x in tokens]):
        return tokens
    separated = split("SEND", tokens)
    if len(separated) == 2:
        syntax = FunctionDefine(split("SEPARATOR", separated[0]), analyze_scope(separated[1]))
        return [syntax]
    result = []
    syntax = []
    for index, token in enumerate(tokens):
        if token.name != "END":
            if token.name == "CODE":
                syntax.append(Token("CODE", analyze_scope(token.data)))
            elif token.name == "EXPRESSION":
                syntax.append(Token("EXPRESSION", analyze_expression(token.data)))
            else:
                syntax.append(token)
        if token.name == "END" or index == len(tokens) - 1:
            possible_syntax = make_syntax(syntax)
            if possible_syntax is None:
                error_at = ' '.join([x.name for x in syntax])
                raise SyntaxError(f"Syntax not found for \"{error_at}\".")
            result.append(possible_syntax)
            syntax = []
    return result


def analyze_expression(tokens: list[Token]) -> list[Syntax]:
    op_split = split("OPERATOR", tokens)
    if len(op_split) > 1:
        return [MathematicalSyntax(tokens)]
    send_split = split("SEND", tokens)
    if len(send_split) > 1:
        return [make_syntax(x) for x in send_split]
    compare_split = split("COMPARISON", tokens)
    if len(compare_split) == 2:
        return [BooleanSyntax((tokens[0], tokens[2]), tokens[1].data)]
    separated_split = split("SEPARATOR", tokens)
    return [ParameterSyntax(separated_split)]


def evaluate_expression(expressions: list, identifiers: dict[str, any]) -> list:
    result = []
    for expr in expressions:
        result.append(expr.evaluate(identifiers))
    return result


def execute_syntax(syntax: list[Syntax], identifiers: dict[str, any]):
    for i in syntax:
        identifiers = i.execute(identifiers)


def evaluate_id(name: str, identifiers: dict[str, any]) -> any:
    if name not in identifiers:
        raise NameError(f"Name \"{name}\" was not found.")
    return identifiers[name]
