# Stack layers

For each path the diff touches, match markers in the file itself and in its
directories up to the repository root. A project can match several layers;
apply the profile of every matched layer. Detect again at every review and
write nothing to the project.

| Layer | Markers | Profile |
|---|---|---|
| Python | `pyproject.toml`, `setup.py`, `requirements*.txt`, `*.py`, a Python shebang | `python.md` |
| Agent skills and instructions | `SKILL.md`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` | `agent-skills.md` |
| Ruby | `Gemfile`, `*.rb` | none yet |
| Rails | `config/application.rb` | none yet |
| TypeScript/JavaScript | `package.json`, `tsconfig.json`, `*.ts`, `*.tsx`, `*.js`, `*.jsx` | none yet |
| React | `react` in `package.json` dependencies | none yet |
| Vitest | `vitest` in `package.json` dependencies | none yet |
| Go | `go.mod`, `*.go` | none yet |
| Rust | `Cargo.toml`, `*.rs` | none yet |
| JVM | `pom.xml`, `build.gradle*`, `*.java`, `*.kt` | none yet |
| Swift | `Package.swift`, `*.swift` | none yet |

## Uncovered layers

Add an `Uncovered stacks` line to the review output when either is true:

- a touched path matches a layer whose profile is `none yet`;
- a touched source file matches no layer. Ignore documentation, data, config
  and lock files (`.md`, `.txt`, `.json`, `.yaml`, `.toml`, `.lock`) for this
  check.

Format: `Uncovered stacks: <layer or file extension> - only generic slop
checks applied.`
