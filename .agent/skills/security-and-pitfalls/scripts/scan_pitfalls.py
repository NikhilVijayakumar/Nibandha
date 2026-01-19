import ast
import sys
from pathlib import Path


class SecurityAuditor(ast.NodeVisitor):
    def __init__(self, filename):
        self.filename = filename
        self.violations = []

    def visit_FunctionDef(self, node):
        # Pitfall 4: Mutable Default Arguments
        for arg in node.args.defaults:
            if isinstance(arg, (ast.List, ast.Dict)):
                self.violations.append(
                    f"❌ {self.filename}:{node.lineno} - Mutable default argument detected in '{node.name}'.")
        self.generic_visit(node)

    def visit_Call(self, node):
        # Pitfall 3: Subprocess shell=True
        if isinstance(node.func, ast.Attribute) and node.func.attr == 'run':
            for keyword in node.keywords:
                if keyword.arg == 'shell' and isinstance(keyword.value, ast.Constant) and keyword.value.value is True:
                    self.violations.append(
                        f"❌ {self.filename}:{node.lineno} - Insecure subprocess call with shell=True.")

        # Pitfall 1: Manual file open without 'with'
        if isinstance(node.func, ast.Name) and node.func.id == 'open':
            # Check if it's inside a 'with' statement
            parent = getattr(node, 'parent', None)
            if not isinstance(parent, ast.With):
                self.violations.append(
                    f"⚠️ {self.filename}:{node.lineno} - Manual open() found. Use 'with' context manager.")
        self.generic_visit(node)


def audit_file(path: Path):
    tree = ast.parse(path.read_text())
    # Add parent links to nodes for context checking
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child.parent = node

    auditor = SecurityAuditor(path.name)
    auditor.visit(tree)
    return auditor.violations


if __name__ == "__main__":
    src_files = list(Path("src").glob("**/*.py"))
    all_violations = []
    for f in src_files:
        all_violations.extend(audit_file(f))

    if all_violations:
        for v in all_violations: print(v)
        sys.exit(1)
    print("✅ Security Audit Passed: No common pitfalls detected.")