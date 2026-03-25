# Benchmark: Claude Code Native vs Upstream Rule File

## Test Scenario

**Serverless Order Management API** -- an e-commerce backend with:
- User authentication (Cognito)
- Order CRUD (Lambda + DynamoDB single-table)
- Payment processing (Stripe via SQS)
- Order notifications (SES/SNS via EventBridge)
- NFR targets: 1,000 orders/min peak, 99.9% availability, sub-200ms p99 latency
- Tech stack: TypeScript, AWS CDK

See `scenario.md` for the full scenario definition with mock artifacts.

## Methodology

Each of the 14 AIDLC stages was evaluated under 3 conditions:

| Condition | Description |
|-----------|-------------|
| **Native** | Claude Code skill + agent reads SKILL.md and follows instructions |
| **Upstream** | Agent reads upstream core-workflow.md (538 lines) and follows stage rules |
| **Baseline** | Agent receives the task with no AIDLC guidance |

42 total agent evaluations (14 stages x 3 conditions). Each output was graded against skill-specific assertions using `grade.py`.

## Assertions

Each skill has 4-7 assertions covering:
- **Structural compliance**: Question format ([Answer]: tags, X) Other options, categorized sections)
- **Methodology adherence**: Stage-specific patterns (4-dimension analysis, INVEST criteria, EXECUTE/SKIP decisions, 2-phase gate pipeline, technology-agnostic constraint)
- **Artifact completeness**: Expected output sections present

## Results

| Approach | Assertions Passed | Pass Rate |
|----------|------------------|-----------|
| **Native** | **76/76** | **100%** |
| Upstream | 73/76 | 96.1% |
| Baseline | 54/71 | 76.1% |

### Native vs Upstream Differences

| Stage | Native | Upstream | Issue |
|-------|--------|----------|-------|
| functional | 6/6 | 5/6 | Upstream leaked specific AWS service names into technology-agnostic business logic design |
| gate | 5/5 | 3/5 | Upstream merged code review and testing into single pass instead of 2-phase GO/NO-GO + PASS/FAIL pipeline |

## Reproducing

```bash
# Run grading on existing outputs
python3 grade.py

# To re-run evaluations, use Claude Code with the skills in ../.claude/skills/
```

## Files

- `benchmark.json` -- Full grading results per skill per condition
- `scenario.md` -- Test scenario with mock artifacts
- `grade.py` -- Grading script (76 assertions across 14 skills)
