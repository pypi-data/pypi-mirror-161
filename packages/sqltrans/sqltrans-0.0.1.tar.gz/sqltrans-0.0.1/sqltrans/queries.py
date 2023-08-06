"""
This module consist of predefined parsed sql statement queries.
"""
from sqltrans.search import Search
import sqlparse.sql as s
import sqlparse.tokens as t


def get_function_name(parsed: s.Function) -> str:
    # Todo check for Function type
    name = Search(parsed).get(sql_class=s.Identifier, levels=1).first().result().one().value
    return name


def get_function_params(parsed: s.TypeParsed) -> list[s.TypeParsed]:
    params = Search(parsed) \
        .get(sql_class=s.Parenthesis).first() \
        .get(sql_class=s.IdentifierList).first() \
        .exclude(ttype=(t.Whitespace, t.Punctuation), levels=1) \
        .result().as_list()
    return params
