# Working on cheztui

Instructions for coding agents (Codex reads this file; Claude Code reads it
through `CLAUDE.md`'s `@AGENTS.md` import). Humans: see CONTRIBUTING.md.

cheztui is a Textual TUI and an argparse CLI for
[chezmoi](https://www.chezmoi.io/). It shows what drifted, which side
changed, and the fix, and runs the fix with one key after a preview. Its
`cheztui edit` command makes scripted, assertion-checked edits to managed
files for agents. `docs/spec.md` is the design; README.md covers use,
CONTRIBUTING.md the layout and the release process, and
`skills/cheztui/SKILL.md` how agents *use* cheztui.

The repo is a scaffold: the placeholder app and `--version` exist, and the
features in `docs/spec.md` §12 land milestone by milestone.

## Before you start

- Read `docs/decisions.md`. Those questions are settled: don't reopen one
  unless the user asks. When the user settles a new one, add an entry.
- Check the roadmap: `gh issue list`, and `gh api repos/chocs-cat/cheztui/milestones`
  for v0.1 to v0.5. Work is tracked there, not in files.

## Commands

- `uv sync`: set up a fresh checkout.
- `make check`: ruff check, ruff format check, ty, pytest. Run it before every
  push. CI runs the same, plus a packaging check.
- `uv run pytest tests/test_cli.py -q`: one file, for the loop while working.

## Roadmap: GitHub Issues

The roadmap is the issue list on `chocs-cat/cheztui`, grouped into the
milestones `v0.1` to `v0.5` from `docs/spec.md` §12. Keep it current:

- **File ideas as issues, don't just mention them.** When you or the user
  come up with a feature, a follow-up, a bug or a loose end you won't handle
  now, create an issue without asking first. Unplanned thoughts get the
  `idea` label. Add an area label and a type label (`bug`, `enhancement`,
  `question`) where one fits, and a milestone when the spec places the work.
  Area labels: `tui`, `cli`, `config`, `chezmoi`, `release`, `documentation`,
  and one per view or feature: `drift`, `files`, `scripts`, `data`,
  `externals`, `adopt`, `secrets`, `health`, `repo`, `preview`, `edit`,
  `skill`.
- **The repo will go public, and its issues with it.** Write them for any
  reader: no private paths, hostnames, dotfile contents or personal details.
- Before starting work, look for an existing issue and reference it. Close
  issues from the PR that resolves them (`Fixes #12` in the PR body).
- Comment on an issue when you learn something that matters to whoever
  picks it up next.

## Workflow

- **One branch and pull request per change.** Don't commit to `master`;
  release-please is the only thing that does.
- Conventional Commits for commit messages *and* PR titles (CI checks
  titles): `feat:`, `fix:`, `perf:`, `docs:`, `refactor:`, `test:`, `ci:`,
  `build:`, `chore:`, with a scope where useful (`fix(tui): …`). The type
  decides the version bump and the changelog entry, so choose it for the
  user-visible effect. PRs are squash-merged, so the title is the commit
  release-please reads.
- Don't edit versions or `CHANGELOG.md`; release-please owns them. Merging
  a release PR publishes to PyPI and the Homebrew tap, so that is the
  maintainer's call. To force a version, add a `Release-As: X.Y.Z` footer.
- `master` only merges once **CI passed** is green; don't bypass it (no
  `gh pr merge --admin`).
- Keep README.md, CONTRIBUTING.md, `skills/cheztui/SKILL.md`, the TUI's help
  text and `docs/spec.md` in step with any behaviour change, in the same PR.
- Put behaviour in `ops.py`; the CLI and the TUI both call it.
- Every chezmoi call goes through `chezmoi.py`, and every write through the
  one write path (DEC-8, DEC-13).

## Live chezmoi: rules

cheztui writes to a real dotfiles repo, and chezmoi may auto-commit and
auto-push every change it makes. A test that reaches the user's own setup
can rewrite their home directory and publish the result. So:

- **Tests never touch the real source dir or home.** Each test builds a
  scratch HOME, a scratch source dir (a real git repo) and a scratch chezmoi
  config under `tmp_path`, and passes them to chezmoi with `--source`,
  `--destination` and `--config`. Set `HOME` (and `XDG_CONFIG_HOME`) to the
  scratch dirs too, so nothing falls back to the real defaults.
- Never run a writing chezmoi command (`apply`, `add`, `re-add`, `edit`,
  `forget`, `destroy`, `chattr`, `state delete`, `update`, `git push`)
  without all three flags pointing at scratch paths.
- The scratch config never enables `autoPush`, and the scratch source repo
  has no remote.
- Integration tests run `ops.py` against the real `chezmoi` binary and skip
  when it isn't installed.

## Testing notes

- Unit: parsers against recorded chezmoi output fixtures; the ops-spec
  engine (every op, count assertions, skip, failure leaves the file
  untouched); masking.
- TUI: `App.run_test()` with `tests/fake_chezmoi.py` (from v0.1) for canned
  states, and snapshot tests per view and for the preview modal.
- To look at the TUI: in `run_test`, `app.save_screenshot("x.svg")`, then
  `rsvg-convert -w 1400 x.svg -o x.png`.
- The shell may be zsh, which doesn't word-split `$var`; wrap bash-isms in
  `bash -c`.
