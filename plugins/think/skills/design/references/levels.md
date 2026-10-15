# Levels — recognise which ones a question spans

| Level | Decides | Leaves to the level below | Language |
|---|---|---|---|
| **product** | the systems and their responsibilities, boundaries between them, who owns which data, how they talk, built vs bought, how it deploys and scales | how any system is built | agnostic |
| **project** | the shape of one codebase: stack, repo and folder layout, layers and their allowed dependencies, cross-cutting concerns (config, errors, logging, auth, testing), how modules are wired | the inside of a module | stack-specific |
| **module** | one unit's interface, internal structure, state and lifecycle, dependencies, the patterns it uses, how it is tested | implementation detail | stack-specific |

## Recognition

- **Signals for product:** more than one system or deployable, clients and servers, sync or offline,
  tenants, scaling, build vs buy, no stack fixed yet. **Project:** one codebase's layout, layers,
  folders, state flow, config, testing, a stack or framework named. **Module:** one unit named (a
  package, service, screen, class, component, store) or its interface, state, or dependencies.
- **Primary level** is where the decision lives; a level is **dependent** when the question's answer
  changes what happens there ("client-server or local-first?" is product, with project implications
  for sync, storage, and state; "how should the sync module expose conflicts?" is module, with a
  project implication for the error model). Answer the primary level fully and each dependent level
  briefly; say when a level is deliberately left open.
- Product reasoning never names a framework or library; project and module reasoning always do.

## Stack detection (project and module)

`package.json`, `pubspec.yaml`, `Package.swift`, `*.xcodeproj`, `go.mod`, `Cargo.toml`, `pyproject.toml`
or `requirements.txt`, `*.csproj`, `pom.xml` or `build.gradle`, `Gemfile`, `mix.exs`, `composer.json`,
and the frameworks they declare. Read the project's own rules (`CLAUDE.md`, `.claude/rules/`, lint and
build configs) before any ecosystem advice: a repo's rule beats a general practice. Optional
user-maintained cards live in `stacks/<stack>.md` (template there).
