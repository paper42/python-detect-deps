#!/usr/bin/env python3
import pkgutil
import os
import sys
from typing import List, Any

def deduplicate(lst: List[Any]) -> List[Any]:
    dedup_lst = []
    for item in lst:
        if item not in dedup_lst:
            dedup_lst.append(item)
    return dedup_lst

def get_internal_modules() -> List[str]:
    items = list(sys.builtin_module_names)
    items += os.listdir(f"/usr/lib/python{sys.version_info.major}.{sys.version_info.minor}/")
    dynlibs = os.listdir(f"/usr/lib/python{sys.version_info.major}.{sys.version_info.minor}/lib-dynload")
    for dynlib in dynlibs:
        items.append(dynlib.split(".")[0])
    modules = []
    for item in items:
        if item == "site-packages":
            continue
        name = item
        if item.endswith(".py"):
            name = item[:-3]
        elif os.path.isdir(item):
            name = item
        modules.append(name)
    return modules

def process_file(path: str, internal_modules: List[str]) -> List[str]:
    text = ""
    with open(path, "r") as f:
        text = f.read()

    modules = []
    for raw_line in text.split("\n"):
        if len(raw_line) == 0:
            continue
        line = raw_line.strip().split()
        if len(line) == 0:
            continue
        if line[0] == "import":
            modules += line[1:]
        elif line[0] == "from":
            modules.append(line[1])

    external_modules = []
    for module in modules:
        # strip "," because import a, b, c is valid
        # TODO: import a.b might be from a different projects than import a
        if module == "":
            continue
        module_name = module.strip(",").split(".")[0]
        if module_name == "":
            continue
        if module_name not in internal_modules:
            external_modules.append(module_name)
    return external_modules

def process_dir(path: str, internal_modules: List[str]) -> List[str]:
    external_modules = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if not name.endswith(".py"):
                continue
            external_modules += process_file(os.path.join(root, name),
                                             internal_modules=internal_modules)
        for name in dirs:
            external_modules += process_dir(os.path.join(root, name),
                                            internal_modules=internal_modules)
    return external_modules

def process(path: str, internal_modules: List[str]) -> List[str]:
    if os.path.isdir(path):
        return process_dir(path=path, internal_modules=internal_modules)
    return process_file(path=path, internal_modules=internal_modules)

def cli() -> None:
    internal_modules = get_internal_modules()
    external_modules = []
    for arg in sys.argv[1:]:
        external_modules += process(path=arg,
                                    internal_modules=internal_modules)

    for module in deduplicate(external_modules):
        print(module)


if __name__ == '__main__':
    cli()
