import sys
import signal
import textwrap
import json
import tabulate
import shutil

__version__ = '1.3.2'


def ctrlc(signum, frame):
    """exit with error on SIGINT"""
    sys.exit(1)


def get_stdin():
    """return STDIN data"""
    if sys.stdin.isatty():
        return None
    else:
        return sys.stdin.read()


def helptext():
    print_error(textwrap.dedent('''\
        jtbl:   Converts JSON and JSON Lines to a table

        Usage:  <JSON Data> | jtbl [OPTIONS]

                --cols=n   manually configure the terminal width
                -m         markdown table output
                -n         do not try to wrap if too wide for the terminal
                -q         quiet - don't print error messages
                -r         rotate table output
                -t         truncate data if too wide for the terminal
                -v         version info
                -h         help
    '''))


def print_error(message, quiet=False):
    """print error messages to STDERR and quit with error code"""
    if not quiet:
        print(message, file=sys.stderr)
    sys.exit(1)


def wrap(data, columns, table_format, truncate):
    """
    Wrap or truncate the data to fit the terminal width.

    Returns a tuple of (data, table_format)
        data (dictionary)       a modified dictionary with wrapped or truncated string values.
                                wrapping is achieved by inserting \n characters into the value strings.

        table_format (string)   'simple' (for truncation) or 'grid' (for wrapping)
    """

    # find the length of the keys (headers) and longest values
    data_width = {}
    for entry in data:
        for k, v in entry.items():
            if k in data_width:
                if len(str(v)) > data_width[k]:
                    data_width[k] = len(str(v))
            else:
                data_width[k] = len(str(v))

    # highest_value calculations are only approximate since there can be left and right justification
    num_of_headers = len(data_width.keys())
    combined_total_list = []
    for k, v in data_width.items():
        highest_value = max(len(k) + 4, v + 2)
        combined_total_list.append(highest_value)

    total_width = sum(combined_total_list)

    if total_width > columns:
        # Find the best wrap_width based on the terminal size
        sorted_list = sorted(combined_total_list, reverse=True)
        wrap_width = sorted_list[0]
        scale = 2.5 if truncate else 4.5

        while wrap_width > 4 and total_width >= (columns - (num_of_headers * scale)):
            sorted_list = sorted(sorted_list, reverse=True)
            sorted_list[0] -= 1
            total_width = sum(sorted_list)
            wrap_width = sorted_list[0]

        # truncate or wrap every wrap_width chars for all field values
        for entry in data:
            delete_keys = []
            add_keys = []
            for k, v in entry.items():
                if v is None:
                    v = ''

                if truncate:
                    new_key = str(k)[0:wrap_width]
                    new_value = str(v)[0:wrap_width]
                    if k != new_key or v != new_value:
                        delete_keys.append(k)
                        add_keys.append((new_key, new_value))

                else:
                    table_format = 'fancy_grid'
                    new_key = '\n'.join([str(k)[i:i + wrap_width] for i in range(0, len(str(k)), wrap_width)])
                    new_value = '\n'.join([str(v)[i:i + wrap_width] for i in range(0, len(str(v)), wrap_width)])
                    if k != new_key or v != new_value:
                        delete_keys.append(k)
                        add_keys.append((new_key, new_value))

            for i in delete_keys:
                del entry[i]

            for i in add_keys:
                entry[i[0]] = i[1]

    return (data, table_format)


def get_json(json_data, columns=None):
    """Accepts JSON or JSON Lines and returns a tuple of
       (success/error, list of dictionaries)
    """
    SUCCESS, ERROR = True, False

    if not json_data or json_data.isspace():
        return (ERROR, 'jtbl:   Missing piped data\n')

    try:
        data = json.loads(json_data)
        if type(data) is not list:
            data_list = []
            data_list.append(data)
            data = data_list

        return SUCCESS, data

    except Exception:
        # if json.loads fails, assume the data is formatted as json lines and parse
        data = json_data.splitlines()
        data_list = []
        for i, jsonline in enumerate(data):
            try:
                entry = json.loads(jsonline)
                data_list.append(entry)
            except Exception as e:
                # can't parse the data. Throw a nice message and quit
                return (ERROR, textwrap.dedent(f'''\
                    jtbl:  Exception - {e}
                           Cannot parse line {i + 1} (Not JSON or JSON Lines data):
                           {str(jsonline)[0:columns - 8]}
                            '''))
        return SUCCESS, data_list


def make_table(data=None,
               truncate=False,
               nowrap=False,
               columns=None,
               table_format='simple',
               rotate=False):
    """
    Generates the table from the JSON input.

    Returns a tuple of ([SUCCESS | ERROR], result)
        SUCCESS | ERROR (boolean)   SUCCESS (True) if no error, ERROR (False) if error encountered
        result (string)             text string of the table result or error message
    """
    SUCCESS, ERROR = True, False

    # only process if there is data
    if data:
        try:
            if not isinstance(data[0], dict):
                data = json.dumps(data)
                return (ERROR, textwrap.dedent(f'''\
                    jtbl:  Cannot represent this part of the JSON Object as a table.
                           (Could be an Element, an Array, or Null data instead of an Object):
                           {str(data)[0:columns - 8]}
                           '''))

        except Exception:
            # can't parse the data. Throw a nice message and quit
            return (ERROR, textwrap.dedent(f'''\
                jtbl:  Cannot parse the data (Not JSON or JSON Lines data):
                       {str(data)[0:columns - 8]}
                       '''))

        if not nowrap:
            data, table_format = wrap(data=data, columns=columns, table_format=table_format, truncate=truncate)

        headers = 'keys'
        if rotate:
            table_format = 'plain'
            headers = ''

        return (SUCCESS, tabulate.tabulate(data, headers=headers, tablefmt=table_format))

    else:
        return (ERROR, '')


def main():
    # break on ctrl-c keyboard interrupt
    signal.signal(signal.SIGINT, ctrlc)

    # break on pipe error. need try/except for windows compatibility
    try:
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    except AttributeError:
        pass

    stdin = get_stdin()

    options = []
    long_options = {}
    for arg in sys.argv:
        if arg.startswith('-') and not arg.startswith('--'):
            options.extend(arg[1:])

        if arg.startswith('--'):
            try:
                k, v = arg[2:].split('=')
                long_options[k] = int(v)
            except Exception:
                helptext()

    markdown = 'm' in options
    nowrap = 'n' in options
    quiet = 'q' in options
    rotate = 'r' in options
    truncate = 't' in options
    version_info = 'v' in options
    helpme = 'h' in options

    tbl_fmt = 'github' if markdown else 'simple'

    if not rotate and markdown:
        nowrap = True

    columns = None
    if 'cols' in long_options:
        columns = long_options['cols']

    if columns is None:
        columns = shutil.get_terminal_size().columns

    if version_info:
        print_error(f'jtbl:   version {__version__}\n')

    if helpme:
        helptext()

    succeeeded, json_data = get_json(stdin, columns=columns)
    if not succeeeded:
        print_error(json_data, quiet=quiet)

    if rotate:
        for idx, row in enumerate(json_data):
            rotated_data = []
            for k, v in row.items():
                rotated_data.append({'key': k, 'value': v})

            succeeeded, result = make_table(data=rotated_data,
                                        truncate=truncate,
                                        nowrap=nowrap,
                                        columns=columns,
                                        rotate=True)
            if succeeeded:
                if len(json_data) > 1:
                    print(f'item: {idx}')
                    print('─' * columns)
                print(result)
                print()
            else:
                print_error(result, quiet=quiet)

    else:
        succeeeded, result = make_table(data=json_data,
                                        truncate=truncate,
                                        nowrap=nowrap,
                                        columns=columns,
                                        table_format=tbl_fmt)

        if succeeeded:
            print(result)
        else:
            print_error(result, quiet=quiet)


if __name__ == '__main__':
    main()
