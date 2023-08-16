from pathlib import Path
from typing import List

import re

import clvm_tools_rs

CRE = re.compile(r"\((\s)*include(\s)+(.+)\)")


def find_included_items(item: Path) -> List[Path]:
    contents = item.read_text()
    matches = CRE.findall(contents)
    included = []
    for match in matches:
        s = match[-1]
        if len(s) > 1 and s[0] == s[-1] and s[0] in "'\"":
            included.append(s[1:-1])
        else:
            included.append(s)
    return included


def calculate_dependencies(source_path: Path, include_paths: List[Path]) -> List[Path]:
    include_paths = [Path(_) for _ in include_paths]
    dependencies = set()
    to_check = [source_path]
    while len(to_check):
        item = to_check.pop()
        if item in dependencies:
            continue
        dependencies.add(item)
        included_items = find_included_items(item)
        for include_item in included_items:
            for include_path in include_paths:
                p = include_path / include_item
                if p.exists():
                    to_check.append(p)
    return dependencies


class ChialispBuild:
    def __init__(self, include_paths: List[Path] = []):
        self.include_paths = include_paths
        self.include_paths_as_str = [str(_) for _ in include_paths]

    def __call__(self, target_path: Path):
        source_path = target_path.with_suffix(".clsp")

        dependencies = calculate_dependencies(source_path, self.include_paths)
        latest_date = max(_.stat().st_mtime for _ in dependencies)

        if not target_path.exists() or target_path.stat().st_mtime < latest_date:
            # we need to rebuild
            if target_path.exists():
                # `compile_clvm` doesn't always replace existing files as of 0.1.34
                target_path.unlink()
            source_path_str, target_path_str = str(source_path), str(target_path)
            clvm_tools_rs.compile_clvm(
                source_path_str, target_path_str, self.include_paths_as_str
            )
