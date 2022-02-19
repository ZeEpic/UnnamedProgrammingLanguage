from lexer import parse_scope
from syntax_analyzer import analyze_scope
from syntaxes import Syntax


def get_file(path: str) -> str:
    with open(path, "r") as f:
        return f.read()


code_path = "code.code"
token_path = "map.tokens"
parsed_token_map = [(x.split(": ")[0], x.split(": ")[1]) for x in get_file(token_path).splitlines()]
token_map = dict(parsed_token_map)


def interpret(raw: str) -> list[Syntax]:
    tokens = parse_scope(raw, token_map)
    syntax = analyze_scope(tokens[0].data)
    return syntax


def main() -> None:
    code = get_file(code_path).replace("\t", "")
    print(interpret(code))
    while True:
        code = input(">>> ")
        print(interpret(code))


if __name__ == '__main__':
    main()
