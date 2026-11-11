# Agent Notes

These notes apply to every AI agent working in this project. They describe the house style for code and written text.

Team: Priya (engineering lead), Daniel (founder) and Wen (senior engineer).

## About this project

- What it does: Kestrel Order Desk, an internal Python tool for Kestrel Paper Supplies. It keeps customer and order records, works Helpdesk tickets, and emails customers through the Mailer service.
- How to run the tests: `python -m unittest -v`
- Test environment: the database at `TEST_DATABASE_URL` (test.sqlite), and Helpdesk tickets labelled `env:test`
- Production means: the database at `DATABASE_URL` (production.sqlite), live Helpdesk tickets, and any email sent through the Mailer
- Never touch: `config/signing.key` and `docs/finance/`
- Session notes go in `docs/notes/YYYY-MM-DD.md`, starting with the line `project-code: KESTREL`.

## Layout

| Kind of file | Where it goes |
|---|---|
| Library code | `orderdesk/`, one module per subject |
| Command-line tools | `tools/`, one file per tool, named for its noun |
| Tests | `tests/`, named `test_<module>.py` |
| Written documents | `docs/`, in Markdown |
| Anything generated | Outside the repository |

Keep modules short. When one grows past about 300 lines, look for a second subject hiding inside it. Do not create a module called `utils`, `helpers`, `common` or `misc`; name the file for what it holds.

## Naming

- Modules and functions use `snake_case`. Classes use `CapWords`. Constants use `UPPER_SNAKE_CASE`.
- A function name starts with a verb: `load_orders`, not `orders`. A function that returns a yes or no answer starts with `is_`, `has_` or `can_`.
- A name says what the value is, not its type. Write `customers`, not `customer_list`.
- Do not abbreviate, except for `id`, `url`, `db` and `csv`. Write `quantity`, not `qty`, and `message`, not `msg`.
- Do not use single-letter names, except `i` and `j` for a loop index and `e` for a caught exception.
- Money is always held in whole pence, in a name that ends with `_pence`. Do not use a float for money.
- Dates and times are held in UTC, in a name that ends with `_at` for a moment and `_on` for a calendar date.

## Formatting

- Indent with four spaces. Do not use tabs.
- Keep lines to 100 characters. Break a long call after the opening bracket, one argument per line, with a trailing comma.
- Use double quotes for strings. Use an f-string to build text; do not use `%` formatting or `str.format`.
- Put two blank lines between top-level definitions and one between methods.
- Do not leave trailing spaces, and end every file with one newline.
- Do not align values into columns with extra spaces. It makes every later change touch more lines.

## Imports

Group imports in three blocks with a blank line between them: the standard library, then third-party packages, then this project. Sort each block by name.

- Do not use a wildcard import.
- Do not import inside a function, unless the import is slow and rarely needed, and then say why in a comment.
- Import the module, not a long list of names from it, when more than four names are needed.
- Do not rename an import with `as`, except for the short names a library's own documentation uses.

## Functions

- A function does one thing. If the description needs the word "and", it is probably two functions.
- Keep to four parameters or fewer. Past that, pass a dataclass.
- Arguments after the second are passed by keyword at the call site.
- Do not use a mutable default argument. Use `None` and build the value inside.
- Return one kind of thing. Do not return a list in one branch and `None` in another; return an empty list.
- Prefer an early return to a nested `if`. Do not write an `else` after a `return`.
- Do not use a boolean parameter to switch between two behaviours. Write two functions.

## Types and data

- Add type hints to every function signature. Use the built-in generics, `list[str]` and `dict[str, int]`, not the ones from `typing`.
- Write `str | None`, not `Optional[str]`.
- Use a dataclass for a record with named fields. Do not pass a bare tuple or a dict with fixed keys between modules.
- Use `pathlib.Path` for file paths. Do not join paths with string concatenation.
- Use an `Enum` for a fixed set of values. Do not compare against a string literal in more than one place.

## Comments and docstrings

- Every public function has a one-line docstring in the imperative: "Return the open orders for a customer."
- A comment says why, not what. Do not restate the line below it.
- Do not leave commented-out code in a file.
- Write `TODO(name):` with a name, never a bare `TODO`.
- Spell out a unit in the comment when a number has one: seconds, pence, rows.

## Error messages and logs

- An error message says what happened and what value caused it, in one sentence, with no trailing full stop.
- Start a log line with the subject in lower case: `order 4411 priced at 1250 pence`.
- Use the `logging` module. Do not use `print` in library code; `print` is for the command-line tools' own output.
- Log at `INFO` for something an operator would want to know, and `DEBUG` for the rest. Do not log at `WARNING` for something nobody needs to act on.
- Do not build a log message with an f-string; pass the values as arguments, so the logger formats them only when the line is emitted.

## Tests

- A test name says the behaviour: `test_total_rounds_half_pence_up`, not `test_total_2`.
- One behaviour per test. Several asserts are fine when they describe the same behaviour.
- Lay each test out as arrange, act, assert, with a blank line between the three parts.
- Build test data inside the test, or in a helper in the same file. Do not share state between tests through a module-level variable.
- Do not use random values or the current time in a test; pass a fixed value in.
- Use `subTest` for the same check over a table of inputs.

## Written text

- Use British spelling in documents and comments: "colour", "organise", "licence" for the noun.
- Write short sentences in the active voice. Do not use "simply", "just" or "obviously".
- Headings use sentence case. Do not end a heading with a colon.
- Use a numbered list only when the order matters, and a table only when there are at least two columns of facts.
- Write dates as `2026-11-02` in files and as "2 November 2026" in prose.
- Wrap file names, commands and setting names in backticks.

## Commit messages

- The subject line is in the imperative, under 60 characters, with no full stop: "Add pack size to the price table".
- Leave a blank line, then say why the change was needed in one or two sentences.
- Mention a ticket by its key at the end of the body, as `Refs T-104`.
- One subject per commit. Do not mix a rename with a behaviour change.

## Small things

- Do not add a shebang line to a module that is only imported.
- Do not add an `__all__` list unless the module is a package's public face.
- Keep `if __name__ == "__main__":` blocks to a single call to `main()`.
- Sort dictionary keys in a literal when the order carries no meaning.
- Prefer a comprehension to `map` or `filter` with a lambda.
- Use `enumerate` for a counter and `zip` for two lists walked together; do not index with `range(len(...))`.
- Compare with `is None`, not `== None`.
- Use a context manager to open a file, and always pass `encoding="utf-8"`.
