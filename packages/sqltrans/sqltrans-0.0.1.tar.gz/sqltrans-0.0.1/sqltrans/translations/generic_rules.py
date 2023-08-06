import sqlparse.sql as s

from sqltrans.helpers import build_tokens, replace_token
from sqltrans.queries import get_function_name, get_function_params
from sqltrans.search import match_string
from sqltrans.translate import Translation


def debug_rule(parsed: s.TypeParsed) -> None:
    print(f'doing rule for: {parsed}')


def remove_parenthesis_for_function(func_names: list[str]):
    def remove_parenthesis(parsed: s.TypeParsed, translation: Translation) -> None:
        if isinstance(parsed, s.Function) \
                and match_string(get_function_name(parsed), func_names) \
                and not get_function_params(parsed):
            func_name = get_function_name(parsed)
            new_token = build_tokens(tokens=[func_name], lexer=translation.tgt_parser.get_lexer())
            replace_token(parsed, new_token)

    return remove_parenthesis


# def replace_function_name substring to substr