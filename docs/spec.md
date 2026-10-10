# cheztui — project spec

> *chez toi*: "at your place." A clean, fast TUI for [chezmoi](https://www.chezmoi.io/).

Working title: **cheztui**. Status: draft spec, 2026-10-09.

## 1. What it is

cheztui is a terminal UI and CLI for managing dotfiles with chezmoi. It answers
the questions chezmoi's CLI makes awkward: *what drifted, which side changed,
and what is the right fix* — and makes the fix one keypress, with a preview.

It also replaces the `chezmoi-edit` agent skill with `cheztui edit`, a
scripted, assertion-checked edit command for agents and scripts. The repo
ships a skill that teaches agents to drive `cheztui edit`, as corral ships
`skills/corral`.

### Goals

- A very clean, efficient interface: one screen layout, few keys, no nested
  menus, and only information about the selected row.
- cheztui previews every write before running it.
- After a write, cheztui shows the result, including the commit chezmoi made.
- Expose the parts of chezmoi that are hard to see from the CLI: drift
  direction, script state, template data, externals, ignore rules, what a new
  machine would get.
- An agent-facing CLI (`--json`) that covers everything an agent needs,
  including safe edits, so the `chezmoi-edit` skill can be retired.

### Non-goals

- Replacing chezmoi. cheztui shells out to the `chezmoi` binary for every
  read and write; it never parses or writes the source state format itself,
  except where noted (reading `.chezmoiignore`/`.chezmoiexternal` for display).
- A git client. Repo features are read-mostly.
- Windows support.

## 2. Stack and shipping

Same shape as corral and tack.

| Item | Choice |
|---|---|
| Language | Python ≥ 3.11 |
| TUI | Textual (`>=8,<9`) |
| CLI | argparse, `--json` on every read command |
| Config | TOML via tomlkit, `~/.config/cheztui/config.toml` |
| Build | hatchling, uv, `uv.lock` |
| Checks | pytest + pytest-asyncio, ruff (corral's rule set), ty |
| Repo | `chocs-cat/cheztui`, default branch `master`, MIT |
| Releases | release-please, Conventional Commits, CI-gated `master` |
| Distribution | PyPI, Homebrew `chocs-cat/tap/cheztui` (`depends_on "chezmoi"`), Claude plugin manifest (`.claude-plugin/`) |
| Platforms | macOS and Linux |
| Requires | chezmoi ≥ 2.60 (pin the floor to whatever the JSON outputs used need) |

The repo starts private and goes public when the maintainer decides to publish
it. The logo is `docs/logo-light.svg` and `docs/logo-dark.svg`.

Repo layout follows corral: `AGENTS.md` (+ `CLAUDE.md` importing it),
`docs/decisions.md`, roadmap in GitHub Issues, `skills/cheztui/SKILL.md`.

## 3. Design principles

1. **Drift first.** The app opens on the Drift view. When nothing has
   drifted, the Drift view shows one line: `✓ in sync`.
2. **One layout everywhere.** Header · view tabs · list (left) · detail
   (right) · log line · key bar. Every view fills the same frame.
3. **Single-key actions.** Single-letter actions on the selected row. The key
   bar shows only keys that work *right now* in *this* view. `:` opens a
   command palette for everything else; `?` shows full help.
4. **Preview, then one key.** Any write opens a compact preview modal; Enter
   confirms, Esc cancels.
5. **Show the result.** After a write, the log line shows the outcome, the
   commit, and whether chezmoi pushed it.
6. **Fast.** Reads are async and cached; the UI never blocks on chezmoi.
   Long operations show progress in the log line and can be cancelled.
7. **Quiet.** No emoji, no banners. Each status has a glyph and a colour,
   so the UI works without colour.

## 4. Screen layout

```
cheztui • ~/.local/share/chezmoi                  ✓ verify   master ↑0 ↓0   clean
 1 Drift  2 Files  3 Scripts  4 Data  5 Externals  6 Adopt  7 Secrets  8 Health  9 Repo  0 Preview
─────────────────────────────────────┬──────────────────────────────────────────────
 you→ M  .zshrc                      │ ~/.zshrc                       you edited it
 src→ M  .gitconfig            tmpl  │ source  dot_zshrc
 both M  .claude/settings.json       │ ────────────────────────────────────────────
 src→ A  .config/ghostty/config      │ @@ -12,3 +12,4 @@
 run  R  once/install-brew.sh        │   alias ll='ls -la'
                                     │ + alias gs='git status'
─────────────────────────────────────┴──────────────────────────────────────────────
re-added ~/.zshrc → a1b2c3d "Update dot_zshrc" (pushed)
 a Apply  r Re-add  m Merge  e Edit  d Full diff  space Select  / Filter  ? Help
```

- **Header:** source path, `chezmoi verify` badge, branch with ahead/behind,
  source-tree cleanliness (`clean` / `2 uncommitted`), dry-run indicator.
- **View tabs:** number keys switch; the current view is highlighted. A view
  with items needing attention shows a count (`1 Drift 4`).
- **List:** filterable (`/`), multi-select (`space`), vim and arrow keys.
- **Detail:** context for the selected row; scrolls independently
  (`J`/`K` or `PgUp`/`PgDn`).
- **Log line:** last result or current progress. `l` opens the full session
  log.
- **Key bar:** current-context keys only.

Narrow terminals (< 100 cols) stack detail under the list; `tab` toggles focus.

## 5. Global behaviour

### Keys (global)

| Key | Action |
|---|---|
| `1`–`9`, `0` | Switch view |
| `j`/`k`, `↑`/`↓` | Move |
| `J`/`K`, `PgUp`/`PgDn` | Scroll detail |
| `/` | Filter list |
| `space` | Toggle selection (actions apply to selection, else to the current row) |
| `g` | Refresh |
| `:` | Command palette |
| `l` | Session log |
| `,` | Settings |
| `?` | Help |
| `q` | Quit |

### Write flow

Every write (apply, re-add, add, merge, forget, destroy, chattr, ignore,
state reset, external refresh, edit, update) goes through one path:

1. **Pre-flight.** Source tree must be clean (`git status --porcelain` in the
   source dir). If it isn't, the preview says so and lists the stray files;
   the action is blocked until resolved (option: open the Repo view).
2. **Preview modal.** Shows the exact command, the targets, and a dry-run
   result (`chezmoi <cmd> --dry-run --verbose` where chezmoi supports it,
   otherwise a computed diff). For batch actions, a per-file summary with
   expandable diffs.
3. **Confirm.** Enter runs; Esc cancels.
4. **Result.** Log line shows the outcome and the commit chezmoi made (read
   from the source repo's `HEAD` before/after), and push state. Views
   refresh.

Global `--dry-run` (`-n`) mode passes `-n` to every chezmoi call and marks
the header `DRY RUN`.

### Refresh

- Watches the source directory and the managed targets (via `watchfiles`) and
  refreshes the affected views, debounced.
- `g` forces a full refresh.
- Refreshes after every write.

### Secrets

- Decrypted contents and rendered templates show secret-looking values
  masked. Detection marks:
  - values from password-manager template functions;
  - encrypted file bodies;
  - values under keys matching configurable name patterns
    (`token|secret|password|api_key`…);
  - values in common token formats, whatever their key is called: GitHub
    (`ghp_`, `gho_`, `github_pat_`), OpenAI/Anthropic-style `sk-…`, AWS
    access keys (`AKIA…`), Slack (`xox…`), and PEM private-key blocks.
- Two config glob lists adjust detection per file. `never_mask` turns
  masking off for files where the name patterns misfire (a keybindings file
  full of `key = …`). `always_mask` masks the whole body of files like
  `.netrc`, `.env` or `~/.ssh/id_*`.
- `R` reveals for the current detail view only; moving away re-masks.
- Nothing decrypted is ever written to disk, the session log, or `--json`
  output (unless `--reveal` is passed explicitly on the CLI).

### External editor and pager

- `e` suspends the TUI and runs `chezmoi edit --apply <target>` with the
  user's `$VISUAL`/`$EDITOR`, then resumes and shows the result.
- `d` suspends and runs `chezmoi diff <target>` with the user's configured
  diff pager.

## 6. Views

Each view lists: purpose · list rows · detail pane · keys · chezmoi calls.

### 1 · Drift

The home view. Everything where actual state ≠ target state, or a script
would run.

- **Rows** come from `chezmoi status` (both columns), joined with
  `chezmoi managed --format=json --path-style=all` for source paths and
  attributes. Each row gets a **direction**:
  - `you→` — first column set: the target changed since chezmoi last wrote
    it (you edited the file). Default fix: **re-add**.
  - `src→` — only second column set: the source changed (pull, edit). Default
    fix: **apply**.
  - `both` — both changed. Default fix: **merge**.
  - `run` — a script will run on next apply.
- Row tags: `tmpl`, `enc`, `exec`, `link`, `ext`, `dir`.
- Sort: `both` first, then `you→`, `src→`, `run`; alphabetical within.
- **Detail:** target and source paths, direction in words, built-in
  syntax-highlighted unified diff (via `chezmoi diff <target>` captured with
  no pager, rendered by cheztui). For templates, a toggle (`t`) between the
  diff and the rendered output.
- **Keys:** `enter` default fix for the row · `a` apply · `r` re-add ·
  `m` merge (suspends for chezmoi's merge tool) · `M` merge-all through the
  selection · `e` edit source · `d` full diff · `x` forget · `A` apply all
  (preview lists every file; individual files can be unticked).

### 2 · Files

All managed entries, as a collapsible tree of targets.

- **Rows:** `chezmoi managed --format=json --path-style=all`, tree-shaped,
  with drift markers from the Drift view and attribute tags.
- **Detail:** target/source paths, attributes (template, encrypted,
  executable, private, readonly, exact, empty, symlink, run-once…), size,
  last commit touching the source file.
- **Keys:** `space` expand/collapse · `e` edit · `v` view (`chezmoi cat`,
  masked) · `c` chattr (attribute picker, pre-filled from current state) ·
  `x` forget · `X` destroy (typed confirmation) · `i` add an ignore rule ·
  `o` open the source file in `$EDITOR` without apply (palette only).
- chezmoi's own special files (`.chezmoiignore`, `.chezmoiremove`,
  `.chezmoiexternal.*`, `.chezmoidata/`, `.chezmoitemplates/`,
  `.chezmoiscripts/`, `.chezmoiversion`, config template) appear in a
  `chezmoi` group at the top.

### 3 · Scripts

The script ledger: every `run_` script and whether it will run.

- **Rows:** scripts from `chezmoi managed --include=scripts --format=json`,
  joined with `chezmoi state dump --format=json` (`scriptState` for
  `run_once_`, `entryState` for `run_onchange_`). Columns: type
  (`always`/`once`/`onchange`), phase (`before`/`after`), last run time,
  will-run-next-apply flag (from `status` `R`).
- **Detail:** rendered script (`chezmoi cat`), stored hash vs current hash,
  last-run timestamp.
- **Keys:** `enter`/`v` view · `e` edit · `u` reset state so the script runs
  on next apply (`chezmoi state delete --bucket=… --key=…`; preview shows
  the bucket and key) · `U` reset all once-scripts (typed confirmation) ·
  `!` run now (applies just that script).

### 4 · Data & Templates

The template workbench.

- **Sub-tabs** (`[`/`]`): **Data** · **Templates** · **Config**.
- **Data:** `chezmoi data --format=json` as a collapsible tree; values from
  `.chezmoidata` files marked with their source file. `y` copies the template
  expression for the selected key (`{{ .chezmoi.os }}`).
- **Templates:** every `.tmpl` source plus `.chezmoitemplates/` partials.
  Detail shows source on top, rendered output below
  (`chezmoi execute-template --file`), re-rendered live when the file
  changes. `p` opens a scratch prompt to evaluate any template expression.
- **Machine overrides:** `o` opens an override panel to render as another
  machine: override `.chezmoi.os`, `.chezmoi.hostname`, and prompt answers
  (`--init --promptString/--promptBool/--promptChoice`). Overrides are named
  profiles stored in cheztui's config; the header shows the active profile.
- **Config:** `chezmoi cat-config` (masked) and the config template if one
  exists. `e` runs `chezmoi edit-config` or `edit-config-template`.

### 5 · Externals

- **Rows:** entries from `.chezmoiexternal.*` (parsed for display via
  `chezmoi dump --format=json` of external targets where possible): target,
  type (`file`/`archive`/`git-repo`), URL, refresh period, age of cached
  copy (from chezmoi's cache dir mtime), outdated flag.
- **Detail:** full entry, including include/exclude filters and checksum.
- **Keys:** `f` refresh selected (`chezmoi apply --refresh-externals=always
  <target>`) · `F` refresh all · `e` edit the externals file.

### 6 · Adopt

Bring files under management, or decide to ignore them.

- **Rows:** `chezmoi unmanaged` under configured roots (default
  `~/.config`, `~/.local/bin`, `~/.ssh`; set in config), as a tree. A second
  section lists `chezmoi ignored` entries, each with the `.chezmoiignore`
  rule that matched (cheztui renders `.chezmoiignore` with
  `execute-template` and matches the patterns itself; best-effort).
- **Detail:** file preview (masked), size, mode.
- **Keys:** `a` add (flag picker: template, encrypt, exact, follow,
  recursive, create, empty) · `i` ignore (writes a rule to `.chezmoiignore`
  through `cheztui edit`, with a preview) · `R` add a `.chezmoiremove` entry ·
  `u` un-ignore (removes the matching rule, with preview).

### 7 · Secrets & Encryption

- **Rows:** encrypted source files; templates that call secret functions
  (`onepassword*`, `bitwarden*`, `pass`, `keyring`, `secret*`, `vault`, …,
  found by scanning template sources); each password manager's status
  (installed, signed in/unlocked) where its CLI can report it.
- **Detail:** encrypted files show decrypted content in memory, masked;
  templates show which lines call which manager.
- **Keys:** `R` reveal · `e` edit encrypted (`chezmoi edit` handles
  decrypt/re-encrypt) · `c` toggle encryption (`chattr +encrypted/-encrypted`)
  · `k` keyring get/set (`chezmoi secret keyring`) · palette: generate an
  age key (`chezmoi age-keygen`) and show the config snippet to use it.

### 8 · Health

- **Cards:** `chezmoi doctor` parsed into pass/warn/fail/info rows;
  `chezmoi verify` result; chezmoi version vs latest.
- **Keys:** `enter` show the full doctor line · `U` upgrade chezmoi
  (`chezmoi upgrade`, or the Homebrew command when installed by brew).

### 9 · Repo

The source repository, read-mostly.

- **Rows:** recent commits (`git log` in the source dir), newest first,
  with files changed.
- **Header detail:** branch, ahead/behind (background `git fetch` on start),
  uncommitted files (these block writes; see §5).
- **Detail:** the commit's diff, by target name.
- **Keys:** `p` pull + apply (`chezmoi update`; preview runs
  `git fetch` + shows incoming commits and the apply dry-run) · `P` push
  (`chezmoi git push`) · `o` open lazygit in the source dir (suspends) ·
  `v` restore a file to the selected commit's version. cheztui reads the old
  source content with `git show <commit>:<source-path>` and writes it
  through `chezmoi edit --apply`, using the same editor entry point as
  `cheztui edit`, so the restore gets the usual preview, apply and commit.

### 0 · Preview

What a new machine would get.

- **Temp dir (always available):** run `chezmoi apply --destination
  <tmpdir> --dry-run`/`dump --format=json`, optionally with a machine
  override profile from the Data view. List shows every target that would be
  created, with scripts that would run; detail shows the rendered file
  (masked).
- **Docker** (when `docker` is on PATH and configured): `chezmoi docker run
  <image>` with the configured image list; output streams into the detail
  pane.
- **SSH** (when hosts are configured): `chezmoi ssh <host>`; same streaming
  output.
- Temp dirs are always cleaned up.

## 7. CLI

`cheztui` with no arguments opens the TUI. Every read command takes
`--json` (result on stdout, progress on stderr). Exit codes: `0` ok,
`1` some target failed / refused, `2` usage or config error, `3` chezmoi
missing or broken.

| Command | Purpose |
|---|---|
| `cheztui status [--json]` | Drift rows with direction and default fix |
| `cheztui files [--json]` | Managed entries with attributes |
| `cheztui scripts [--json]` | Script ledger |
| `cheztui scripts reset <script>` | Reset run state (prompts unless `--yes`) |
| `cheztui data [--json] [--profile NAME]` | Template data |
| `cheztui render <target> [--profile NAME]` | Rendered output, masked unless `--reveal` |
| `cheztui externals [--json]` | Externals and age |
| `cheztui unmanaged [PATH…] [--json]` | Adopt candidates |
| `cheztui verify [--json]` | Pass/fail, failing targets |
| `cheztui doctor [--json]` | Parsed doctor results |
| `cheztui preview [--profile NAME] [--json]` | Temp-dir new-machine preview |
| `cheztui edit <target> --ops FILE [--dry-run]` | Safe scripted edit (§8) |

Global flags: `--dry-run/-n`, `--chezmoi-config PATH`, `--source PATH`,
`--profile NAME`.

Behaviour lives in `ops.py`; the CLI and the TUI both call it.

## 8. `cheztui edit` and the agent skill

Absorbs the `chezmoi-edit` skill and its `chezmoi-editor.py` script.

### Command

```sh
cheztui edit ~/.zshrc --ops /path/ops.json --dry-run   # print unified diff, write nothing
cheztui edit ~/.zshrc --ops /path/ops.json             # apply, commit (via chezmoi), verify
cheztui edit ~/.zshrc --ops -                          # spec on stdin
```

It takes one target per call, as today's script does. A failure affects
only that file, and each successful call produces one commit. Agents call
it once per file.

It runs the skill's whole procedure as one command:

1. **Managed?** `chezmoi source-path <target>`. Not managed → exit 1 with a
   message pointing at `chezmoi add`.
2. **Template?** If the source ends in `.tmpl`, say so in the output (and
   in `--json`), since the applied result differs from the edit.
3. **Drift?** If `chezmoi status <target>` is non-empty, refuse (exit 1):
   applying would clobber the target. `--allow-drift` overrides.
4. **Clean source tree?** Refuse if `git status --porcelain` in the source
   dir is non-empty, listing the stray files.
5. **Apply ops** to the source text in memory, with the same rules as
   today's script; on any failure, exit 1 having written nothing.
6. **`--dry-run`** prints the unified diff and stops.
7. **Write** by running `chezmoi edit --apply --hardlink=false <target>`
   with cheztui itself as `$EDITOR`/`$VISUAL` (an internal
   `cheztui _editor` entry point that writes in place, never renames).
8. **Verify:** source contains the change, target matches
   (`chezmoi verify <target>`), report the commit made and push state.

### Ops spec

Unchanged from `chezmoi-editor.py`, so existing specs keep working:

```json
{
  "skip_if_contains": "alias buccl=",
  "ops": [
    {"op": "insert_after", "anchor": "alias ssbrew='brew list | fzf'\n",
     "text": "\n# Upgrade Claude Code cask\nalias buccl='brew upgrade claude-code@latest'\n"}
  ]
}
```

Ops: `replace` (`old`/`new`), `delete` (`old`), `insert_after` /
`insert_before` (`anchor`/`text`), `append` / `prepend` (`text`),
`regex_replace` (`pattern`/`repl`, `flags` from `msix`). `count` defaults
to 1 and is an assertion (`"all"` = any number ≥ 1). A bare list of ops is
accepted. `skip_if_contains` makes a re-run a no-op (exit 0).

`--json` output: `{target, source, template, skipped, diff, commit, pushed,
verified}`.

### New files

`cheztui add <path> [--template] [--encrypt] [--dry-run]` wraps
`chezmoi add` with the same clean-tree check and result report, so the
skill has one tool for both cases.

### Skill

`skills/cheztui/SKILL.md` ships in the repo and is deployed by tack (as
corral's is). It covers: when to use cheztui (any change to a file that is
or might be chezmoi-managed), use the CLI with `--json` not the TUI, the
edit flow (read source → write spec → `--dry-run` → apply), ops reference,
new files, exit codes, and read commands for looking before acting.

**Retiring `chezmoi-edit`:** once cheztui v0.1 is released and the
`cheztui` skill is deployed, it replaces the `chezmoi-edit` skill.

## 9. Configuration

`~/.config/cheztui/config.toml`, editable from the settings screen (`,`).

```toml
[ui]
theme = "textual-dark"          # any Textual theme
diff_context = 3
narrow_breakpoint = 100

[adopt]
roots = ["~/.config", "~/.local/bin", "~/.ssh"]

[secrets]
mask_patterns = ["token", "secret", "password", "passwd", "api[_-]?key"]
token_formats = true            # ghp_, sk-, AKIA, xox, PEM blocks…
never_mask = ["~/.config/karabiner/**", "~/.config/ghostty/config"]
always_mask = ["~/.netrc", "~/.ssh/id_*", "**/.env"]

[refresh]
watch = true
debounce_ms = 300

[preview]
docker_images = ["ubuntu:24.04", "debian:12"]
ssh_hosts = []

[profiles.work-linux]           # machine override profiles for Data/Preview
os = "linux"
hostname = "work-laptop"
```

## 10. Architecture

```
src/cheztui/
  cli.py          argparse entry; `cheztui` → TUI, subcommands → ops
  ops.py          all behaviour; returns dataclasses; used by CLI and TUI
  chezmoi.py      async wrapper around the chezmoi binary (--no-tty,
                  --config/--source, -n); typed parsers for each JSON output
  git.py          source-repo queries (porcelain status, ahead/behind, log, HEAD)
  edit.py         ops-spec engine + `_editor` entry point (in-place writes)
  secrets.py      masking
  state.py        chezmoi persistent-state reads/resets
  preview.py      temp-dir / docker / ssh back ends
  config.py       TOML load/save
  watch.py        filesystem watching
  tui/
    app.py        app, header, view tabs, log line, key bar
    views/        drift.py files.py scripts.py data.py externals.py
                  adopt.py secrets.py health.py repo.py preview.py
    widgets/      diff.py (highlighted unified diff), confirm.py (preview
                  modal), picker.py (flags/attributes), tree.py
```

- One chezmoi call per data source per refresh; results cached and shared
  across views.
- Prefer machine-readable output (`--format=json`, `--path-style=all`,
  `--no-pager`); parse text only where chezmoi has no JSON (`status`,
  `doctor`), with parsers that handle paths containing spaces.

## 11. Testing

- **Never touch the real source dir or home.** Tests build a scratch HOME
  and source dir (a real git repo) per test and point chezmoi at them with
  `--source`, `--destination`, `--config`.
- **Unit:** parsers against recorded chezmoi output fixtures; ops engine
  (every op, count assertions, skip, failure leaves file untouched);
  masking.
- **Integration:** `ops.py` against a real `chezmoi` binary in the scratch
  setup (skipped if chezmoi isn't installed).
- **Fake:** `tests/fake_chezmoi.py` for TUI tests that need canned states
  (drift in both directions, scripts, externals, errors).
- **TUI:** `App.run_test()` + snapshot tests (pytest-textual-snapshot) for
  each view and the preview modal.
- CI: macOS and Linux, pytest, ruff check/format, ty, packaging check.

## 12. Milestones

Each milestone is releasable.

**v0.1 — Drift and edit** (enough to retire `chezmoi-edit`)
- App frame: header, view tabs, list/detail, log line, key bar, help,
  palette, settings.
- Drift view with direction, built-in diff, apply / re-add / merge / edit /
  full diff, multi-select, apply-all.
- Write flow (pre-flight, preview modal, result with commit).
- Watch + manual refresh; `--dry-run`.
- CLI: `status`, `edit`, `add`, `verify`, all with `--json`.
- `skills/cheztui/SKILL.md`; plugin manifest; PyPI + Homebrew.

**v0.2 — Files and Adopt**
- Files view (tree, attributes, chattr picker, forget/destroy, special
  files group).
- Adopt view (unmanaged, ignored with matched rule, add flags, ignore,
  `.chezmoiremove`).
- CLI: `files`, `unmanaged`.

**v0.3 — Scripts and Data**
- Script ledger with state reset.
- Data & Templates workbench, live render, machine override profiles.
- CLI: `scripts`, `scripts reset`, `data`, `render`.

**v0.4 — Secrets, Externals, Health**
- Secrets & Encryption view with masking/reveal.
- Externals view with refresh.
- Health view (doctor, verify, upgrade).
- CLI: `externals`, `doctor`.

**v0.5 — Repo and Preview**
- Repo view (log, pull+apply with preview, push, restore, lazygit).
- Preview: temp dir, then Docker and SSH.
- CLI: `preview`.

## 13. Settled decisions

These questions were open in the first draft and are now settled.

- **Restore from a commit** stays in the Repo view. It writes through
  `chezmoi edit --apply` like every other write (§6, Repo).
- **Masking** uses name patterns plus token-format detection, with
  `never_mask` and `always_mask` globs in config (§5, §9).
- **`cheztui edit`** takes one target per call (§8).
- **The Homebrew formula** declares `depends_on "chezmoi"` (§2).
