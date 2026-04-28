# Addressing

The address grammar used throughout CFS — in `config.yaml`, in admin files (`sources.md`, `targets.md`), and in knowledge node fields and links.

---

## Grammar

Every CFS address is `<backend>:<path>`.

- **`<backend>`** — name of a backend declared in `config.yaml` `backends:`. Lowercase, identifier-safe (letters, digits, `_`, `-`). User-chosen.
- **`<path>`** — backend-relative path. Forward slashes separate components. No leading `/`.

There is no bare-path form. Every address carries an explicit backend.

```
gdrive:System/Archive
laptop_a:Repos/cfs
laptop_b:Downloads
```

A prefix that does not match a declared backend is not a CFS address (e.g., `https://...`, `s3://...`, `mailto:...`). Flows do not attempt to resolve such strings as addresses.

## Backends

Each backend declares `type:` plus type-specific fields. Two classes:

- **Local** (`type: local`) — a filesystem on a specific machine. Resolves only when the agent is running on that machine.
- **Remote** (`type: gdrive`, etc.) — a service the agent reaches via API/MCP/CLI. Resolves wherever the agent has the capability.

A single `config.yaml` may declare any number of each, and the same config is portable across machines and cloud environments.

### Local backends

Declared with `type: local` and a `match:` block describing how the agent recognizes the machine. The agent inspects available context and considers the backend active when all listed `match:` fields agree.

```yaml
backends:
  laptop_a:
    type: local
    match:
      hostname: LAPTOP-A.local       # `hostname` / `uname -n`
      local_hostname: LAPTOP-A       # `scutil --get LocalHostName` (macOS)
```

Recognized fields:

| Field | Source |
|---|---|
| `hostname` | `hostname` / `uname -n` |
| `local_hostname` | `scutil --get LocalHostName` (macOS) |
| `computer_name` | `scutil --get ComputerName` (macOS) |
| `env` | map of environment variable to required value, e.g., `env: { CFS_MACHINE: laptop_a }` |

The set is extensible — additional fields may be added as new platforms surface relevant identifiers. The agent uses what it can inspect and ignores what it can't.

**Path roots at `$HOME` by default.** Local paths resolve relative to the matched machine's home directory: `laptop_a:Repos` → `~/Repos` when running on `laptop_a`. Items outside the user's home are out of scope.

**Optional `root:` override.** A local backend may set `root:` to override the default home-directory root. Useful for sub-directory-scoped backends (test fixtures, named media roots). Resolution: if `root:` is absolute or starts with `~`, it's used as-is; otherwise it's relative to the config file's directory.

**Empty `match:` (always active).** A local backend may declare `match: {}` to signal "trivially active." Use only when the config itself is environmentally scoped (test fixtures, ephemeral configs loaded by an explicit runner) — never in a real `config.yaml` where an unconstrained match would conflict with declared machine backends.

**Exactly one local backend may be active per session.** If multiple match, the configuration is in error — refuse to operate and surface a todo.

### Remote backends

Declared with a backend-specific type (currently `gdrive`) plus type-specific fields. No `match:` block — a remote backend is active wherever the agent has a capability for it.

A remote backend may declare a `mirrors:` map — per-machine local sync paths the agent may use **for reads only**:

```yaml
backends:
  gdrive:
    type: gdrive
    account: you@example.com  # pii:allow
    mirrors:
      laptop_a: ~/Library/CloudStorage/GoogleDrive-you@example.com/My Drive  # pii:allow
      laptop_b: ~/gdrive
```

Mirror semantics are governed by `refs/admin/safety.md` § Backend dispatch — reads may use the mirror, mutations always go through the backend's API. The agent uses the mirror entry whose key matches the active local backend; if no key matches, dispatch is API-only.

## Active-backend determination

At session start, the agent:

1. Inspects environment signals and identifies the matching local backend, if any. At most one.
2. For each remote backend, confirms an available capability (native, MCP, CLI, bundled tool).

Addresses whose backend is not active in the current session are **inert**: valid typed references that cannot be resolved here. Flows must log and soft-skip operations on inert addresses — never error, never improvise. An address pointing at another machine (`laptop_b:Repos/foo` from a session on `laptop_a`) is a meaningful pointer to where the file lives; it just isn't accessible from this environment.

Capability selection for active backends is covered in `SKILL.md` § Prerequisites and `refs/admin/safety.md` § Backend dispatch.

## Locations

`config.yaml` `locations:` entries declare named alternative locations for storage classes (typically projects with different physical requirements per machine). A location may use either of two forms:

**Single-address form** — one address, applies wherever its backend is active:

```yaml
locations:
  cache:
    class: library
    address: gdrive:Cache
```

**Mirrors form** — per-machine map, keyed by local backend name. The agent resolves the location via the entry whose key matches the active local backend; if no key matches, the location is inert in the current session.

```yaml
locations:
  projects-local:
    class: projects
    mirrors:
      laptop_a: laptop_a:Repos
      laptop_b: laptop_b:Code
```

Mirrors-form values are full addresses — the keyed local backend is conventional but not required (a key may resolve to any backend if the user needs it). Mirrors form is a strict superset of single-address form; choose based on whether the location varies by machine.

## Multi-machine sharing

Because every address carries an explicit backend, the same `config.yaml` works across all environments. Each machine declares its own local backend; only the matching one is active per session. Cloud environments declare no local backends, so all `<machine>:` addresses are inert — the intended behavior.

A knowledge node referencing `laptop_a:Repos/cfs/SKILL.md` is portable: on `laptop_a` it resolves; elsewhere it remains a typed reference.

## Constraints

- Backend names must be unique across `backends:`.
- Backend names should not collide with common URI schemes (`http`, `https`, `file`, `mailto`, `ssh`, `git`, `ftp`, `sftp`, `data`, `tel`) — the collision is permitted by grammar but creates parsing ambiguity in node bodies.
- Local backend names should be stable per machine (changing them invalidates existing addresses).

## Examples

### Single-machine setup

```yaml
backends:
  laptop_a:
    type: local
    match: { local_hostname: LAPTOP-A }
  gdrive:
    type: gdrive
    account: you@example.com  # pii:allow
    mirrors:
      laptop_a: ~/Library/CloudStorage/GoogleDrive-you@example.com/My Drive  # pii:allow

storage:
  archive: gdrive:System/Archive
  projects: laptop_a:Repos
```

### Cloud environment

```yaml
backends:
  gdrive:
    type: gdrive
    account: you@example.com  # pii:allow
    # no mirrors — pure API access
```

### Multi-machine

```yaml
backends:
  laptop_a:
    type: local
    match: { local_hostname: LAPTOP-A }
  laptop_b:
    type: local
    match: { hostname: laptop-b.local }
  gdrive:
    type: gdrive
    account: you@example.com  # pii:allow
    mirrors:
      laptop_a: ~/Library/CloudStorage/GoogleDrive-you@example.com/My Drive  # pii:allow
      laptop_b: ~/gdrive
```

- Session on `laptop_a`: `laptop_a:` and `gdrive:` active; `laptop_b:` inert.
- Session on `laptop_b`: `laptop_b:` and `gdrive:` active; `laptop_a:` inert.
- Cloud session: `gdrive:` active via API; both local backends inert.
