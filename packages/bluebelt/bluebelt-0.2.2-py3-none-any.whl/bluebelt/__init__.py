# from bluebelt.core import index
from bluebelt.core import series
from bluebelt.core import dataframe

from bluebelt.create import create

import bluebelt.styles.rc

import os
from collections.abc import MutableMapping

import matplotlib as mpl
import yaml


class BlueConfig:
    _config = {}

    @staticmethod
    def get(name):
        if name in BlueConfig._config.keys():
            return BlueConfig._config[name]
        elif (
            ".".join(name.split(".")[:-1]) in BlueConfig._config.keys()
        ):  # is the name up to the last dot in keys?
            # is the last part of the name in this valueset?
            if (
                name.split(".")[-1]
                in BlueConfig._config[".".join(name.split(".")[:-1])]
            ):
                return BlueConfig._config[".".join(name.split(".")[:-1])][
                    name.split(".")[-1]
                ]
            else:
                return None
        else:
            return None

    @staticmethod
    def set(name, value):
        BlueConfig._config[name] = value

    @staticmethod
    def default():
        set_style("paper")


def config(key=None, value=None):
    """
    Change or get the Bluebelt configuration.

    Parameters
    ----------
    key: the name of the configuration parameter
    value: the value of the configuration parameter

    Returns
    -------
    If key and value are provided parameter key is set to value and nothing is
    returned.
    If only key is provided the parameter value is returned.
    If key and value are both not provided the configuration is reset to the
    default parameter values.
    """

    if key and value:
        BlueConfig.set(key, value)
    elif key:
        return BlueConfig.get(key)
    else:
        BlueConfig.default()


def set_style(name=None):
    """
    Set the default style

    Parameters
    ----------
    name : string, default None
        a string with a default bluebelt style name or the path to a custuom
        YAML style sheet

    Returns
    -------
    None

    Example
    -------
    bluebelt.set_style("paper")

    """
    if name is None:
        return BlueConfig.get("style")

    path = os.path.dirname(os.path.realpath(__file__))

    # check if name is not pointing to a yaml file
    if os.path.splitext(name)[1] not in [".yaml", ".yml"]:
        path_file = f"{path}/styles/{name}.yaml"

        # check if the style exists
        if not os.path.isfile(path_file):

            # list styles
            style_list = ""
            for file in os.listdir(f"{path}/styles/"):
                if file.endswith(".yaml"):
                    if len(style_list) > 0:
                        style_list += ", "
                    style_list += str(file.split(".")[0])
            raise ValueError(
                f"{name} style does not exist. Choose from {str(style_list)}"
            )
    else:
        path_file = name

    try:
        with open(path_file, "r") as file:
            style = _flatten_style(yaml.load(file, yaml.SafeLoader))

        for key, value in style.items():
            if key.startswith("rc."):
                # set the values in matplotlib and bluebelt
                mpl.rc(key.split(".")[-1], **value)
                BlueConfig.set(key, value)
            else:
                BlueConfig.set(key, value)

    except OSError as e:
        print(f"Unable to find {path_file}. Did you enter the correct file path?")


def get_style(name):
    """
    Return the contents of a bluebelt style

    Parameters
    ----------
    name : string, default None
        a string with a default bluebelt style name or the path to a custuom
        YAML style sheet

    Returns
    -------
    bluebelt style dict

    Example
    -------
    bluebelt.set_style("paper")

    """
    path = os.path.dirname(os.path.realpath(__file__))

    # check if name is not pointing to a yaml file
    if os.path.splitext(name)[1] not in [".yaml", ".yml"]:
        name = f"{path}/styles/{name}.yaml"

    with open(name, "r") as file:
        style = _flatten_style(yaml.load(file, yaml.SafeLoader))

    return style


def _flatten_style(
    d: MutableMapping, parent_key: str = "", sep: str = "."
) -> MutableMapping:
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, MutableMapping):
            if any(map(lambda x: isinstance(x, dict), v.values())):
                items.extend(_flatten_style(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        else:
            items.append((new_key, v))
    return dict(items)


def set_figsize_in_pixels(
    size: tuple or int = None, height: int = None, dpi: int = None
):
    """
    Set the default figsize in pixels

    Parameters
    ----------
    size : tuple or int, default None
        a tuple with (width, height) values or
        an int with the 'width' value in which case a height must be provided
    height: int, default None
        if size is an int height will complete the figsize
    dpi: int, default None
        change the default dpi (dots per inch, or dots per 2.54 cm)

    Returns
    -------
    None

    Example
    -------
    bluebelt.set_figsize_in_pixels(900, 600)

    """
    # set or get dpi
    if dpi:
        mpl.rcParams["figure.dpi"] = dpi
    else:
        dpi = mpl.rcParams["figure.dpi"]

    # in case two int are passed
    if height and isinstance(size, int):
        size = (size, height)

    # set figsize
    mpl.rcParams["figure.figsize"] = tuple(ti / dpi for ti in size)


def set_figsize_in_cm(size: tuple or int = None, height: int = None, dpi: int = None):
    """
    Set the default figsize in centimeters

    Parameters
    ----------
    size : tuple or int, default None
        a tuple with (width, height) values or
        an int with the 'width' value in which case a height must be provided
    height: int, default None
        if size is an int height will complete the figsize
    dpi: int, default None
        change the default dpi (dots per inch, or dots per 2.54 cm)

    Returns
    -------
    None

    Example
    -------
    bluebelt.set_figsize_in_cm(5, 8)

    """
    # set or get dpi
    if dpi:
        mpl.rcParams["figure.dpi"] = dpi
    else:
        dpi = mpl.rcParams["figure.dpi"]

    # in case two int are passed
    if height and isinstance(size, int):
        size = (size, height)

    # set figsize
    mpl.rcParams["figure.figsize"] = tuple(ti / 2.54 for ti in size)


def set_transparent(transparent: bool = False):
    """
    Set the default way to handle transparency when saving an image.

    Parameters
    ----------
    transparent : bool, default False

    Returns
    -------
    None

    Example
    -------
    bluebelt.set_transparent(True)

    """
    mpl.rcParams["savefig.transparent"] = transparent


def set_language(language=None):
    """
    Set the default language.

    Parameters
    ----------
    language : str, default None
        currently only support 'en' and 'nl'
        currently only works for weekday names

    Returns
    -------
    None

    Example
    -------
    bluebelt.set_language('en')

    """
    languages = ["nl", "en"]
    if language not in languages:
        raise ValueError(
            f"The language should be one of {str(languages)[1:-1]}, not {language}."
        )

    BlueConfig.set("language", language)


def get_language():
    """
    Get the current language.

    Returns
    -------
    str

    Example
    -------
    bluebelt.get_language()

    """
    return BlueConfig.get("language")


set_style("paper")
set_language("en")
