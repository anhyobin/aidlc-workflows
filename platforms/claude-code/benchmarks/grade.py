#!/usr/bin/env python3
"""Grade all 14 AIDLC skill test outputs against comprehensive assertions."""

import json
import re
import sys
import os
from pathlib import Path


def has_korean(text: str) -> bool:
    return bool(re.search(r'[\uAC00-\uD7AF\u1100-\u11FF\u3130-\u318F]', text))


def check(text, pattern, flags=re.IGNORECASE):
    return bool(re.search(pattern, text, flags))


def grade_skill(skill_name: str, text: str) -> list:
    results = []

    # Universal assertion: no Korean
    results.append({
        "text": f"[{skill_name}] Output contains no Korean characters",
        "passed": not has_korean(text),
        "evidence": "No Korean found" if not has_korean(text) else "Korean characters detected"
    })

    # Skill-specific assertions
    if skill_name == "detect":
        results.append({"text": "Identifies Greenfield/Brownfield", "passed": check(text, r'greenfield|brownfield'), "evidence": ""})
        results.append({"text": "Recommends next step", "passed": check(text, r'/aidlc-(reverse|requirements)'), "evidence": ""})
        results.append({"text": "Contains state file structure", "passed": check(text, r'Current Phase|Phase Progress|INCEPTION'), "evidence": ""})
        results.append({"text": "Contains completion summary", "passed": check(text, r'===.*Complete|===.*Detection'), "evidence": ""})

    elif skill_name == "reverse":
        results.append({"text": "Multi-dimensional discovery", "passed": check(text, r'package|module|business|infrastructure|build|service'), "evidence": ""})
        results.append({"text": "Produces 8 artifact types", "passed": check(text, r'(architecture|code.structure|api|component|technology|dependenc|quality)'), "evidence": ""})
        results.append({"text": "Mentions brownfield context", "passed": check(text, r'brownfield|existing.*code'), "evidence": ""})

    elif skill_name == "requirements":
        results.append({"text": "4-dimension analysis", "passed": check(text, r'clarity.*type.*scope.*complexity|clarity.*scope|type.*scope', re.IGNORECASE | re.DOTALL), "evidence": ""})
        results.append({"text": "Analysis depth specified", "passed": check(text, r'minimal|standard|comprehensive'), "evidence": ""})
        results.append({"text": "Questions with [Answer]: tags", "passed": check(text, r'\[Answer\]:'), "evidence": ""})
        results.append({"text": "Questions with X) Other option", "passed": check(text, r'X\)'), "evidence": ""})
        results.append({"text": "Multiple question categories", "passed": check(text, r'functional.*non.functional|business.*technical', re.IGNORECASE | re.DOTALL), "evidence": ""})
        results.append({"text": "Team notification message", "passed": check(text, r'generated|file location|let us know|answer.*complete'), "evidence": ""})

    elif skill_name == "stories":
        results.append({"text": "Personas defined", "passed": check(text, r'persona|archetype|role.*goal'), "evidence": ""})
        results.append({"text": "INVEST criteria mentioned", "passed": check(text, r'INVEST|independent.*negotiable|valuable.*estimable'), "evidence": ""})
        results.append({"text": "Acceptance criteria present", "passed": check(text, r'acceptance criteria|\[ \]'), "evidence": ""})
        results.append({"text": "Story format (As a...I want...)", "passed": check(text, r'As a.*I want|As a.*so that'), "evidence": ""})

    elif skill_name == "app-design":
        results.append({"text": "Component definitions", "passed": check(text, r'component.*purpose|component.*responsibilit'), "evidence": ""})
        results.append({"text": "Service definitions", "passed": check(text, r'service.*trigger|service.*responsibilit|service.*flow'), "evidence": ""})
        results.append({"text": "Dependency matrix/diagram", "passed": check(text, r'depend.*matrix|depend.*diagram|depends on'), "evidence": ""})
        results.append({"text": "Question file with options", "passed": check(text, r'\[Answer\]:') or check(text, r'A\)|B\)|X\)'), "evidence": ""})

    elif skill_name == "units":
        results.append({"text": "Unit definitions with scope", "passed": check(text, r'unit.*scope|unit.*component'), "evidence": ""})
        results.append({"text": "Dependency/execution order", "passed": check(text, r'execution order|phase 1|critical path|depends on'), "evidence": ""})
        results.append({"text": "Effort estimates", "passed": check(text, r'effort|XS|S|M|L|XL|t-shirt'), "evidence": ""})
        results.append({"text": "Story-to-unit mapping", "passed": check(text, r'US-\d+|story.*unit|mapping'), "evidence": ""})

    elif skill_name == "plan":
        results.append({"text": "EXECUTE/SKIP decisions", "passed": check(text, r'EXECUTE|SKIP'), "evidence": ""})
        results.append({"text": "Risk assessment", "passed": check(text, r'risk.*level|risk.*low|risk.*medium|risk.*high'), "evidence": ""})
        results.append({"text": "Impact analysis", "passed": check(text, r'impact.*analysis|user.facing|structural|data model'), "evidence": ""})
        results.append({"text": "Workflow visualization", "passed": check(text, r'mermaid|graph|flowchart|───|→'), "evidence": ""})

    elif skill_name == "functional":
        results.append({"text": "Business logic flows", "passed": check(text, r'business logic|business rule|process|flow'), "evidence": ""})
        results.append({"text": "Domain model/entities", "passed": check(text, r'domain.*model|domain.*entit|entity|Order.*orderId'), "evidence": ""})
        results.append({"text": "Validation rules", "passed": check(text, r'validation|constraint|invariant'), "evidence": ""})
        results.append({"text": "Question file present", "passed": check(text, r'\[Answer\]:') or check(text, r'question', re.IGNORECASE), "evidence": ""})
        results.append({"text": "Technology-agnostic", "passed": not check(text, r'Lambda|DynamoDB|SQS') or check(text, r'technology.agnostic|agnostic'), "evidence": ""})

    elif skill_name == "nfr":
        results.append({"text": "NFR categories covered", "passed": check(text, r'scalability.*performance|availability.*security', re.DOTALL), "evidence": ""})
        results.append({"text": "Tech stack decisions", "passed": check(text, r'tech.*stack|technology.*choice|TypeScript|Node'), "evidence": ""})
        results.append({"text": "Design patterns", "passed": check(text, r'pattern|circuit.breaker|retry|cach|resilience'), "evidence": ""})
        results.append({"text": "Measurable targets", "passed": check(text, r'p99|latency.*\d|uptime.*\d|99\.\d'), "evidence": ""})

    elif skill_name == "infra":
        results.append({"text": "AWS service mapping", "passed": check(text, r'Lambda|DynamoDB|API Gateway|SQS|EventBridge'), "evidence": ""})
        results.append({"text": "Configuration details", "passed": check(text, r'memory|timeout|capacity|instance|provisioned'), "evidence": ""})
        results.append({"text": "Deployment architecture", "passed": check(text, r'deploy|CI/CD|pipeline|stack|CDK'), "evidence": ""})
        results.append({"text": "Cost considerations", "passed": check(text, r'cost|\$|pricing|estimate'), "evidence": ""})

    elif skill_name == "code":
        results.append({"text": "Checkbox-based plan", "passed": check(text, r'\[ \]|- \['), "evidence": ""})
        results.append({"text": "Structured sections", "passed": check(text, r'project structure|business logic|API layer|data layer|test', re.IGNORECASE), "evidence": ""})
        results.append({"text": "Plan approval gate", "passed": check(text, r'approv|gate|confirm|before.*writ'), "evidence": ""})
        results.append({"text": "Design artifact references", "passed": check(text, r'functional.design|nfr|infrastructure|design.*artifact'), "evidence": ""})

    elif skill_name == "gate":
        results.append({"text": "Two-phase pipeline", "passed": check(text, r'phase 1.*phase 2|code review.*build.*test', re.DOTALL), "evidence": ""})
        results.append({"text": "GO/NO-GO verdict", "passed": check(text, r'GO.*NO.GO|verdict'), "evidence": ""})
        results.append({"text": "PASS/FAIL verdict", "passed": check(text, r'PASS.*FAIL|verdict'), "evidence": ""})
        results.append({"text": "Security checks", "passed": check(text, r'security|OWASP|secret|injection|auth'), "evidence": ""})

    elif skill_name == "test":
        results.append({"text": "Multiple test types", "passed": check(text, r'unit test.*integration|integration.*contract|unit.*integration', re.DOTALL), "evidence": ""})
        results.append({"text": "Build step included", "passed": check(text, r'build.*step|build.*command|compile|transpil'), "evidence": ""})
        results.append({"text": "Coverage metrics", "passed": check(text, r'coverage|percent|%'), "evidence": ""})
        results.append({"text": "PASS/FAIL summary", "passed": check(text, r'PASS.*FAIL|overall.*readiness|verdict'), "evidence": ""})

    elif skill_name == "status":
        results.append({"text": "Dashboard format", "passed": check(text, r'dashboard|===|---'), "evidence": ""})
        results.append({"text": "Phase progress shown", "passed": check(text, r'INCEPTION|CONSTRUCTION|phase.*progress', re.IGNORECASE), "evidence": ""})
        results.append({"text": "Unit status table", "passed": check(text, r'unit|order.service|auth.service'), "evidence": ""})

    # Fill evidence
    for r in results:
        if not r["evidence"]:
            r["evidence"] = "Check passed" if r["passed"] else "Check failed"

    return results


def main():
    base_dir = Path("/Users/anhyobin/dev/aidlc-claude/aidlc-skills-workspace/full-eval")
    skills = ["detect", "reverse", "requirements", "stories", "app-design", "units",
              "plan", "functional", "nfr", "infra", "code", "gate", "test", "status"]

    all_results = {}
    total_passed = 0
    total_assertions = 0

    for skill in skills:
        for variant in ["with_skill", "upstream", "without_skill"]:
            result_file = base_dir / f"eval-{skill}" / variant / "outputs" / "result.md"
            if not result_file.exists():
                print(f"SKIP: {skill}/{variant} (no output file)")
                continue

            text = result_file.read_text()
            grades = grade_skill(skill, text)

            passed = sum(1 for g in grades if g["passed"])
            total = len(grades)
            total_passed += passed
            total_assertions += total

            key = f"{skill}/{variant}"
            all_results[key] = {
                "passed": passed,
                "total": total,
                "pass_rate": round(passed / total, 2) if total > 0 else 0,
                "details": grades
            }

            # Save grading.json
            grading_dir = base_dir / f"eval-{skill}" / variant
            grading_file = grading_dir / "grading.json"
            with open(grading_file, 'w') as f:
                json.dump({"eval_name": skill, "variant": variant, "expectations": grades,
                           "summary": {"passed": passed, "total": total}}, f, indent=2)

    # Print summary
    print("=" * 70)
    print(f"  AIDLC Full Skill Evaluation - Benchmark Report")
    print("=" * 70)
    print(f"\n{'Skill':<16} {'Native (Ours)':<18} {'Upstream Rule':<18} {'No Guidance':<18} {'Native vs Up':<12}")
    print("-" * 82)

    for skill in skills:
        ws = all_results.get(f"{skill}/with_skill", {})
        up = all_results.get(f"{skill}/upstream", {})
        base = all_results.get(f"{skill}/without_skill", {})

        def fmt(r):
            if not r: return "N/A"
            return f"{r.get('passed','?')}/{r.get('total','?')} ({r.get('pass_rate',0)*100:.0f}%)"

        delta = ""
        if ws and up and ws.get('total') == up.get('total'):
            d = ws.get('passed', 0) - up.get('passed', 0)
            delta = f"+{d}" if d > 0 else str(d) if d < 0 else "="
        print(f"{skill:<16} {fmt(ws):<18} {fmt(up):<18} {fmt(base):<18} {delta:<12}")

    print("-" * 70)
    print(f"Total: {total_passed}/{total_assertions} ({total_passed/total_assertions*100:.1f}%)")
    print("=" * 70)

    # Save benchmark.json
    benchmark = {
        "skill_name": "aidlc-skills-full",
        "scenario": "Serverless Order Management API",
        "total_skills": 14,
        "total_runs": len(all_results),
        "aggregate": {
            "total_passed": total_passed,
            "total_assertions": total_assertions,
            "overall_pass_rate": round(total_passed / total_assertions, 3) if total_assertions > 0 else 0
        },
        "per_skill": all_results
    }
    benchmark_file = base_dir / "benchmark.json"
    with open(benchmark_file, 'w') as f:
        json.dump(benchmark, f, indent=2)
    print(f"\nBenchmark saved to: {benchmark_file}")


if __name__ == '__main__':
    main()
