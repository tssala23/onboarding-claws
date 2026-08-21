# Onboarding Claws

Generate a personalized, installable OpenClaw Claw project directory from a small
enterprise onboarding questionnaire.

This repository is deliberately only a generator. It does not deploy OpenClaw,
install the generated Claw, configure credentials, retain generated agents, or manage
them after handoff. A downstream pipeline receives the generated directory and owns
everything that follows.

New to OpenClaw? Read [OpenClaw agents and Claws: a guide for app developers](docs/openclaw-agents-and-claws.md)
for an explanation of the workspace files that shape an agent, what the experimental
Claws feature installs, and how this repository connects the two.

## What onboarding controls

The generator combines three layers:

1. Shared enterprise briefing, evidence, and approval behavior.
2. One of six initial role lenses: General Management, Finance, Operations,
   Marketing, Technology, or Engineering.
3. The employee's initial focus, key contacts, preferred communication style, and
   morning schedule.

The resulting agent is not permanently locked to these answers. `BOOTSTRAP.md` uses
them once to initialize the living OpenClaw workspace. The user can subsequently ask
the agent to evolve its `USER.md`, `SOUL.md`, memory, priorities, contacts, style, or
schedule. Security boundaries remain in the downstream sandbox, connector, and proxy
configuration rather than editable prose files.

## Requirements

- Ansible Core 2.15 or newer
- Python with IANA timezone data
- OpenClaw `2026.8.1-beta.2` or newer with experimental Claws support, recommended
  for canonical validation

The role performs structural verification without OpenClaw, but skips canonical
`openclaw claws validate` when the CLI is unavailable. At the time this repository
was created, the command was present in `2026.8.1-beta.2` but not in the latest stable
`2026.7.1-2`; CI therefore pins the tested beta explicitly.

## Generate a Claw

Copy the sanitized example outside the repository and edit it with the application's
onboarding values:

```bash
cp examples/onboarding.example.yml /tmp/onboarding.yml
ansible-playbook playbooks/generate-claw.yml \
  -e @/tmp/onboarding.yml \
  -e claw_output_dir=/tmp/generated-employee-claw
```

The output must be an absolute path to an absent or empty dedicated directory. The
role refuses broad or nonempty targets.

The generated project contains:

```text
package.json
CLAW.md
BOOTSTRAP.md
profiles/openclaw.yml
workspace/AGENTS.md
workspace/skills/enterprise-briefing/SKILL.md
workspace/skills/persona-briefing/SKILL.md
```

The downstream installer can preview and apply it using the Claw lifecycle:

```bash
export OPENCLAW_EXPERIMENTAL_CLAWS=1
openclaw claws validate /tmp/generated-employee-claw
openclaw claws add /tmp/generated-employee-claw --dry-run --json
```

Applying the plan, credentials, connector setup, and artifact disposal are outside
this repository's responsibility.

## Input fields

| Field | Purpose |
| --- | --- |
| `preferred_name` | Name the agent should use when addressing the person |
| `role` | One of the six supported persona keys |
| `day_start` | User's local workday start in `HH:MM` form |
| `timezone` | Confirmed IANA timezone such as `America/New_York` |
| `current_focus` | Initial projects, outcomes, or problems occupying the user |
| `key_contacts` | Directory-backed contacts with stable ID, display name, and email |
| `communication_style` | `executive`, `concise`, `analytical`, or `conversational` |
| `connectors` | Expected governed communication connectors; credentials are never embedded |
| `working_days` | Optional local workdays; defaults to Monday through Friday |
| `brief_lead_minutes` | Optional lead time; defaults to 30 minutes before day start |
| `claw_output_dir` | Absolute handoff directory owned by the calling pipeline |

The JSON Schema at `schemas/onboarding.schema.json` is suitable for validation in the
calling application. The Ansible role repeats safety-critical validation at render
time.

`preferred_name` is initialized in `USER.md`, which OpenClaw uses for stable user
preferences and how the agent relates to the person. It does not belong in `SOUL.md`;
that file describes the agent's own voice and personality. The generated package and
default agent IDs are role-based and contain no employee identifier. A downstream
installer placing multiple agents of the same role on one Gateway should supply its
own collision-free `--agent-id` during Claw preview and apply.

## Privacy

Generated Claws contain personal and business context in `BOOTSTRAP.md`. Treat the
entire output directory as private, hand it directly to the installer, and remove it
according to the calling pipeline's retention policy.

The repository ignores common onboarding input names and generated output folders.
Ansible suppresses tasks that render or inspect personal values, but callers must also
avoid passing real values directly on a command line because process listings and CI
logs may capture them. Prefer `-e @/protected/path/onboarding.yml` or an equivalent
secret-input mechanism.

## Development

Run the local checks:

```bash
python3 -m unittest discover -s tests/unit -v
ansible-playbook --syntax-check playbooks/generate-claw.yml
tests/integration/generate_matrix.sh
```

CI additionally runs `yamllint`, `ansible-lint`, and JSON Schema validation. The
integration test renders all 24 role/style combinations into a temporary directory
and removes them afterward.
