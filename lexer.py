import re
from typing import Union

from attr import dataclass


@dataclass
class Token:
    name: str
    data: Union[str, list]


def find_end_scope(raw: str, char: str, other_char: str, start: int) -> int:
    count = 0
    for index, i in enumerate(raw[start:]):
        if i == other_char:
            count -= 1
            if count == 0:
                return index
        elif i == char:
            count += 1
    return start


def parse_token(token: str, tokens: dict[str, str]) -> Union[Token, None]:
    if token == '':
        return None
    if token in tokens:
        return Token(tokens[token], token)
    elif bool(re.fullmatch(r"(\d+(\.\d+)?)\.\.\.(\d+(\.\d+)?)", token)):
        return Token("RANGE", [int(x) for x in token.split("...")])
    elif bool(re.fullmatch(r"\d+(\.\d+)?", token)):
        return Token("NUMBER", token)
    elif bool(re.fullmatch(r"[a-zA-Z0-9_]*", token)):
        return Token("IDENTIFIER", token)
    else:
        raise Exception(f"Error at '{token}'!")


def find_parens(raw: str, open_bracket: str, close_bracket: str) -> list[tuple]:
    pairs = []
    paren_stack = []

    for i, c in enumerate(raw):
        if c == open_bracket:
            paren_stack.append(i)
        elif c == close_bracket:
            if len(paren_stack) == 0:
                raise IndexError("No matching closing parens at: " + str(i))
            pairs.append((paren_stack.pop(), i))

    if len(paren_stack) > 0:
        raise IndexError("No matching opening parens at: " + str(paren_stack.pop()))

    return pairs


def get_scope_token(raw: str, index: int, token_map: dict[str, str]) -> tuple[int, Token]:
    opposite = ')' if raw[index] == '(' else '}'

    parentheses = find_parens(raw, raw[index], opposite)
    parentheses.sort(key=lambda x: x[0])
    parentheses = [x for x in parentheses if x[1] > index]
    end = parentheses[0][1]
    tokens = parse_scope(raw[index+1:end], token_map)
    if raw[index] == "{":
        return end, Token("CODE", tokens)
    else:
        return end, Token("EXPRESSION", tokens)


def parse_scope(raw: str, token_map: dict[str, str]) -> list[Token]:
    raw += " "
    tokens = []
    string = ""
    do_string = False
    token = ""
    pause_till = -1
    for index, i in enumerate(raw):
        if pause_till > -1:
            if pause_till == index:
                pause_till = -1
            else:
                continue
        elif i == "\"":
            if do_string:
                tokens.append(Token("STRING", string))
                do_string = False
            else:
                do_string = True
            string = ""
            continue
        elif do_string:
            string += i
            continue
        if i in [" ", "(", "{", ")", "}", "\n", ";", ","]:
            parsed = parse_token(token, token_map)
            if parsed is not None:
                tokens.append(parsed)
            if i == ';':
                tokens.append(Token("END", ';'))
            elif i == ',':
                tokens.append(Token("SEPARATOR", ','))
            token = ""
        else:
            token += i

        if i == '(' or i == '{':
            result = get_scope_token(raw, index, token_map)
            if result[0] != index and result[0] != raw[index+1]:
                pause_till = result[0]
            else:
                pause_till = -1
            tokens.append(result[1])
    return tokens
