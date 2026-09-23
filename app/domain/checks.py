# A list of functions to perform a list of checks on the incoming github diff
# All of the checklists are performing independent checks so scalability will not be an issue
"""
For now I will write only the basic checks like TODO, Large PR, print debugging etc. Later on we can add more checks like checking for the presence of docstrings, checking for the presence of type hints, checking for the presence of logging, checking for the presence of error handling, checking for the presence of tests, checking for the presence of comments, checking for the presence of code smells, checking for the presence of security vulnerabilities, checking for the presence of performance issues, checking for the presence of code duplication and other programming jargons.
"""

from dataclasses import dataclass
from typing import Callable

from app.domain.diff import parse_diff


@dataclass
class Finding:
    severity : str # "info"|"warning"|"severity"
    message :  str

CheckFn = Callable[[str], list[Finding]] #CheckFn is a function that takes a string and returns a list of Finding objects.

_Registry :list[CheckFn] = []   #list of such functions 
"""
_since these CheckFn are bunch of rules in the name of functions, so _Registry is just a list of such rules for the tool to keep in mind while reviewing a PR
"""

def check(fn:CheckFn) -> CheckFn:
    """
    Decorator to register a check function. 
    You may ask why returning the function? Well, simply because we dont want the decorator to destroy/replace the original function.
    """
    _Registry.append(fn)
    return fn

def run_all_checks(diff:str) -> list[Finding]:

    """
    Run all registered checks on the given diff and return a list of findings.
    """
    findings:list[Finding] = []
    for check_fn in _Registry:
        findings.extend(check_fn(diff))
    return findings


def format_findings(findings: list[Finding]) -> str:
    if not findings:
        return "Automated review: no issues found."
    lines = ["### Automated review findings", ""]
    lines += [f"- [{f.severity}] {f.message}" for f in findings]
    return "\n".join(lines)


@check
def check_todo_comments(diff:str) -> list[Finding]:
    """
    Check for TODO comments in the diff.
    """
    hits=[l for f in parse_diff(diff)
          for l in f.added_lines if "TODO" in l or "todo" in l or "ToDo" in l or "FIXME" in l or "fixme" in l or "FixMe" in l]

    return [Finding("warning",f"{len(hits)} new TODO/FIXME comments added")] if hits else []


@check
def check_large_diff(diff:str) -> list[Finding]:
    """
    Check for large diffs. If the diff has more than 500 lines, it is considered large.
    """
    added_lines = sum(len(f.added_lines) for f in parse_diff(diff))
    if added_lines > 500:
        return [Finding("warning", f"Large PR: {added_lines} added lines")]
    return []



@check
def no_print_debugging(diff: str) -> list[Finding]:
    hits = [
        l
        for f in parse_diff(diff)
        for l in f.added_lines
        if "print(" in l or "console.log(" in l
    ]

    return [
        Finding(
            "info",
            f"{len(hits)} debug print statement(s) in new code"
        )
    ] if hits else []










