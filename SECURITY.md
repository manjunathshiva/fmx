# Security Policy

## Supported Versions

`fmx` follows semantic versioning. Security fixes ship in the latest release.
Older minors receive a fix only if the issue is actively exploited and there
is no reasonable upgrade path.

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x: (please upgrade)|

## Reporting a Vulnerability

If you believe you have found a security issue in `fmx`, please **do not**
open a public GitHub issue. Instead, either:

- Use **private vulnerability reporting** under the repository's
  [**Security** tab](https://github.com/manjunathshiva/fmx/security) (preferred), or
- Email **manjunath.shiva@gmail.com** with the subject line
  `[fmx security] <short summary>`.

Include enough detail to reproduce: the affected version, your macOS version,
a minimal command or script, and the observed vs expected behavior. If you
have a proof-of-concept, include or link to it.

You should expect an acknowledgement within **5 business days**. The maintainer
will share an estimated remediation timeline once the report is triaged.

While the report is being investigated, please refrain from publicly disclosing
the issue. Once a fix has shipped and a reasonable window has passed for users
to upgrade, you are encouraged to publish your write-up — credit will be given
in the release notes unless you prefer to remain anonymous.

## Scope

This policy covers issues in:

- The Python source tree (`src/fmx/`) shipped on PyPI as `fmx`.
- Default configuration (`pyproject.toml`) and the CI/publish workflows that
  affect what gets installed on a user's machine.

Out of scope:

- Vulnerabilities in upstream dependencies (`apple-fm-sdk`, `typer`, `rich`) —
  please report those to the relevant project. `fmx` will ship a release that
  pins or works around a confirmed upstream issue if it materially affects
  users.
- The behavior, guardrails, or output of Apple's on-device Foundation Model
  itself — that lives in Apple Intelligence, not `fmx`. Report model-safety
  concerns to Apple.
- Issues that require an attacker to already have local code-execution rights
  on the user's machine.

## Publishing integrity

`fmx` is published to PyPI via **Trusted Publishing** (OpenID Connect) from the
tagged GitHub Actions release workflow — there are no long-lived API tokens to
leak or rotate. Releases are built on GitHub-hosted runners and uploaded over
OIDC, so a published artifact is always traceable to a specific tag and commit.
