# Contributing to fmx

Thanks for your interest! `fmx` is a small, friendly CLI over Apple's
on-device Foundation Model (`apple-fm-sdk`) — it brings `fmx chat` /
`respond` / `schema` to macOS 26 ahead of macOS 27's native `fm`. This
guide covers the dev setup, how changes are reviewed, and how to sign off
your commits.

## Requirements

`fmx` drives Apple Intelligence's on-device model, so actually *running* it
needs:

- macOS 26.0+ on a compatible Mac (Apple silicon, M1 or later — see
  https://support.apple.com/en-us/121115)
- Apple Intelligence enabled in System Settings
- Python 3.10+

You can still develop and test the parts that don't touch the model (schema
parsing, CLI wiring) on any OS — see "Running tests" below.

## Development setup

We use [uv](https://docs.astral.sh/uv/) for environments and packaging.

```bash
git clone https://github.com/manjunathshiva/fmx.git
cd fmx
uv venv
uv pip install -e .
```

`apple-fm-sdk` compiles against the macOS 26 Foundation Models framework,
so `uv pip install -e .` only fully resolves on a supported Mac. On other
platforms, install just the tooling to work on the SDK-free code:

```bash
uv pip install pytest ruff
```

## Running tests

```bash
# Everything that doesn't need the on-device model (runs anywhere):
PYTHONPATH=src uv run --no-project --isolated --with pytest pytest -m "not require_model"

# Full suite, including on-device model smoke tests (needs a supported Mac):
pytest
```

Tests marked `require_model` auto-skip when Apple Intelligence isn't
available, so the "not require_model" run is exactly what CI verifies.

## Linting

```bash
uvx ruff check .
```

Please run ruff before opening a PR — CI rejects lint failures.

## How to propose a change

1. For anything substantial (new subcommand, behavior change, new
   dependency), open an issue first to discuss. Small fixes can go straight
   to a PR.
2. Fork, branch, implement, add/adjust tests, run ruff + the test suite.
3. Keep PRs focused — one logical change per PR makes review tractable.
4. Match the surrounding style: type hints on public functions, concise
   docstrings, and the explanatory-comment tone used in the workflows.
5. Fill out the pull-request template.

### Review & merge rules

`main` is protected. Every PR needs:

- a passing **`lint-and-test`** check (ruff + SDK-free tests + build),
- a passing CodeQL **`Analyze (python)`** check, and
- at least **one approving review**.

The branch must be up to date with `main` before it can merge.

## Sign-off (Developer Certificate of Origin)

`fmx` uses the [Developer Certificate of Origin](https://developercertificate.org/)
(DCO) instead of a CLA. Signing off certifies you wrote the code (or have
the right to contribute it) and agree to release it under the project's
license.

Add a `Signed-off-by` trailer to each commit:

```bash
git commit -s -m "your message"
```

`-s` appends `Signed-off-by: Your Name <your.email@example.com>` from your
git identity, so set it once:

```bash
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

PRs without sign-off will be asked to add it before merge. You keep
copyright over your contribution; the DCO simply confirms you have the
right to contribute it.

## Reporting security issues

Please don't open a public issue for a vulnerability. Use GitHub's private
vulnerability reporting under the repo's **Security** tab, or email the
maintainer at manjunath.shiva@gmail.com, so it can be fixed before
disclosure.

## License

By contributing, you agree your contributions are licensed under the
project's [MIT License](LICENSE).
