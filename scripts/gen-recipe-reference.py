#!/usr/bin/env python3
"""Generate the recipe verb reference from KARMAX's source.

The verbs, which of them return a value, and which fields each requires are
facts about internal/recipes/recipe.go. Copying them into prose means the
documentation is correct until somebody adds a verb, and silently wrong after
that — so it is generated instead.

    ./scripts/gen-recipe-reference.py ~/code/KARMAX > karmax/dev/recipes-reference.mdx
"""

import re
import sys
from pathlib import Path


def main() -> None:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    src = (root / "internal/recipes/recipe.go").read_text()

    # Verb constants carry their own one-line description as a trailing comment.
    verbs = dict(re.findall(r'Verb\w+\s*=\s*"(\w+)"\s*//\s*(.+)', src))

    returns = set(
        re.findall(r"Verb(\w+)", re.search(
            r"func storesResult\(verb string\) bool \{.*?case (.*?):", src, re.S).group(1)))
    returns = {v.lower() for v in returns}

    required: dict[str, list[str]] = {}
    block = re.search(r"var required = map\[string\]\[\]string\{(.*?)\n\}", src, re.S).group(1)
    for verb_const, fields in re.findall(r"Verb(\w+):\s*\{(.*?)\}", block):
        required[verb_const.lower()] = re.findall(r'"(\w+)"', fields)

    print("---")
    print("title: Recipe reference")
    print("description: 'Every verb, what it needs, and what it returns.'")
    print('icon: "list-check"')
    print("---")
    print()
    print("Generated from `internal/recipes/recipe.go`, so it cannot drift from what")
    print("KARMAX actually accepts.")
    print()
    print("| Verb | Does | Required fields | Returns |")
    print("|---|---|---|---|")
    for verb, desc in verbs.items():
        req = ", ".join(f"`{f}`" for f in required.get(verb, [])) or "—"
        ret = "yes" if verb in returns else "no"
        print(f"| `{verb}` | {desc.strip()} | {req} | {ret} |")
    print()
    print("Only the verbs that return something can be bound with `as`.")


if __name__ == "__main__":
    main()
