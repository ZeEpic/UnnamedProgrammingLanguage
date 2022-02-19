from typing import Union

import syntaxes
from lexer import Token
from syntaxes import Syntax


def analyze_expression(tokens: list[Token]) -> list[Syntax]:
    op_split = syntaxes.split("OPERATOR", tokens)
    if len(op_split) > 1:
        return [syntaxes.MathematicalSyntax(tokens)]
    send_split = syntaxes.split("SEND", tokens)
    if len(send_split) > 1:
        return [syntaxes.make_syntax(x) for x in send_split]
    compare_split = syntaxes.split("COMPARISON", tokens)
    if len(compare_split) == 2:
        return [syntaxes.BooleanSyntax((tokens[0], tokens[2]), tokens[1].data)]
    separated_split = syntaxes.split("SEPARATOR", tokens)
    return [syntaxes.ParameterSyntax(separated_split)]


def analyze_scope(tokens: list[Union[Token, Syntax]]) -> list[Syntax]:
    if any([isinstance(x, Syntax) for x in tokens]):
        return tokens
    separated = syntaxes.split("SEND", tokens)
    if len(separated) == 2:
        syntax = syntaxes.FunctionDefine(syntaxes.split("SEPARATOR", separated[0]), analyze_scope(separated[1]))
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
            possible_syntax = syntaxes.make_syntax(syntax)
            if possible_syntax is None:
                error_at = ' '.join([x.name for x in syntax])
                raise SyntaxError(f"Syntax not found for \"{error_at}\".")
            result.append(possible_syntax)
            syntax = []
    return result
