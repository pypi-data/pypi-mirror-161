"""
Set of everyday functions, mostly for debugging, consists of variables,
functions and classes that make the interaction of the program with the
terminal simpler, but without needing a user interface.
"""

import img2pdf
import importlib
import math
import os
import sys
from typing import Any, Iterable, Generator
from pylejandria.constants import Number
import pylejandria


def center(text: str, space: int) -> str:
    """
    secondary function for prettify, it centers the given text and splits the
    space evenly.
    Params:
        text: string to be centered.
        space: quantity of white space to split.
    """
    padding = (space-len(text))/2
    return f'{" "*math.floor(padding)}{text}{" "*math.ceil(padding)}'


def prettify(
        values: list[list[Any]],
        separator: str | None='|',
        padding: int | None=0,
        headers: bool | None=False,
        orientation: str | None='center',
        _print: bool | None=True
) -> str:
    """
    prettify receives as main argument a 2D matrix and returns a string
    to make easier the visualization of data in console, mostly is for
    school projects, if is something more complicated it would be easier
    to use tkinter.

    Params:
        separator: string that separated columns.
        padding: integer of white space to fill each item.
        headers: boolean to indicate if horizontal bar of headings is needed.
        centered: boolean to indiceate if text must be centered.
    """
    separator = " "*padding + separator + " "*padding
    total_rows = len(values)
    total_cols = max([len(row) for row in values])
    string_values = [[str(col) for col in row] for row in values]
    all_values = [row + [""]*(total_cols - len(row)) for row in string_values]
    col_values = [[row[i] for row in all_values] for i in range(total_cols)]
    lengths = [(col, max([len(i) for i in col])) for col in col_values]
    if orientation == 'left':
        padded_values = [
            [row + " "*(length - len(row)) for row in col]
            for col, length in lengths
        ]
    elif orientation == 'right':
        padded_values = [
            [" "*(length - len(row)) + row for row in col]
            for col, length in lengths
        ]
    elif orientation == 'center':
        padded_values = [
            [center(row, length) for row in col]
            for col, length in lengths
        ]
    else:
        raise NotImplementedError(
            "invalid orientation. Expected right, left or center."
        )
    row_values = [[col[i] for col in padded_values] for i in range(total_rows)]
    joined_rows = [separator.join(row) for row in row_values]
    if headers:
        joined_rows.insert(1, '-'*len(joined_rows[0]))

    if _print:
        print('\n'.join(joined_rows))
    return '\n'.join(joined_rows)


def pretty_list(
    values: list | tuple,
    indent: int | None=0,
    tab: str | None=' '*4,
    start_tab: bool | None=True,
    _print: bool | None=True

) -> str:
    """
    pretty_list is a function to print list or tuples with indentation, it may
    be helpful for print debugging or console programs.

    Params:
        values:     values in list or tuple with the info we want to display.
        indent:     is a parameter used for the function to print nested
                    values.
        tab:        is a string to separate levels of indentation, it can be
                    any string.
        start_tab   the start tab can be omitted if necessary, for example is
                    not needed in pretty_dict.
        _print:     prints the result, but also returns it. Helpful to avoid
                    print function.
    """
    if not isinstance(values, list | tuple):
        raise NotImplementedError('Argument must be iterable.')
    if not values:
        return '[]'
    result = tab*indent*start_tab + '[\n'
    for value in values:
        result += tab*indent
        if isinstance(value, dict):
            result += tab
            result += pretty_dict(
                value, indent=indent+1, _print=False, start_tab=False
            )
        elif isinstance(value, list | tuple):
            result += pretty_list(value, indent=indent+1, _print=False)
        else:
            result += f'{tab}{value}\n'
    if _print is True:
        print(result + tab*indent + ']\n')
    return result + tab*indent + ']\n'


def pretty_dict(
        dictionary: dict,
        indent: int | None=0,
        tab: str | None=' '*4,
        start_tab: bool | None=True,
        _print: bool | None=True
) -> str:
    """
    pretty_dict is a function to print dictionaries with indentation, it may be
    helpful for print debugging or console programs.

    Params:
        dictionary: a dict with the info we want to display.
        indent:     is a parameter used for the function to print nested
                    values.
        tab:        is a string to separate levels of indentation, it can be
                    any string.
        _print:     prints the result, but also returns it. Helpful to avoid
                    print function.
    """
    if not isinstance(dictionary, dict):
        raise NotImplementedError("Argument must be dict type.")
    if not dictionary.items():
        return '{}\n'
    result = tab*indent*start_tab + '{\n'
    for key, value in dictionary.items():
        result += tab*indent + f'{tab}{key}: '
        if isinstance(value, dict):
            result += pretty_dict(value, indent=indent+1, _print=False)
        elif isinstance(value, list | tuple):
            result += pretty_list(
                value, indent=indent+1, _print=False, start_tab=False
            )
        else:
            result += f'{value}\n'
    if _print is True:
        print(result + tab*indent + '}\n')
    return result + tab*indent + '}\n'


def image_to_pdf(
    images: list[str], path: str,
    get_path: bool | None=False,
    get_images: bool | None=False,
    remove: bool | None=False
) -> str:
    """
    saves a pdf file with the given images at the given location and returns
    the path, specificated or not.
    Params:
        images: list of paths of the images.
        path: path where pdf will be saved.
        get_path: bool to open a window to ask path.
        get_images: bool to open a window to select images.
        remove: remove or not the given files.
    """
    if get_path is True:
        path = pylejandria.gui.ask(
            'saveasfilename', 'PDF', defaultextension='*.pdf'
        )
    if get_images is True:
        images = pylejandria.gui.ask('openfilenames', 'PNG', 'JPEG')
    if not (path and images):
        return
    with open(path, 'wb') as f:
        f.write(img2pdf.convert(images))
    if remove is True:
        for image in images:
            os.remove(image)
    return path


def parse_seconds(seconds: Number, decimals: int | None=0) -> str:
    """
    Simple function to parse seconds to standard form hh:mm:ss.
    Params:
        seconds: number of seconds to represent.
        decimals: number of decimals of seconds.
    """
    h = int(seconds // 3600)
    m = int(seconds // 60)
    s = round(seconds % 60, decimals)
    if decimals < 1:
        s = int(s)
    return f'{0 if h < 10 else ""}{h}:{0 if m < 10 else ""}{m}:{s}'


class ArgumentParser:
    def __init__(self):
        """
        ArgumentParser parses the console arguments, is simplification of
        sys.argv, instead of a list it returns a dictionary for easy access.
        """
        self.path = ''
        self.expected_args = {}
        self.args = {}

    def add_argument(
        self, name: str, type: object | None=str,
        required: bool | None=False, default: str | None=''
    ) -> None:
        """
        Adds an argument to the parser.
        Params:
            name:   name of the expected argument.
            type:   type of the argument to be parsed.
            required:   if argument is required or not, if not then should be
                        a default argument.
            default:    default value for the argument, if required is true
                        then default can be skipped.

        """
        self.expected_args[name] = [type, required, default]

    def parse(self) -> None:
        """
        Parses the arguments given from the console, it loads a dictionary
        with all arguments and values.
        """
        self.path = sys.argv[0]
        keys, values = sys.argv[1::2], sys.argv[2::2]
        for argument, (type_, required, default) in self.expected_args.items():
            if required is True:
                if argument not in keys:
                    raise NotImplementedError(f'{argument} not provided')
                value_index = keys.index(argument)
                argument_value = values[value_index]
                self.args[argument] = self.eval(argument_value, type_)
            elif argument in keys:
                try:
                    value_index = keys.index(argument)
                    argument_value = values[value_index]
                    self.args[argument] = self.eval(argument_value, type_)
                except ValueError:
                    self.args[argument] = default
            else:
                self.args[argument] = default

    def eval(self, value: str, type_: object) -> None:
        """
        Simple function to eval the given arguments and convert them into their
        respective type.
        Params:
            value: value of the argument to be evaluated.
            type_: type of the given value.
        """
        if type_ is bool:
            return value.lower().startswith('t')
        return type_(value)

    def __getitem__(self, key) -> Any:
        return self.args.get(key, None)

    def __repr__(self) -> str:
        return pretty_dict(self.args, _print=False)


def all_are(values: Iterable, comparison: Any) -> bool:
    """
    Returns if all items are equal to the comparison.
    Params:
        values: iterable to check.
        comparison: value to compare.
    """
    return all(map(lambda x: x == comparison, values))


def dict_get(dictionary: dict, key: Any, default: Any=None) -> Any:
    """
    Searches the key in the dict, but in case some key is a list or tuple it
    returns the value if key is in that list or tuple.
    Params:
        dictionary: dictonary to search from.
        key: key of the value to search.
        default: value to return if key not founded.
    """
    if value := dictionary.get(key, False):
        return value
    for keys, value in dictionary.items():
        if isinstance(keys, list | tuple):
            if key in keys:
                return value
    return default


def make_dirs(folders: Iterable[str], root: str | None='') -> None:
    """
    Creates the corresponding directories and manages the existing conflict.
    Params:
        folders: list of folders to create if possible.
        root: optional root of folder.
    """
    for folder in folders:
        if not os.path.isdir(f'{root}\{folder}'):
            os.mkdir(f'{root}\{folder}')


def dict_zip(*dicts, strict: bool | None=False) -> None:
    """
    Creates a generator to iterate each key, value of each dictionary, just as
    regular zip to lists.
    Params:
        dicts:  all the dictionaries to zip.
        strict: raise an error if any dictionary is exhausted.
    """
    for items in zip(*[dict_.items() for dict_ in dicts], strict=strict):
        yield [[element for element in item] for item in items]


def pair(items: list[Any], length: int, index: int | None=None) -> Generator:
    """
    Pairs n-elements from the list and yields it.
    Example:
        a = [1, 2, 3, 4, 5, 6]

        for a, b, c, c in pair(a, 4):
            print(a, b, c, d)
        >>> (1, 2, 3, 4)
        >>> (2, 3, 4, 5)
        >>> (3, 4, 5, 6)
    Params:
        items:  list to be paired.
        length: length of the pairs.
        index:  optional index to get an slice, useful for cases where items is
                a list of lists.
    """
    items = items if index is None else get_slice(items, index)
    for i in range(len(items)-length+1):
        yield items[i:i+length]


def get_module(file: str) -> Any:
    """
    Loads and returns the given module.
    Params:
        file: absolute path of the file to be imported.
    """
    loader = importlib.machinery.SourceFileLoader('loaded_module', file)
    spec = importlib.util.spec_from_loader('loaded_module', loader)
    loaded_module = importlib.util.module_from_spec(spec)
    loader.exec_module(loaded_module)
    return loaded_module


def get_slice(values: list[list], index: int) -> list:
    """
    Returns an slice of the values.
    Example:
        a = [
            [1, 2, 3, 4],
            [5, 6, 7, 8],
            [9, 10, 11, 12]
        ]
        print(get_row(a, 0))
        >>> [1, 5, 9]
    Params:
        values: list of list to get the slice from.
        index:  index of the slice.
    """
    return [value[index] for value in values]


if __name__ == '__main__':
    a = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
        [10, 11, 12]
    ]
    for a, b in pair(a, 2, index=0):
        print(a, b)
