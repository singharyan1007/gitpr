from app.domain.checks import run_all_checks


def test_flags_todo():
    diff = "+++ b/x.py\n+# TODO: fix this\n"
    findings = run_all_checks(diff)
    assert any("TODO" in f.message for f in findings)


def test_flags_large_diff():
    diff = "+++ b/x.py\n" + "\n".join(f"+line {i}" for i in range(600))
    findings = run_all_checks(diff)
    assert any("Large PR" in f.message for f in findings)


def test_flags_print_debugging():
    diff = "+++ b/x.py\n+print('debugging')\n"
    findings = run_all_checks(diff)
    assert any("debug print" in f.message.lower() for f in findings)


def test_clean_diff_has_no_findings():
    diff = "+++ b/x.py\n+def add(a, b):\n+    return a + b\n"
    assert run_all_checks(diff) == []
