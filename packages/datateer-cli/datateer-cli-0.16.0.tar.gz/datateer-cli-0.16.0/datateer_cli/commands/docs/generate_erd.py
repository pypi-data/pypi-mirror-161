import os
import pprint
import re

import yaml
from erd_python.parser import parse
from erd_python.render import render

searchdir = (
    r"./dbt/models"  # we search for .yml files in the /dbt/models folder in the project
)


def get_yml(searchdir):
    print(f"Searching for .yml files in: {searchdir}")
    yml_files = []
    count = 0
    for root, dirs, files in os.walk(searchdir):
        for name in files:
            (base, ext) = os.path.splitext(name)  # split base and extension
            if ext == ".yml":  # check the extension
                count += 1
                full_name = os.path.join(root, name)  # create full path
                yml_files.append(full_name)
                print(full_name)
    print(f"Total number of .yml files found: {count}")
    return yml_files


def get_model(searchdir):
    fct_tables = {}
    dim_tables = {}
    brg_tables = {}
    yml_files = get_yml(searchdir)
    for yml_file in yml_files:
        with open(yml_file) as f:
            core = yaml.load(f, Loader=yaml.FullLoader)
            if "models" not in core.keys():
                continue
            fct_models = [m for m in core["models"] if m["name"].startswith("fct_")]
            dim_models = [m for m in core["models"] if m["name"].startswith("dim_")]
            brg_models = [m for m in core["models"] if m["name"].startswith("brg_")]
            for model in fct_models:
                columns = model["columns"]
                relationships = []
                for c in columns:
                    tests = c.get("tests")
                    if tests is not None:
                        for t in tests:
                            if "relationships" in t:
                                related_table_name = re.search(
                                    r"ref\('(.*?)'\)", t["relationships"]["to"]
                                ).group(1)
                                relationships.append(
                                    {
                                        "table": related_table_name,
                                        "from_field": c["name"],
                                        "to_field": t["relationships"]["field"],
                                        # 'columns': [col['name'] for col in next(model for model in all_models if model['name'] == related_table_name)['columns']]
                                    }
                                )
                fct_tables[model["name"]] = {
                    "columns": [column["name"] for column in model["columns"]],
                    "relationships": relationships,
                }
            for model in brg_models:
                columns = model["columns"]
                relationships = []
                for c in columns:
                    tests = c.get("tests")
                    if tests is not None:
                        for t in tests:
                            if "relationships" in t:
                                related_table_name = re.search(
                                    r"ref\('(.*?)'\)", t["relationships"]["to"]
                                ).group(1)
                                relationships.append(
                                    {
                                        "table": related_table_name,
                                        "from_field": c["name"],
                                        "to_field": t["relationships"]["field"],
                                        # 'columns': [col['name'] for col in next(model for model in all_models if model['name'] == related_table_name)['columns']]
                                    }
                                )
                brg_tables[model["name"]] = {
                    "columns": [column["name"] for column in model["columns"]],
                    "relationships": relationships,
                }
            for model in dim_models:
                columns = model["columns"]
                dim_tables[model["name"]] = {
                    "columns": [column["name"] for column in model["columns"]]
                }

    return fct_tables, dim_tables, brg_tables


# flake8: noqa: C901
def generate(searchdir):
    fct_tables, dim_tables, brg_tables = get_model(searchdir)
    pp = pprint.PrettyPrinter(indent=2)
    # pp.pprint(fct_tables)

    if not os.path.exists("build"):
        os.makedirs("build")
    if not os.path.exists("build/erds"):
        os.makedirs("build/erds")
    if not os.path.exists("dbt/assets"):
        os.makedirs("dbt/assets/")
    if not os.path.exists("dbt/assets/erds"):
        os.makedirs("dbt/assets/erds")

    for name, metadata in fct_tables.items():
        print(name)
        fct_brg_tables = set()
        with open(f"build/erds/{name}.er", "w") as f:
            f.write("# The fact table\n")
            f.write(f"[{name}]\n")
            for c in metadata["columns"]:
                if f"{name[4:-1]}_id" == c:
                    f.write(f"*{c}\n")
                elif c.endswith("_id"):
                    f.write(f"+{c}\n")
                else:
                    f.write(f"{c}\n")
            f.write("\n# Related tables\n")

            for rel in metadata["relationships"]:
                if rel["table"].startswith("dim"):
                    dim_name = rel["table"]
                    if dim_name in dim_tables:
                        cols = dim_tables[dim_name]
                        f.write(f"[{dim_name}]\n")
                        for c in dim_tables[dim_name]["columns"]:
                            if f"{dim_name[4:-1]}_id" == c:
                                f.write(f"*{c}\n")
                            else:
                                f.write(f"{c}\n")
                elif rel["table"].startswith("brg"):
                    brg_name = rel["table"]
                    fct_brg_tables.add(brg_name)
                    if brg_name in brg_tables:
                        cols = brg_tables[brg_name]
                        f.write(f"[{brg_name}]\n")
                        for c in brg_tables[brg_name]["columns"]:
                            if f"{brg_name[4:-1]}_id" == c:
                                f.write(f"*{c}\n")
                            else:
                                f.write(f"{c}\n")
                        for r in brg_tables[brg_name]["relationships"]:
                            print(r)
                            brg_dim_name = r["table"]
                            if brg_dim_name in dim_tables:
                                cols = dim_tables[brg_dim_name]
                                f.write(f"[{brg_dim_name}]\n")
                            for c in dim_tables[brg_dim_name]["columns"]:
                                if f"{brg_dim_name[4:-1]}_id" == c:
                                    f.write(f"*{c}\n")
                                else:
                                    f.write(f"{c}\n")

                f.write("\n")

            f.write("\n# Relationships\n")
            for rel in metadata["relationships"]:
                if rel["table"].startswith("dim"):
                    f.write(
                        f"{name}:{rel['from_field']} *--1 {rel['table']}:{rel['to_field']}\n"
                    )
                elif rel["table"].startswith("brg"):
                    f.write(
                        f"{name}:{rel['from_field']} *--* {rel['table']}:{rel['to_field']}\n"
                    )
                print(rel)
            for table_name in fct_brg_tables:
                if table_name in brg_tables:
                    for rel in brg_tables[table_name]["relationships"]:
                        f.write(
                            f"{table_name}:{rel['from_field']} *--1 {rel['table']}:{rel['to_field']}\n"
                        )
                        print(rel)

        with open(f"build/erds/{name}.er") as f:
            data = f.read()
            objects = parse(data)
            render(objects, f"dbt/assets/erds/{name}.png", "png")
            render(objects, f"build/erds/{name}.dot", "dot")
