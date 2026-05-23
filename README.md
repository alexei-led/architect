# architect

Instruction-first architecture review plugin.

## Contents

- `src/agents/architect/AGENT.md` — architect role prompt.
- `src/skills/` — review, scorecard, planning, methodology, and tool skills.
- `src/templates/` — report, scorecard, and plan templates.
- `src/architect_tools/` — helper CLIs.
- `src/plugins/architecture/plugin.yaml` — plugin manifest.

## Install

Install the plugin. The manifest defines what ships.

## Development

```sh
make setup
make check
```

Hooks:

- pre-commit: `make lint`
- pre-push: `make check`
