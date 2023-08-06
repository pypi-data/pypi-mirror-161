import pickle, os

import pandas as pd

from datetime import datetime


def dump_pickle(variable, file_path: str, verbose: int = 0) -> None:
    """[summary]

    :param variable: [description]
    :type variable: [type]
    :param file_path: [description]
    :type file_path: str
    :return: [description]
    :rtype: [type]
    """
    result = False
    try:
        pickle.dump(variable, open(file_path, "wb"))
        if verbose > 0:
            print("[info] Variable successfully dumped!")
        result = True

    except Exception as err:
        print("[error]", err)

    return result


def load_pickle(file_path: str, verbose: int = 0):
    """[summary]

    :param file_path: [description]
    :type file_path: str
    :return: [description]
    :rtype: [type]
    """
    result = None
    try:
        result = pickle.load(open(file_path, "rb"))
        if verbose > 0:
            print("[info] Variable successfully load!")

    except Exception as err:
        print("[error]", err)

    return result


def get_today_string(form: str = "%d/%m/%Y"):
    """Get a string with the present date.

    :param form: The date format. Use %Y for year, %m for months and %d for daus, defaults to "%d/%m/%Y"
    :type form: str, optional
    :return: The present data in string format
    :rtype: `str`
    """

    # today = date.today()
    today = datetime.now()
    return str(today.strftime(form))


def to_date(string, format="%d/%m/%Y"):
    """Converts a string to datetime

    :param string: String containing the date.
    :type string: str
    :param format: The date format. Use %Y for year, %m for months and %d for daus, defaults to "%d/%m/%Y"
    :type format: str, optional
    :return: The present data in string format
    :rtype: `str`
    """
    return datetime.strptime(string, format)


def read_file(file: str) -> str:
    """Read a file content

    :param file: path to the file
    :type file: str
    :return: A string with the file content
    :rtype: str
    """
    with open(file, "r") as file:
        private_key = file.read()
    return private_key


def file_print(
    content, file: str, mode: str = "write", sep: str = " ", end: str = "\n", **kwargs
) -> None:
    """Print the content to file

    :param content: Content to be printed
    :type content:
    :param file: path to the file
    :type file: str
    :param mode: write mode. Can be 'write' or 'append', defaults to "write"
    :type mode: str, optional
    :param sep: string inserted between values, defaults to " "
    :type sep: str, optional
    :param end: string appended after the last value, defaults to "\n"
    :type end: str, optional
    """
    if mode == "write":
        mode = "w"
    elif mode == "append":
        mode = "a"

    with open(file, mode) as text_file:
        print(content, file=text_file, sep=sep, end=end, **kwargs)


def make_directory(path):
    """Creates a dict if it does not exists.

    :param path: path of new directory
    :type path: str
    """
    if not os.path.exists(path):
        os.makedirs(path)


def set_column_position(data: pd.DataFrame, column: str, position: int):
    """[summary]

    :param data: [description]
    :type data: [type]
    :param column: [description]
    :type column: [type]
    :param index: [description]
    :type index: [type]
    :return: [description]
    :rtype: [type]
    """
    columns = list(data.columns)
    columns.remove(column)
    columns.insert(position, column)
    return data[columns]


def file_names(path=None, directory=False):

    if path is None:
        path = os.getcwd()

    list_ = os.listdir(path)

    if directory:
        return list_

    else:
        return [f for f in list_ if os.path.isfile(os.path.join(path, f))]
