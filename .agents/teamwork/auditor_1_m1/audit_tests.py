import ast
import re
from pathlib import Path

REPO_ROOT = Path("d:/pivot-edu-kdp/pivot-digital-edu-kdp")
TESTS_DIR = REPO_ROOT / "tests"

def audit_tests_directory():
    print("=== AUDITING TESTS DIRECTORY FOR CIRCUMVENTION & MOCKS ===")
    test_files = list(TESTS_DIR.glob("**/*.py"))
    print(f"Total test files found: {len(test_files)}")

    findings = []

    for tfile in test_files:
        rel_path = tfile.relative_to(REPO_ROOT)
        content = tfile.read_text(encoding="utf-8")

        # 1. Search for skip decorators or skip calls
        skips = re.findall(r"(@unittest\.skip[a-zA-Z0-9_]*|self\.skipTest\([^)]*\))", content)
        if skips:
            findings.append((str(rel_path), "SKIP_DETECTED", skips))

        # 2. Search for mock usage
        mocks = re.findall(r"(mock\.patch|MagicMock|unittest\.mock)", content)
        if mocks:
            findings.append((str(rel_path), "MOCK_DETECTED", mocks))

        # 3. Parse AST for suspicious patterns: empty test methods, test methods with only `pass` or `assert True`
        try:
            tree = ast.parse(content, filename=str(tfile))
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                    # Check if body is just pass or return
                    if len(node.body) == 1:
                        stmt = node.body[0]
                        if isinstance(stmt, ast.Pass):
                            findings.append((str(rel_path), f"EMPTY_TEST: {node.name}", "body is pass"))
                        elif isinstance(stmt, ast.Return):
                            findings.append((str(rel_path), f"NOOP_TEST: {node.name}", "body is return"))
                    # Check for assert True or self.assertTrue(True)
                    for stmt in node.body:
                        if isinstance(stmt, ast.Assert):
                            if isinstance(stmt.test, ast.Constant) and stmt.test.value is True:
                                findings.append((str(rel_path), f"VACUOUS_ASSERT: {node.name}", "assert True"))
                        elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                            call = stmt.value
                            if isinstance(call.func, ast.Attribute) and call.func.attr == "assertTrue":
                                if call.args and isinstance(call.args[0], ast.Constant) and call.args[0].value is True:
                                    findings.append((str(rel_path), f"VACUOUS_ASSERT_TRUE: {node.name}", "assertTrue(True)"))
        except Exception as e:
            findings.append((str(rel_path), "AST_PARSE_ERROR", str(e)))

    if not findings:
        print("PASS: Zero suspicious skips, dummy pass/return tests, or vacuous assertions found in tests/.")
    else:
        print(f"Items to review in tests/ ({len(findings)}):")
        for f in findings:
            print(f"  {f[0]}: [{f[1]}] -> {f[2]}")

if __name__ == "__main__":
    audit_tests_directory()

