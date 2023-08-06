import re
import shutil

from pathlib import Path
from album import core

import pkg_resources


def create(output_path, coordinates):
    create_yml(output_path)
    create_execution_entrypoint(output_path)
    create_call_solution(output_path, coordinates)


def create_yml(output_path):
    yml_path = Path(output_path).joinpath('album.yml')
    with open(pkg_resources.resource_filename('album.package.resources.templates', 'album.yml'), 'r') as file:
        template_str = file.read()
    template_str = re.sub("<version>", core.__version__, template_str)
    with open(yml_path, 'w') as file:
        file.write(template_str)


def create_execution_entrypoint(output_path):
    entrypoint_path = Path(output_path).joinpath('execution_entrypoint.py')
    shutil.copy(pkg_resources.resource_filename('album.package.resources.templates', 'execution_entrypoint.template'),
                entrypoint_path)


def create_call_solution(output_path, coordinates):
    with open(pkg_resources.resource_filename('album.package.resources.templates', 'call_solution.template'),
              'r') as file:
        template_str = file.read()
    template_str = re.sub("<coordinates>", str(coordinates), template_str)
    with open(Path(output_path).joinpath('call_solution.py'), 'w') as file:
        file.write(template_str)
