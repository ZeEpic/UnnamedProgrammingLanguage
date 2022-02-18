import syntaxes
from lexer import Token
from syntaxes import Syntax


def analyze_scope(tokens: list[Token]) -> list[Syntax]:
    result = []
    syntax = []
    for index, token in enumerate(tokens):
        if token.name == "END" or index == len(tokens) - 1:
            possible_syntax = syntaxes.make_syntax(syntax)
            if possible_syntax is None:
                error_at = ' '.join([x.name for x in syntax])
                raise SyntaxError(f"Syntax not found for \"{error_at}\".")
            print(possible_syntax)
            result.append(possible_syntax)
            syntax[:] = []
            continue
        syntax.append(token)
    return result
