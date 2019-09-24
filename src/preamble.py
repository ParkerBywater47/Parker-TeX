import re


# noinspection RegExpRedundantEscape
def packages_parser(source_str):
    """
    Searches for packages[] command. This has its own parser because packages may be loaded with optional args, which
    requires different parsing
    :param source_str:
    :return: appropriate laTeX code
    """
    # print("source_str:\n" + source_str)
    # try to find the word 'packages'
    packages_start = source_str.find('packages')

    # if 'packages' is somewhere in the string
    if packages_start > 0:
        # if 'packages' is not the first word in the string, the character before must be whitespace and 'begin[document]'
        # cannot be found before source_str[packages_start]
        if re.match('[^\w\d]+', source_str[packages_start - 1]):
            # find the args_string of packages[<args_string>]
            match = re.match("[ \t]*\[", source_str[packages_start + len('packages'):])
            if match:
                work_str = source_str[packages_start + len('packages'):] # this is [geom[<options>], soul] type deal
                if match.end() < len(work_str):
                    rights_found = 0
                    rights_to_find = 1
                    i = match.end() - 1
                    while rights_found < rights_to_find and i < len(work_str) - 1:
                        i += 1
                        current_char = work_str[i]
                        if current_char == '[':
                            rights_to_find += 1
                            i += 1
                        elif current_char == ']':
                            rights_found += 1
                    pack_str = generate_packages_string(work_str[match.end():i])
                    # print("pack_str:\n" + pack_str)
                    # print("the string returned by the function:\n" + source_str[:packages_start] + pack_str +
                    #       work_str[i + 1:])
                    return source_str[:packages_start] + pack_str + work_str[i + 1:]
                else:
                    # unexpected EOF while parsing error
                    pass
            else:
                # invalid. generate compiler error
                pass
        else:
            # conclude that this is not a package declaration, rather the word 'package'
            pass

    # if packages is the first word in the string
    elif packages_start == 0:
        if re.match('\s*=\s*\[([^%]*)\]', source_str[packages_start + len('packages'):]):
            # valid
            pass
        else:
            # invalid. generate compiler error
            pass
    # packages found nowhere
    return source_str


def generate_packages_string(packages_str):
    """
    Generates the LaTeX code for the packages in packages_str
    :param packages_str: a comma separated list of package names
    """
    # Check for case when no packages are loaded with options
    out_str = ""
    if '[' not in packages_str:
        packages_lst = packages_str.split(",")
        for i in packages_lst:
            out_str += '\\usepackage{' + i.strip() + '}\n'
    else:
        i = 0
        j = 0
        packages_str += ','
        while i < len(packages_str) and j < len(packages_str):
            if packages_str[j] != '[' and packages_str[j] != ',':
                j += 1
            elif packages_str[j] == ',':
                # print('\\usepackage{' + packages_string[i:j].strip() + '}\n', end='')
                out_str += ('\\usepackage{' + packages_str[i:j].strip() + '}\n')
                i = j + 1
                j = i
            else:  # when packages_string[j] == '[':
                rsb = packages_str.find(']', j)
                if rsb == -1:
                    print(
                        'Missing or extra right bracket (]) somewhere in your packages list?\nYour list of packages: '
                        + packages_str)
                    return -101
                else:
                    # print('\\usepackage' + packages_string[j:rsb + 1] + '{' + packages_string[i:j].strip() + '}\n', end='')
                    out_str += r'\usepackage' + '\\' + packages_str[j:rsb] + r'\]{' + packages_str[i:j].strip() + '}\n'
                    for i in range(rsb + 1, len(packages_str)):
                        if packages_str[i] == ',':
                            i += 1
                            j = i
                            break
    return out_str


def do_doc_class(source_file):
    """
    Reads lines from input file until documentclass[<class>] is found or EOF is reached.
    :param  source_file: file to be read
    :param  out_file: file to be written
    :return
    """
    line_no = 1
    out_string = ""
    found_doc_class = False
    for line in source_file:
        if not found_doc_class:
            match_obj = re.match('\s*documentclass *\[([\w\d]*)\]', line)
            if match_obj is not None:
                # determine the document class and check that it's not blank
                doc_class = match_obj.group(1)
                if not doc_class == '':
                    out_string += '\documentclass{' + doc_class + '}\n' + line[match_obj.end():]
                    found_doc_class = True
                else:
                    print("Error: \'documentclass\' command with no class specified\nline "
                          + str(line_no) + ": " + line)
            else:
                if re.match('( )*documentclass( )*.*\]', line):
                    print("Error: Missing or extra left bracket ([)?\nline " + str(line_no) + ": " + line)
                    return -3
                elif re.match('( )*documentclass( )*\[.*', line):
                    print("Error: Missing or extra right bracket (])?\nline " + str(line_no) + ": " + line)
                    return -3
                elif 'newcommand' not in line:
                    print(
                        'Error: document class declaration must be the first non-empty line in the file (with the exception of '
                        'command definitions)\nline ' + str(line_no) + ': ' + line)
                    return -4
                else:
                    print("not quite sure what's not right at this point")
        else:
            out_string += line
        line += 1

    if not found_doc_class:
        print("No document class found")
        # This will raise an exception to return to its caller in the future
        return
    return out_string



