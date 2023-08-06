"""Run this script to create or refresh your developer environment

Installs a virtual environment with the main requirements at venv, one at venv/dbt, and one at venv/meltano. The root (venv) can be changed by passing an argument e.g. "python requirements/developer_setup.py my_venv_root"
"""
import glob
import os
import re
import shutil
import subprocess
import sys
import venv

import pip

# REQUIREMENTS_DIR = 'requirements'
# SUB_VENVS = ['', 'dbt', 'meltano']


def setup(venv_root="venv", requirements_dir="requirements"):
    """Installs virtual environments in the venv folder"""
    if os.path.exists(venv_root):
        print(f"Path {venv_root} already exists; deleting")
        remove_directory(venv_root)

    builder = venv.EnvBuilder(clear=True, with_pip=True)

    # install requirements.txt and requirements-dev.txt in the main venv
    print()
    print(f">>>> creating virtual environment at {venv_root} <<<<")
    builder.create(os.path.join(venv_root))
    pip_install(venv_root, "", ["pip", "setuptools", "wheel"])
    pip_install(venv_root, "", ["-e", "."])
    if os.path.exists(os.path.join(requirements_dir, "requirements-dev.txt")):
        pip_install_requirements(
            venv_root, "", os.path.join(requirements_dir, "requirements-dev.txt")
        )

    # get the remaining requirements files
    sub_venvs = list(
        set(glob.glob(os.path.join(requirements_dir, "requirements-*.txt")))
        - set(glob.glob(os.path.join(requirements_dir, "requirements-dev.txt*")))
    )
    for req_filename in sub_venvs:
        m = re.search("requirements-(.*).txt", req_filename)
        venv_name = m.group(1)

        print()
        print(f">>>> creating sub virtual environment {venv_name} at {venv_root} <<<<")
        builder.create(os.path.join(venv_root, venv_name))
        pip_install(venv_root, venv_name, ["pip", "setuptools", "wheel"])
        pip_install_requirements(venv_root, venv_name, req_filename)


def remove_directory(dir):
    if os.name == "nt":
        os.system(f'rmdir /S /Q "{dir}"')
    else:
        shutil.rmtree(dir)


def executable_path(venv_root, venv_name):
    if os.name == "nt":
        return os.path.join(venv_root, venv_name, "scripts/python.exe")
    else:
        return os.path.join(venv_root, venv_name, "bin/python")


def pip_install_requirements(venv_root, venv_name, requirements_file, verbosity=0):
    """pip install a requirements file"""
    print()
    print(f">>>> installing {requirements_file} into venv {venv_root}/{venv_name}")
    command = [
        executable_path(venv_root, venv_name),
        "-m",
        "pip",
        "install",
        "-r",
        requirements_file,
    ]
    # append verbosity flag if included. e.g. verbosity=3 results in "-vvv"
    if verbosity is not None and 0 < verbosity:
        vs = ["v" for level in range(2)]
        command.append("-" + str.join("", vs))
    subprocess.run(command)


def pip_install(venv_root, venv_name, package_names, upgrade=True):
    """pip install a set of packages"""
    command = [
        executable_path(venv_root, venv_name),
        "-m",
        "pip",
        "install",
    ] + package_names
    if upgrade:
        command.append("--upgrade")
    print(f"Running {command} in {os.getcwd()}")
    subprocess.run(command)


if __name__ == "__main__":
    if 1 < len(sys.argv):
        setup(sys.argv[0], sys.argv[1])
    else:
        setup()
