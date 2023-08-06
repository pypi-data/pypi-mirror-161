import platform
import re
from pathlib import Path

import certifi
import pkg_resources


def create(output_path, solution):
    spec_path = Path(output_path).joinpath('build_executable.spec')
    yml_path = repr(str(Path(output_path).joinpath('album.yml')))
    hook_path = repr(str(Path(pkg_resources.resource_filename('album.package.resources.installer', 'install_all.py'))))
    call_sol_path = repr(str(Path(output_path).joinpath('call_solution.py')))
    run_sol_path = repr(
        str(pkg_resources.resource_filename('album.package.resources.templates', 'run_solution.template')))
    run_sol_gui_path = repr(
        str(pkg_resources.resource_filename('album.package.resources.templates',
                                            'run_solution_gui.template')))
    uninstall_sol_path = repr(
        str(pkg_resources.resource_filename('album.package.resources.templates',
                                            'uninstall_solution.template')))
    uninstall_sol_gui_path = repr(
        str(pkg_resources.resource_filename('album.package.resources.templates',
                                            'uninstall_solution_gui.template')))
    if platform.system() == 'Windows':
        icon_path = repr(str(pkg_resources.resource_filename('album.package.resources.icons', 'album_icon_windows.ico')))
        cert_path = repr(str(Path(certifi.where())))

    elif platform.system() == 'Darwin':
        icon_path = repr(str(pkg_resources.resource_filename('album.package.resources.icons', 'album_icon_macos.icns')))
        cert_path = repr(str(Path(certifi.where())))

    elif platform.system() == 'Linux':
        icon_path = repr(str(pkg_resources.resource_filename('album.package.resources.icons', 'album_icon_linux.png')))
        cert_path = repr(str(Path(certifi.where())))
    else:
        print("Your OS is currently not supported")
        raise NotImplementedError

    if Path(solution).is_dir():
        solution_path = repr(str(Path(solution).joinpath('*')))
    if Path(solution).is_file():
        solution_path = repr(str(Path(solution)))

    with open(pkg_resources.resource_filename('album.package.resources.templates',
                                              'build_executable_spec.template'), 'r') as file:
        template_str = file.read()

    tmp = re.sub(r"\\", r"\\\\", yml_path)
    template_str = re.sub("<yml_path>", tmp, template_str)
    tmp = re.sub(r"\\", r"\\\\", solution_path)
    template_str = re.sub("<solution_path>", tmp, template_str)
    tmp = re.sub(r"\\", r"\\\\", hook_path)
    template_str = re.sub("<hook_path>", tmp, template_str)
    tmp = re.sub(r"\\", r"\\\\", run_sol_path)
    template_str = re.sub("<run_sol_path>", tmp, template_str)
    tmp = re.sub(r"\\", r"\\\\", run_sol_gui_path)
    template_str = re.sub("<run_sol_gui_path>", tmp, template_str)
    tmp = re.sub(r"\\", r"\\\\", uninstall_sol_path)
    template_str = re.sub("<uninstall_sol_path>", tmp, template_str)
    tmp = re.sub(r"\\", r"\\\\", uninstall_sol_gui_path)
    template_str = re.sub("<uninstall_sol_gui_path>", tmp, template_str)
    tmp = re.sub(r"\\", r"\\\\", icon_path)
    template_str = re.sub("<icon>", tmp, template_str)
    tmp = re.sub(r"\\", r"\\\\", call_sol_path)
    template_str = re.sub("<call_sol_path>", tmp, template_str)
    tmp = re.sub(r"\\", r"\\\\", cert_path)
    template_str = re.sub("<cert_path>", tmp, template_str)

    with open(spec_path, 'w') as file:
        file.write(template_str)

    return spec_path
