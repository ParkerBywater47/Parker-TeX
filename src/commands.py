import os
from preamble import *
import environments

SLASH_ITEM_COMMANDS = {"item", "question"}
NASTY_ENVIRONMENTS = {'align', 'align*', 'equation', 'equation*', 'multline', 'multline*',
                      'gather', 'gather*', 'flalign', 'flalign*'}

def main_parser(string):
    """
    This parser is kind of the driver of the whole "compiler". It uses ']' characters as markers for commands.
    Let the index of a ']' which was just found be j. The next step undertaken by the compiler is to search for '['
    characters occuring before j. As '[' are found, the indices are stored for later use in lsb_indices.
    Let the index of the lsb closest to j be i.

    Upon finding the lsb at index i, the compiler searches backwards until a whitespace character is found. The character
    immediately following this whitespace character is considered to be the beginning of the command name while the ending
    is the character at i-1.

    The string sliced between indices i and j is then checked for a match to whitespace characters. If this is a match,
    the compiler checks if the command name is "end" as this can have an empty argument string, but needs to be parsed
    differently than other commands with empty arguments.

    :param string: the source string to be compiled
    :return: the "compiled" string
    """
    string = packages_parser(string)
    environments_stack = []
    rsb = find_brace(']', string)
    while rsb != -1:
        lsb_indices = []
        lsb = find_brace('[', string)

        # do some syntax checking
        if lsb == -1 and rsb == -1:
            print("Syntax error: Missing a '[' or ']'")
            return
        elif rsb == -1:
            print("Syntax error: Missing a ']'")
            return
        elif lsb == -1:
            print("Syntax error: Missing a '['")
            return
        else:
            while lsb != -1 and rsb != -1:
                lsb_indices.append(lsb)
                lsb = find_brace('[', string, lsb + 1, rsb)

            while len(lsb_indices) != 0:
                lsb = lsb_indices.pop()
                rsb = find_brace(']', string, lsb + 1)
                name = get_command_name(string, lsb - 1)
                name_start = lsb - len(name)

                # check for a simple command such as implies[]
                if re.match('\[\s*\]', string[lsb:rsb + 1]):
                    if name == "end":
                        # if len(environments_stack) == 0:
                        #     print("breakpoint")
                        env_name = environments_stack.pop()
                        if env_name in NASTY_ENVIRONMENTS:
                            string = end_parser(string, name_start)

                        string = string[:name_start] + "\\" + string[name_start:lsb] + "{" + env_name + "}" \
                             + string[rsb + 1:]
                    else:
                        string = string[:name_start] + '\\' + name + string[rsb + 1:]
                else:
                    if name == "begin":
                        # try:
                        string = string[:name_start] + "\\" + string[name_start:lsb] \
                                 + environments.begin_env_parser(string[lsb + 1:rsb], environments_stack) \
                                 + string[rsb + 1:]
                        # except EmptyEnvironmentError:
                    elif name == "newcommand" or name == "renewcommand":
                        string = string[:name_start] + "\\" + name + new_commands_parser(string[lsb + 1:rsb]) + \
                                 string[rsb + 1:]
                    elif name.strip() in SLASH_ITEM_COMMANDS:
                        string = string[:name_start] + "\\" + name + "\[" + string[lsb + 1:rsb] + "\]" + \
                                 string[rsb + 1:]
                    elif name.strip() == "documentclass":
                        # find the args string of doc class
                        args_str = string[lsb + 1:rsb]
                        doc_class_str = parse_doc_class(args_str)
                        string = string[:name_start] + doc_class_str + string[rsb + 1:]
                    else:
                        work_string = ''
                        optional_args_str = ''
                        args = split(string[lsb + 1:rsb])
                        for arg in args:
                            if re.match(r'[oO][pP]\d( )*=( )*', arg.strip()):
                                optional_args_str += '\\[' + arg[arg.find('=') + 1:].strip() + '\\]'
                            elif name.strip() == 'item':
                                optional_args_str += '\\[' + arg + '\\]'
                            else:
                                work_string += '{' + arg.strip() + '}'
                        work_string = work_string + optional_args_str
                        if name_start > 0:
                            string = string[:name_start] + '\\' + name + work_string + string[
                                                                                       rsb + 1:]  # NTS: I probably want to fix this splice
                        elif name_start == 0:
                            string = '\\' + string[:lsb] + work_string + string[rsb + 1:]
                        else:
                            # This is some old code I don't quite understand
                            print('\n\nsomething went wrong\npointer = lsb - len(name) - 1 = ' + str(name_start) + '\n')
                            return
        rsb = find_brace(']', string, rsb + 1)
    return escape_commands(string)


def get_command_name(string, start):
    """
    Gets command name within string
    :param string: to be searched for name
    :param start: the starting index. In practice, this is the character directly before '['
    :return: the name of the command; None if start is not an int. This function will eventually be updated to
             throw an exception in this case.
    """
    name = ""
    if isinstance(start, int) and start > 0:
        for i in range(start, -1, -1):
            current_char = string[i]
            if re.match(r"[\w\d]", current_char):
                name = current_char + name
            else:
                break
    return name


def new_commands_parser(args_string):
    """
    Parser for the newcommand and renewcommand commands.
    :param args_string: the arguments given for the newcommand or renewcomannd call in the source file. According to
        Parker-TeX syntax this string should be in one of the following forms:
            1. <new command name>, <what the command does> (assumes user is defining a command with 0 arguments)
            2. <number of arguments the command requires>, <command name>, <what the command does>
    :return: a string in one of the following forms corresponding to 1 and 2 above
            1. {\<new command name>}{what the command does}
            2. {\<new command name>}[number of args required]{what the command does}
    """
    out_string = ''
    args = split(args_string)
    if len(args) == 2:
        out_string = "{\\" + args[0].strip() + "}{" + args[1].strip() + "}"
    elif len(args) == 3:
        if (args[0].strip()).isdigit():
            number_of_args = int(args[0])
            out_string = "{\\" + args[1].strip() + "}\\[" + str(number_of_args) + "\\]{" + args[2].strip() + "}"
        else:
            # "compiler" error
            pass
    else:
        # not enough args "compiler" error
        pass
    return out_string


def parse_doc_class(args_str):
    """ I really need to re-think this function """
    match = re.match("[\w\d]+", args_str)
    out = ""
    if match:
        if match.end() < len(args_str):
            next_match = re.match(r"[\s|\\]*,[\s|\\]*([\w\d]+[\s|\\]*,\s*)+[^%]*", args_str[match.end():])
            if next_match:
                out = "\\documentclass\\[" + args_str[args_str.find(',') + 1:] + \
                      "\\]" + "{" + args_str[:args_str.find(',')] + "}"
        else:
            out = "\\documentclass{" + args_str + "}"
        # string = string[:name_start] + "\\documentclass{" + doc_class + "}\n"  + string[rsb + 1:]
    elif re.match("|\s+", args_str):
        # no doc class specified
        pass
    return out


def escape_commands(string):
    """
    Finds '\[' and '\]' and replaces them with '[' and ']' respectively
    :param string: self explanatory
    :return: the appropriately parsed string
    """
    out = string
    done = False
    while not done:
        left = out.find('\[')
        if left != -1:
            out = out[:left] + out[left + 1:]
        right = out.find('\]')
        if right != -1:
            out = out[:right] + out[right + 1:]
        done = left == -1 and right == -1
    return out


def split(string):
    """
    Splits string into a list using "," as a delimiter. Ignores "\," as this is used as an escape sequence in args
    strings
    :param string: the string to be split into a list
    :return: the list
    """
    j = 0
    out = []
    for i in range(len(string)):
        if string[i] == ',':
            if i > 0 and string[i - 1] != '\\':
                out.append(string[j:i])
                j = i + 1
    out.append(string[j:])
    return out


def find_brace(key, string, start=0, end=None):
    """
    Finds only '[' and ']' which are not prefixed by a '\' within the (closed) interval [start:end)
    :param key: '[' or ']'
    :param string: the string to be searched
    :param start: the starting index
    :param end: the last acceptable index
    :return: the index of '[' or ']'; return -1 if not found in string or start is out of bounds
    """
    # validate search key
    target = key.strip()
    if not (target == '[' or target == ']'):
        return -1
    # assign the appropriate end value
    if end is None:
        end = len(string)
    # validate start index
    if 0 <= start < end:
        for i in range(start, end):
            current_char = string[i]
            if current_char == target:
                if i > 0 and string[i - 1] != '\\':
                    return i
                elif i == 0:
                    return i
    return -1


def end_parser(string, start):
    """
    Parses end[<nasty environment>] commands. Does this by searching backwards to remove excess newline sequences. These
    are replaced with spaces so that the caller does not have to adjust indices pointing to important places in the
    string.

    :param string: the string to be searched for newline sequences
    :param start: the starting index
    :return: the parsed string
    """
    NEWLINES_ALLOWED = 1
    # search backwards through the string for newline sequences until the first non-whitespace character is found
    newlines_found = 0
    for i in range(start, -1, -1):
        if string[i] == '\n':
            newlines_found += 1
            if newlines_found > NEWLINES_ALLOWED:
                # replace string[i] with a blank string so that string string indices don't have to be adjusted
                string = string[:i] + " " + string[i + 1:]
        # stop searching when the first non-whitespace character is found
        elif re.match('[^\w ]', string[i]):
            break
    return string


if __name__ == "__main__":
    with open(os.pardir + '\\inputs\\test-input0.txt') as file:
        s = ''
        for line in file:
            s += line
    print(main_parser(s))
