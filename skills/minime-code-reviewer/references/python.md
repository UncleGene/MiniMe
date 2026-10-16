# Python slop profile

Apply these in addition to the generic slop checks.

- Bare `except:` and `except Exception: pass`, and exceptions converted into
  `None` or a default return.
- Mutable default arguments. Naive and timezone-aware datetimes mixed.
- Imports of packages missing from the declared dependencies; stdlib or
  library calls that do not exist at the supported Python version; syntax
  newer than `requires-python`.
- Type and lint suppressions added to pass checks: `# type: ignore`, `Any`,
  `cast`, or `# noqa` with no reason. Treat these like weakened tests.
- Tests that patch the unit under test, assert only that a mock was called,
  or depend on the real network, clock, filesystem layout or test order.
- `subprocess` with `shell=True` or interpolated input, `eval` or `exec`,
  unpickling untrusted data, and paths built from input without a
  containment check.
- Files, sockets or processes opened outside `with` or another guaranteed
  cleanup.
- Reimplemented stdlib (`pathlib`, `itertools`, `dataclasses`, `functools`)
  or helpers the project already has.
- Leftover `print` debugging, and secrets or tokens in logs or error messages.
