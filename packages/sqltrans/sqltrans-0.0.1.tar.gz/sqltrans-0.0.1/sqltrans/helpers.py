from sqlparse import sql as s
from sqlparse import tokens as t
from sqlparse.lexer import Lexer
from sqlparse.tokens import TokenType

from sqltrans.search import Search, get_token_idx


def build_tokens(tokens: list[s.TypeParsed | str], lexer: Lexer | None = None,
                 encoding: str | None = None, translate_tokens=False) -> s.TokenList:
    new_tokens = []
    for token in tokens:
        if isinstance(token, str):
            if lexer:
                new_token = [s.Token(i[0], i[1]) for i in lexer.get_tokens(token, encoding)]
            else:
                new_token = [s.Token(None, token)]
            new_tokens.extend(new_token)
        elif isinstance(token, s.TypeParsed):
            if translate_tokens:
                new_token = [s.Token(i[0], i[1]) for i in lexer.get_tokens(str(token), encoding)]
            else:
                new_token = [token]
            new_tokens.extend(new_token)
        else:
            raise ValueError(f'Invalid type of token: {type(token)}, expected: str, Token.')
    token_list = s.TokenList(tokens=new_tokens)
    return token_list


# TODO consider removing/ slicing/ substituting
def replace_token(old: s.Token, new: s.Token):
    idx = get_token_idx(old)
    parent = old.parent
    parent.tokens[idx] = new
    new.parent = parent
