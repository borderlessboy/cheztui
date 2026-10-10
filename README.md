<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/chocs-cat/cheztui/master/docs/logo-dark.svg">
  <img alt="cheztui" src="https://raw.githubusercontent.com/chocs-cat/cheztui/master/docs/logo-light.svg" height="64">
</picture>

A clean, fast TUI for [chezmoi](https://www.chezmoi.io/): see what drifted,
which side changed, and fix it with one key.

cheztui opens on the files where your home directory and your chezmoi source
disagree, says which side changed, and offers the right fix: re-add, apply or
merge. Every write shows a preview first, and the result names the commit
chezmoi made. A `--json` CLI covers the same ground for scripts and coding
agents, including `cheztui edit` for safe scripted edits to managed files.

**Status:** early scaffold. The app opens a placeholder; the design is in
[docs/spec.md](docs/spec.md) and the plan in the
[milestones](https://github.com/chocs-cat/cheztui/milestones).

## Development

```sh
uv sync
make check            # ruff, ty and pytest, as CI runs them
uv run cheztui        # the dev install
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the layout and the release process.

## License

MIT; see [LICENSE](LICENSE).
