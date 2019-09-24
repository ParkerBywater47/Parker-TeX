import re
import commands


def begin_env_parser(args_string, env_stack=None):
    """
    Parses begin[<env>] commands into laTeX code
    :param args_string: the string in between '[' and ']'
    :param env_stack: a list to add the environment to
    :return: appropriate "\begin{<env>}" laTeX command.
    """
    out = ""
    if re.match(r"\s+", args_string):
        # empty environment error
        pass
    else:
        # old options_match regexp = "([\w\d]+)\s*,\s*([\w\d()| ]+\s*,\s*)*([\w\d()| ]+\s*\])"
        options_match = re.match("\s*([\w\d]+)\s*,\s*([\w\d()| ]+\s*,\s*)*([\w\d()| ]+\s*)", args_string)
        if options_match:
            env_name = options_match.group(1)
            if env_name == "array":
                splice_pt = args_string.find(",")
                out = "{array}{" + args_string[splice_pt + 1:] + "}"
            elif re.match("[bvp]matrix", env_name):
                splice_pt = args_string.find(",")
                out = "{" + env_name + "}\n" + matrix_parser(args_string[splice_pt + 1:])
            else:
                # the default parse for begin[<required_arg>, <optional_arg>] syntax
                optional_args_str = "\\["
                start = args_string.find(",", len(env_name))
                args = commands.split(args_string[start + 1:])
                for i in args:
                    optional_args_str += i
                optional_args_str += "\\]"
                out = "{" + env_name + "}" + optional_args_str
        else:
            env_name = args_string.strip()
            out = "{" + env_name + "}"
        if env_stack is not None:
            env_stack.append(env_name)
    return out


def matrix_parser(args_string):
    """
    Function to output matrix code. This will eventually be generalized to deal with array environments and the such like
    :param args_string: string of data to be converted to tex code. first two args are rows and colums, respectively
    :return: tex code for a matrix/array/tabular environment. returns only the code in between begin{env} and end{env}
    """
    # print("matrices args_string:" + args_string)
    data = args_string.split(",")
    rows = int(data.pop(0))
    columns = int(data.pop(0))
    out_string = ""
    for i in range(len(data) - 1):
        out_string += data[i] + (r'\\' if i // (columns - 1) == 1 else ' &')
    out_string += data[len(data) - 1]
    return out_string

