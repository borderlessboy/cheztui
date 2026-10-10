# Decisions

Settled questions, so they aren't reopened by accident. Each entry says what
was decided and why, and is cited from the docs and the code as `(DEC-n)`.

- Add new entries at the end, numbered one past the greatest existing ID,
  with the month they were settled.
- To change one, discuss it first, then edit the entry in place (don't delete
  it): say what replaced it, when, and why, and update every doc and code site
  that cites it. Never give a changed decision a new ID.

Each entry has this shape:

```markdown
## DEC-1: <short title> (YYYY-MM)

What was decided and why, in a paragraph or two: the alternatives it rules
out and the reason they lost.

*Where:* the docs that carry the rule, if any.
```

## DEC-1: Drift first (2026-10)

The app opens on the Drift view. The question a user brings to cheztui is
what drifted and how to fix it, so the home view answers it. When nothing has
drifted, the Drift view shows one line: `✓ in sync`.

*Where:* `docs/spec.md` §3, §6 (Drift).

## DEC-2: One layout everywhere (2026-10)

Every view fills the same frame: header, view tabs, list on the left, detail
on the right, log line, key bar. A user learns the frame once and can move
between views without reorienting. Terminals narrower than 100 columns stack
the detail under the list.

*Where:* `docs/spec.md` §3, §4.

## DEC-3: Single-key actions, and a key bar of working keys (2026-10)

Actions are single letters on the selected row, with no nested menus. The key
bar lists only the keys that work in the current view at that moment. `:`
opens a command palette for everything else, and `?` shows full help.

*Where:* `docs/spec.md` §3, §5 (Keys).

## DEC-4: Preview, then one key (2026-10)

Any write opens a compact preview modal. Enter confirms and Esc cancels. The
user sees the exact command and its dry-run result before anything changes.

*Where:* `docs/spec.md` §3, §5 (Write flow).

## DEC-5: Show the result (2026-10)

After a write, the log line shows the outcome, the commit chezmoi made, and
whether chezmoi pushed it. chezmoi may auto-commit and auto-push, so the user
needs to see what reached the source repo.

*Where:* `docs/spec.md` §3, §5 (Write flow).

## DEC-6: Async, cached reads (2026-10)

Reads run asynchronously and are cached. The UI never blocks on chezmoi. Each
data source gets one chezmoi call per refresh, shared across views. Long
operations show progress in the log line and can be cancelled.

*Where:* `docs/spec.md` §3, §10.

## DEC-7: Quiet (2026-10)

No emoji and no banners. Each status has a glyph as well as a colour, so the
UI still works without colour.

*Where:* `docs/spec.md` §3.

## DEC-8: One write path (2026-10)

Every write (apply, re-add, add, merge, forget, destroy, chattr, ignore, state
reset, external refresh, edit, update) goes through the same four steps:

1. **Pre-flight.** The source tree must be clean (`git status --porcelain` in
   the source dir). A dirty tree blocks the action, and the preview lists the
   stray files, since chezmoi's auto-commit would sweep them into its commit.
2. **Preview modal.** The exact command, the targets, and a dry-run result
   (`chezmoi <cmd> --dry-run --verbose` where chezmoi supports it, else a
   computed diff). Batch actions get a per-file summary with expandable diffs.
3. **Confirm.** Enter runs; Esc cancels.
4. **Result.** The log line shows the outcome, the commit (from the source
   repo's `HEAD` before and after), and the push state. Views refresh.

A global `--dry-run` (`-n`) passes `-n` to every chezmoi call and marks the
header `DRY RUN`.

*Where:* `docs/spec.md` §5 (Write flow).

## DEC-9: Restore from a commit stays in the Repo view (2026-10)

The Repo view restores a file to a chosen commit's version. cheztui reads the
old source with `git show <commit>:<source-path>` and writes it through
`chezmoi edit --apply`, the same entry point `cheztui edit` uses. The restore
therefore gets the usual preview, apply and commit (DEC-8).

*Where:* `docs/spec.md` §6 (Repo).

## DEC-10: Masking by name patterns and token formats (2026-10)

cheztui masks secret-looking values in decrypted contents and rendered
templates. It detects them from password-manager template functions,
encrypted file bodies, keys matching configurable name patterns, and common
token formats (GitHub, `sk-…`, AWS access keys, Slack, PEM private-key
blocks). Two config glob lists adjust detection per file: `never_mask` for
files where the name patterns misfire, and `always_mask` for files masked
whole. Nothing decrypted reaches disk, the session log, or `--json` output
unless `--reveal` is passed.

*Where:* `docs/spec.md` §5 (Secrets), §9.

## DEC-11: `cheztui edit` takes one target per call (2026-10)

A failure then affects only that file, and each successful call makes one
commit. Agents call it once per file. Its ops spec stays compatible with the
`chezmoi-editor.py` script it replaces, so existing specs keep working.

*Where:* `docs/spec.md` §8.

## DEC-12: The Homebrew formula depends on chezmoi (2026-10)

`chocs-cat/tap/cheztui` declares `depends_on "chezmoi"`. cheztui does nothing
without the chezmoi binary.

*Where:* `docs/spec.md` §2; `scripts/formula.py`.

## DEC-13: Every read and write goes through the chezmoi binary (2026-10)

cheztui shells out to `chezmoi` and never parses or writes the source state
format itself. The exceptions read `.chezmoiignore` and `.chezmoiexternal.*`
for display. It prefers chezmoi's machine-readable output (`--format=json`,
`--path-style=all`) and parses text only where chezmoi has no JSON (`status`,
`doctor`).

*Where:* `docs/spec.md` §1 (Non-goals), §10.
