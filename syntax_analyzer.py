import syntaxes
from lexer import Token
from syntaxes import Syntax


def analyze_expression(tokens: list[Token]) -> list[Syntax]:
    op_split = syntaxes.split("OPERATOR", tokens)
    if len(op_split) > 1:
        print([syntaxes.MathematicalSyntax(tokens)])
        return [syntaxes.MathematicalSyntax(tokens)]
    print([syntaxes.ParameterSyntax(syntaxes.split("SEPARATOR", tokens))])
    return [syntaxes.ParameterSyntax(syntaxes.split("SEPARATOR", tokens))]


def analyze_scope(tokens: list[Token]) -> list[Syntax]:
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
