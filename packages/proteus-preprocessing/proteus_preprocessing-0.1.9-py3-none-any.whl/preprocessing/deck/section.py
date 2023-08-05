import re
import os


def get_includes(input_file_loc, download_func=None):
    with open(input_file_loc, "r") as data_file:
        content = data_file.read()
    # recursively finds the include files
    abs_path = os.path.abspath(input_file_loc)
    return find_includes(content, abs_path, download_func)


def find_section(input_file_loc, section_header, download_func=None):
    file_list = [input_file_loc] + get_includes(input_file_loc, download_func)

    for file_loc in file_list:
        with open(file_loc, "r") as f:
            section = scan_file(f.read(), section_header)
            if section is not None:
                return section.group("content")


def parse_dependency_path(file_absolute_path, dependency):
    """Parse relative dependencies path to absolute ones
    Arguments:
        file_absolute_path {string} -- the absolute file path
        dependency {string} -- the relative path of the dependency
    Returns:
        absolute_dependency {string} -- the absolute path of the dependency
    """
    file_name_expression = re.compile(r"/(?P<file_name>[^/]+\.[^/]+)$")

    # Split directories by folders. Create a list with the folders
    file_name = file_name_expression.search(file_absolute_path).group()
    file_path = file_absolute_path.replace(file_name, "")
    file_path_list = file_path.split("/")

    # Count and remove previous directories: ../
    previous_directories_expression = re.compile(r"(?P<previous_directories>(\.\./)|(\.\.\\))")
    previous_directories = previous_directories_expression.finditer(dependency)
    previous_directories = [
        previous_directory.groupdict().get("previous_directories") for previous_directory in previous_directories
    ]
    number_of_previous_directories = len(previous_directories)
    dependency_name = dependency.replace("../", "").replace("..\\", "")

    # Remove `./` just in case
    dependency_name = dependency_name.replace("./", "")

    # Create absolute path
    list_length = len(file_path_list)
    file_path_list = file_path_list[: list_length - number_of_previous_directories]
    return f"{'/'.join(file_path_list)}/{dependency_name}".replace("\\", "/")


def find_includes(content, filepath, download_func=None):
    include_expression_re = re.compile(r"\s*INCLUDE[^\'\/]+'(?P<path>[^']+)'")
    inc_found = include_expression_re.finditer(content)
    includes_list = [inc.groupdict().get("path") for inc in inc_found]
    fixed_includes_list = []
    for include_file_loc in includes_list:
        actual_path = parse_dependency_path(filepath, include_file_loc)
        fixed_includes_list.append(actual_path)
        try:
            if download_func:
                relative_path = remove_tmp_folder(actual_path)
                download_func(relative_path, actual_path)
            with open(actual_path, "r") as include_file:
                content = include_file.read()

            fixed_includes_list += find_includes(content, actual_path, download_func)
        except Exception as e:
            print(e)

    return fixed_includes_list


def scan_file(content, section_header):
    section_expression_re = re.compile(
        section_header + r"\s+=*(?P<content>[\S\s]*?)(RUNSPEC|GRID|PROPS|REGIONS|SOLUTIONS|SUMMARY|SCHEDULE)\s"
    )
    section_found = section_expression_re.finditer(content)

    section_content = next(section_found)
    if section_content is not None:
        return section_content


def remove_tmp_folder(path):
    path_expression_re = re.compile(r"^\/tmp\/tmp[^\/]*(?P<path>.*)$")
    path_found = path_expression_re.finditer(path)
    try:
        return next(path_found).groupdict().get("path")
    except StopIteration:
        return None
