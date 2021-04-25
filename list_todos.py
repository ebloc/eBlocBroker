# Helper method to dump project TODOs to stdout.
#
# Script can be stored anywhere, but should be run from the project
# root dir:
#     python tools/list_todos.py
#
# Sample output:
#
#    Current TODOs by category:
#
#    base (code fixes that will require some rearchitecting)
#
#    ./path/to/file.py (medium):  rest of comment
#
#    fix (code fixes)
#
#    ./other/file.py (high):  add config validation
#    ...

import fnmatch
import os
import re

# Types of todos:
# docs = documentation
# base = fundamental project changes/investigations
# nice = nice-to-have
TODO_TYPES = {
    "base": "code fixes that will require some rearchitecting",
    "fix": "code fixes",
    "docs": "documentation",
    "nice": "nice-to-haves",
}

PRIORITIES = {"high": "high", "med": "medium", "low": "low"}

# Config
ignore_dirs = ["./venv", "./.git", "./docs/_build", "./tools"]
ignore_file_exts = [".pyc"]
ignore_files = ["./docs/conf.py", "./README.md"]


def find_files(directory, pattern, ignore_dirs, ignore_file_exts):
    "Generator: find files, prune search tree during search."
    for root, subdirs, files in os.walk(directory):
        prune_subdirs = []
        for d in subdirs:
            if os.path.join(root, d) in ignore_dirs:
                prune_subdirs.append(d)

        for d in prune_subdirs:
            subdirs.remove(d)

        for basename in files:
            filename, ext = os.path.splitext(basename)
            if ext not in ignore_file_exts and fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                yield filename


def make_todo(filename, line):
    """Breaks a line up into a hash.

    expected TODO format: 'TODO type/priority: rest of line'"""

    header, rest = line.split(":")
    p = "medium"  # default
    for s in PRIORITIES:
        if re.search(s, header, re.IGNORECASE):
            p = PRIORITIES[s]
            break

    todo_type = ""
    for s in TODO_TYPES:
        if re.search(s, header, re.IGNORECASE):
            todo_type = s
            break

    hsh = {"filename": filename, "line": line.lstrip(" "), "priority": p, "type": todo_type, "rest": rest}
    return hsh


def collect_todos(filename):
    with open(filename, "r") as f:
        data = f.read()
    return [make_todo(filename, lin) for lin in data.split("\n") if re.search("todo", lin, re.IGNORECASE)]


def print_todos(all_todos):
    """Prints todos collected by make_todo."""

    def print_section(todo_type, todos):
        if len(todos) == 0:
            return
        desc = TODO_TYPES.get(todo_type, "uncategorized")
        print("\n{0} ({1})\n".format(todo_type, desc))
        for t in todos:
            print("  {0} ({1}): {2}".format(t["filename"], t["priority"], t["rest"]))

    for tt in ("base", "fix", "docs", "nice"):
        todos = [t for t in all_todos if t["type"] == tt]
        print_section(tt, todos)
        all_todos = [t for t in all_todos if t not in todos]

    print_section("remaining", all_todos)


# Output.

print("\nCurrent TODOs by category:")
todos = []
for filename in find_files(".", "*.*", ignore_dirs, ignore_file_exts):
    if filename not in ignore_files:
        todos.extend(collect_todos(filename))

print_todos(todos)
print
