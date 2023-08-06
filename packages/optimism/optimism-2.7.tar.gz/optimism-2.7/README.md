# `optimism`

A very small & simple unit-testing framework designed to provide all the
basic necessities to beginner programmers as simply as possible.

Designed by Peter Mawhorter.


## Dependencies

Works on Python versions 3.7 and up, with 3.9+ recommended.


## Installing

To install from PyPI, run the following command on the command-line:

```sh
python3 -m pip install optimism
```

Once it's installed, you can run the tests using:

```sh
pytest --doctest-modules optimism.py
pytest test_examples.py
```

## Usage

Use the `testFunction`, `testFunctionMaybe`, `testFile`, `testBlock`,
and/or `testThisNotebookCell` functions to establish test managers for
specific pieces of code. Then use those managers' `checkCodeContains`
methods to check for the presence/absence of certain code constructs (see
the `ASTRequirement` class) or use the `case` method to establish a test
case w/ specific inputs (one manager can support multiple derived cases
w/ different inputs). Finally, use methods of a test case like
`checkResult` or `checkPrintedLines` to check for specific behavior.

See
[the documentation](https://cs.wellesley.edu/~pmwh/optimism/docs/optimism)
for more details on how to use it and what each function does.

## Changelog

- Version 2.0 creates a less fragile test-case API while streamlining the
  expectations API to focus on values only. `expect` now takes an
  expression and expected value together as two arguments, and `testCase`
  isn't needed. `expectType` was also added to encourage thinking about
  types. These functions are now intended to be used for debugging rather
  than testing. There are new `testFunction`, `testFile`, and `testBlock`
  functions which create `TestManager` objects that have a `case` method
  to derive `TestCase` objects. Those objects have `checkResult` and
  `checkOutputLines` methods, as well as `provideInputs`. Now that we're
  in control of running tests, the old input/output capturing/mocking
  functions are mostly removed (they were quite confusing to students).
  The new test case API does require the use of methods, but as a result
  it can avoid the following:
      1. The use of tuples to specify arguments
      2. The specification of arguments where one argument is an extra
         argument to specify the test case
      3. The use of behind-the-scenes magic to remember the current test
         case (students were confused and it encourages bad mental
         models).
      4. The use of triple-quoted strings for specifying input or output
         (too hard to get newlines right at the start and end).
- Version 2.2.0 changes some method names in the new API to make them
  more explicit: `checkResult` becomes `checkReturnValue`, and
  `checkOutputLines` becomes `checkPrintedLines`.
- Version 2.5.0 adds automatic skipping of checks for a case after one
  check fails, and includes a global setting to apply this at the manager
  level or disable it.
- Version 2.5.1 fixes a bug with comparisons on recursive structures.
- Version 2.6.0 upgrades `checkCustom` to include a 'case' key in the
  dictionary supplied to the checker whose value is the `TestCase` object
  that `checkCustom` was called on. This allows custom checkers to do
  things like access the arguments given to a `FunctionCase`.
- Version 2.6.1 Upgrades `checkCustom` again; it now accepts additional
  arguments to be passed on to the custom checker, which vastly improves
  usability!
- Version 2.6.2 Fixes a bug in the comparison code that would cause
  crashes when comparing dictionaries with different key sets. It also
  adds unit tests for the `compare` function.
- Version 2.6.3 introduces the `checkFileContainsLines` method, and also
  standardizes the difference-finding code and merges it with
  equality-checking code, removing `checkEquality` and introducing
  `findFirstDifference` instead (`compare`) remains but just calls
  `findFirstDifference` internally. Also fixes a bug w/ printing
  tracebacks for come checkers (need to standardize that!). Also adds
  global skip-on-failure and sets that as the default!
- Version 2.6.4 immediately changes `checkFileContainsLines` to
  `checkFileLines` to avoid confusion about whether we're checking
  against the whole file (we are).
- Version 2.6.5 fixes a bug with displaying filenames when a file does
  not exist and `checkFileLines` is used, and also sets the default
  length higher for printing first differing lines in
  `findFirstDifference` since those lines are displayed on their own line
  anyways. Fixes a bug where list differences were not displayed
  correctly, and improves the usefulness of first differences displayed
  for dictionaries w/ different lengths. Also fixes a bug where strings
  which were equivalent modulo trailing whitespace would not be treated
  as equivalent.
- Version 2.6.6 changes from splitlines to split('\\n') in a few places
  because the latter is more robust to extra carriage returns. This
  changes how some error messages look and it means that in some places
  the newline at the end of a file actually counts as having a blank line
  there in terms of output (behavior is mostly unchanged). Also escaped
  carriage returns in displayed strings so they're more visible. From
  this version we do NOT support files that use just '\\r' as a newline
  as easily. But `IGNORE_TRAILING_WHITESPACE` will properly get rid of
  any extra '\\r' before a newline, so when that's on (the default) this
  shouldn't change much. A test of this behavior was added to the file
  test example.
- Version 2.6.7 changes default SKIP_ON_FAILURE back to 'case', since
  'all' makes interactive testing hard, and dedicated test files can call
  `skipChecksAfterFail` at the top. Also fixes an issue where comparing
  printed output correctly is lenient about the presence or absence of a
  final newline, but comparing file contents didn't do that. This change
  means that extra blank lines (including lines with whitespace on them)
  are ignored when comparing strings and IGNORE_TRAILING_WHITESPACE is
  on, and even when IGNORE_TRAILING_WHITESPACE is off, the presence or
  absence of a final newline in a file or in printed output will be
  copied over to a multi-line expectation (since otherwise there's no way
  to specify the lack of a final newline when giving multiple string
  arguments to `checkPrintedLines` or `checkFileLines`).
- Version 2.7 introduces the `ASTRequirement` class and subclasses, along
  with the `TestManager.checkCodeContains` method for applying them. It
  reorganizes things a bit so that `Trial` is now a super-class of both
  `TestCase` and the new `CodeChecks` class. It also introduces
  `testThisNotebookCell` for better access to source code in Jupyter
  notebooks, although access to function source code for `testFunction`
  managers is still not implemented.
