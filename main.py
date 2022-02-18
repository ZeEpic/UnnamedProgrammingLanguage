from lexer import parse_scope, Token
from syntax_analyzer import analyze_scope


def get_file(path: str) -> str:
    with open(path, "r") as f:
        return f.read()


code_path = "code.code"
token_path = "map.tokens"
parsed_token_map = [(x.split(": ")[0], x.split(": ")[1]) for x in get_file(token_path).splitlines()]
token_map = dict(parsed_token_map)


def main() -> None:
    code = get_file(code_path).replace("\t", "")
    print(token_map)
    tokens = parse_scope(code, token_map)
    for i in tokens[0].data:
        print(i)
    syntax = analyze_scope(tokens[0].data)
    print(syntax)


if __name__ == '__main__':
    main()
