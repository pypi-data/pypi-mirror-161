# Sqltrans

Sqltrans is a package containing tools and framework to search through parsed sql statement tree and transform it. 
Main purpose is to create environment for defining sql dialect transformation rules.
Some sql translation rules may be added to the project in the future - 
there are already few of them for demonstration purposes.

Sqltrans is based on [modified](https://github.com/m-matelski/msqlparse) version 
of [sqlparse](https://github.com/andialbrecht/sqlparse) package.

## Requirements
* Python >= 3.8

## Installation
* `pip install sqltrans`

## Examples

### Searching
Sqltrans provides fluent interface for searching through sql statement parsed tree.

```python
import sqlparse
import sqlparse.sql as s
import sqlparse.tokens as t

from sqltrans.search import Search

sql = "select cast(substring(tab.field, 1, 4) as int) from tab"
parsed = sqlparse.parse(sql)[0]

cast_call = Search(parsed).get(sql_class=s.Function, pattern='cast.*').result().one()
print(cast_call)
# >>> cast(substring(tab.field, 1, 4) as int)

substring_params = Search(parsed)
.get(sql_class=s.Function, pattern='substring.*').first()
.get(sql_class=s.IdentifierList).first()
.exclude(ttype=(t.Punctuation, t.Whitespace), levels=1)
.result().as_list()
# >>> [<Identifier 'tab.fi...' at 0x22EBBD73610>, <Name 'tab' at 0x22EBBD9B280>, <Name 'field' at 0x22EBBD9B340>, <Integer '1' at 0x22EBBD9B460>, <Integer '4' at 0x22EBBD9B580>]
```

Parsed search is performed in a recursive manner. Entry point for a Search can be parsed sql statement, or Iterable of parsed statements.
`get` call returns all groups or tokens meeting the condition. Using multiple `get` statements can be used
to express more complex condition. `exclude` is opposite to `get`.

`levels` parameter in `get` / `exclude` calls defines how deep the recursion should be. Search step can be restricted
to be performed only on a top level by settings `levels=1`. If `levels` is not specified then full recursion search is performed.

Placing `first` and `last` methods after every `get` and `exclude` ensures, that next search step will be performed over
Single parsed statement, instead of Iterable of statements - it is important to note that in case of single parsed statement
next search step will start from children tokens of parsed statement, but in case of iterable of statements it will start from statement itself
(`for i in parsed.tokens` vs `for i in [parsed]`). It must be implicitly declared using `first` and `last`, that
We want to work on a single parsed element (even if `get` returns only one element).

Use `search` method to retrieve search result. Result can be returned as `one()`, or `as_list()`.
`one()` will raise an exception if number of search results is different from 1.

### Predefined queries

Predefined queries are helper functions which utilize Search objects.

```python
# ... continuing previous example

from sqltrans.queries import get_function_params, get_function_name

substring_func = Search(parsed).get(sql_class=s.Function, pattern='substring.*').result().one()
substring_params = get_function_params(substring_func)
print(substring_params)
# >>> [<Identifier 'tab.fi...' at 0x19DB83436F0>, <Integer '1' at 0x19DB836B460>, <Integer '4' at 0x19DB836B580>]

functions = [get_function_name(i) for i in Search(parsed).get(sql_class=s.Function).result().as_list()]
print(functions)
# >>> ['cast', 'substring']
```

### Translation

* extending translation (adding new rules)
* adding translation (registering, overwriting)
* creating rules
* reusing rules
* composite translation