"""
Script to auto-generate TESTS.md with all test harnesses and descriptions in the repo.
Scans for test files and extracts test functions/classes and docstrings.
"""
import os
import ast
from pathlib import Path

def find_test_files(root):
    for dirpath, _, filenames in os.walk(root):
        for fname in filenames:
            if fname.startswith('test_') and fname.endswith('.py'):
                yield Path(dirpath) / fname
            if fname.endswith('.test.tsx') or fname.endswith('.test.js'):
                yield Path(dirpath) / fname

def extract_py_tests(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read(), filename=str(file_path))
    tests = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith('test'):
            doc = ast.get_docstring(node) or ''
            tests.append((node.name, doc))
        if isinstance(node, ast.ClassDef) and node.name.startswith('Test'):
            doc = ast.get_docstring(node) or ''
            tests.append((node.name, doc))
    return tests

def extract_js_tests(file_path):
    # Simple extraction for describe/it blocks
    tests = []
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if 'describe(' in line or 'it(' in line:
            desc = line.strip()
            tests.append((f"Line {i+1}", desc))
    return tests

def main():
    root = Path('.')
    test_files = list(find_test_files(root))
    output = ['# Test Harnesses and Descriptions\n']
    for file in test_files:
        output.append(f"## {file.relative_to(root)}\n")
        if file.suffix == '.py':
            tests = extract_py_tests(file)
        else:
            tests = extract_js_tests(file)
        if tests:
            for name, doc in tests:
                output.append(f"- **{name}**: {doc if doc else 'No description'}\n")
        else:
            output.append("- No test functions found\n")
    with open('TESTS.md', 'w', encoding='utf-8') as f:
        f.writelines(output)
    print("TESTS.md generated with all test harnesses.")

if __name__ == "__main__":
    main()
