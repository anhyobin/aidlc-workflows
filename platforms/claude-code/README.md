# AIDLC on Claude Code Native

A native Claude Code implementation of [AWS AIDLC (AI-Driven Development Life Cycle)](https://github.com/awslabs/aidlc-workflows) using agents, skills, hooks, and rules.

The upstream AIDLC provides a single rule file for all AI coding agents. This project reimplements it as a **Claude Code-native multi-agent system** with dedicated agents, 14 slash commands, conditional extension rules, and automated hooks -- while preserving AIDLC's core value: **deep question-answer cycles that eliminate ambiguity before code is written**.

## Why Claude Code Native?

| Aspect | Upstream AIDLC (Rule File) | Claude Code Native |
|--------|---------------------------|-------------------|
| Context cost | ~30K tokens always loaded | ~73-line CLAUDE.md + skills loaded on demand |
| Role separation | Single AI plays all roles | 4 specialized agents with tool restrictions |
| Tool control | "Don't modify code" (text instruction) | `disallowedTools: [Write, Edit]` (system-level enforcement) |
| Workflow UX | AI interprets rules to progress | Natural language auto-routing + `/aidlc-*` direct control |
| Session resumption | "Read the state file" (text rule) | SessionStart hook auto-detects and guides |
| Audit logging | AI manually writes audit.md | SubagentStop hook auto-records |
| Extensions | Always-loaded opt-in files | `paths`-based conditional rule loading |

## Prerequisites

- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) installed and authenticated

## Installation

```bash
# Copy .claude/ directory to your project root
cp -r .claude/ /path/to/your-project/.claude/

# Start Claude Code in your project
cd /path/to/your-project
claude
```

Claude Code automatically recognizes the `.claude/` directory at the project root.

## Project Structure

```
.claude/
├── CLAUDE.md                              # Lightweight core (routing + conventions)
├── settings.json                          # Hooks + Permissions
│
├── agents/                                # Role-based specialized agents
│   ├── aidlc-analyst.md                   #   Analysis & design (Bash disabled)
│   ├── aidlc-architect.md                 #   Infrastructure design (AWS CLI + MCP)
│   ├── aidlc-developer.md                 #   Code generation (full tool access)
│   └── aidlc-reviewer.md                  #   Verification (read-only, Write/Edit disabled)
│
├── rules/                                 # Cross-cutting rules (auto-loaded by all agents)
│   ├── aidlc-content-validation.md        #   Mermaid/ASCII diagram validation
│   ├── aidlc-error-handling.md            #   Error severity levels and recovery
│   ├── aidlc-terminology.md               #   Phase/Stage/Unit term definitions
│   ├── aidlc-workflow-changes.md          #   Mid-workflow change handling
│   ├── aidlc-ext-security-baseline.md     #   Security extension (conditional)
│   └── aidlc-ext-property-based-testing.md #  PBT extension (conditional)
│
└── skills/                                # Workflow slash commands (14 skills)
    ├── aidlc-detect/SKILL.md              #   /aidlc-detect
    ├── aidlc-reverse/SKILL.md             #   /aidlc-reverse
    ├── aidlc-requirements/SKILL.md        #   /aidlc-requirements [description]
    ├── aidlc-stories/SKILL.md             #   /aidlc-stories
    ├── aidlc-app-design/SKILL.md          #   /aidlc-app-design
    ├── aidlc-units/SKILL.md               #   /aidlc-units
    ├── aidlc-plan/SKILL.md                #   /aidlc-plan
    ├── aidlc-functional/SKILL.md          #   /aidlc-functional [unit]
    ├── aidlc-nfr/SKILL.md                 #   /aidlc-nfr [unit]
    ├── aidlc-infra/SKILL.md               #   /aidlc-infra [unit]
    ├── aidlc-code/SKILL.md                #   /aidlc-code [unit]
    ├── aidlc-test/SKILL.md                #   /aidlc-test
    ├── aidlc-gate/SKILL.md                #   /aidlc-gate [unit]
    └── aidlc-status/SKILL.md              #   /aidlc-status
```

## Agents

Four agents divide AIDLC responsibilities with enforced tool boundaries.

| Agent | Skills | Tools Blocked | Purpose |
|-------|--------|---------------|---------|
| **aidlc-analyst** | 9 (Inception + functional/nfr design) | Bash, Edit | Deep questioning, ambiguity analysis, design docs |
| **aidlc-architect** | 1 (infrastructure design) | Edit | AWS service mapping with CLI + MCP access |
| **aidlc-developer** | 1 (code generation) | -- | Plan-first code generation (maxTurns: 100) |
| **aidlc-reviewer** | 2 (gate, test) | Write, Edit | Read-only verification: GO/NO-GO and PASS/FAIL |

Each skill runs in `context: fork` with its assigned agent, providing both context isolation and tool enforcement.

## Slash Commands

### Inception Phase

| Command | Description |
|---------|-------------|
| `/aidlc-detect` | Scan workspace, create state file, determine greenfield/brownfield |
| `/aidlc-reverse` | Reverse-engineer existing codebase (brownfield only) |
| `/aidlc-requirements [desc]` | Requirements analysis through deep Q&A cycles |
| `/aidlc-stories` | User personas and INVEST-validated stories |
| `/aidlc-app-design` | Component, service, and dependency design |
| `/aidlc-units` | Decompose system into development units |
| `/aidlc-plan` | Create execution plan (EXECUTE/SKIP per Construction stage) |

### Construction Phase (per unit)

| Command | Agent | Description |
|---------|-------|-------------|
| `/aidlc-functional [unit]` | analyst | Business logic, domain models, validation rules |
| `/aidlc-nfr [unit]` | analyst | NFR requirements + tech stack + design patterns |
| `/aidlc-infra [unit]` | architect | Map logical components to AWS services |
| `/aidlc-code [unit]` | developer | Plan-first code generation |
| `/aidlc-gate [unit]` | reviewer | Code review (GO/NO-GO) + build/test (PASS/FAIL) |
| `/aidlc-test` | reviewer | Full project build and test suite |

### Utility

| Command | Description |
|---------|-------------|
| `/aidlc-status` | Project status dashboard with pending items |

## Extensions

Optional rule sets activated during Requirements Analysis via opt-in questions.

| Extension | Description | Activation |
|-----------|-------------|------------|
| **Security Baseline** | Encryption, logging, auth, input validation, secrets, HTTP headers, dependency audit | Team selects "Yes" during requirements |
| **Property-Based Testing** | Round-trip, invariant, idempotence testing with framework and generator requirements | Team selects "Yes" or "Partial" |

Extensions use Claude Code's `paths`-based conditional rule loading -- rules in `.claude/rules/aidlc-ext-*.md` are only active when their corresponding marker file exists in `aidlc-docs/extensions/`.

## Quick Start

```bash
claude

# Natural language (auto-routing)
> I want to build an online booking system with user authentication and payment processing

# Or direct control
> /aidlc-detect
> /aidlc-requirements I want to build an online booking system...
```

The workflow progresses automatically through each stage with team approval gates.

## Question-Answer Cycle

The core AIDLC mechanism:

```
Skill triggered → Analyst generates question file
                       ↓
              Team answers in .md file → says "done"
                       ↓
              Analyst analyzes answers
              ├── Empty/vague/contradictory → Clarification file → repeat
              └── All clear → Generate artifacts → Team approves → Next stage
```

Vague signals auto-detected: "depends", "maybe", "not sure", "probably", "standard", "as needed", "TBD"

## Upstream Compatibility

Same AIDLC methodology as [awslabs/aidlc-workflows](https://github.com/awslabs/aidlc-workflows):
- Same three-phase lifecycle (Inception → Construction → Operations)
- Same stage sequence and gate rules
- Same question file format and artifact structure
- Extensions aligned with upstream's security-baseline and property-based-testing

What's different: Claude Code-native implementation using agents, skills, rules, and hooks.

## License

This project is licensed under the MIT-0 License. See [LICENSE](LICENSE).

Based on [awslabs/aidlc-workflows](https://github.com/awslabs/aidlc-workflows).
