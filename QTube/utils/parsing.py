import argparse
import json
import re


def parse_arguments():
    """Parses command line arguments.

    Args:
        None

    Returns:
        (dict): Dictionary of the command line arguments.
    """
    parser = argparse.ArgumentParser(
        prog="QTube",
        description="Automatically add Youtube videos to a playlist.",
        epilog="For more information, check out the Github repo at https://github.com/Killian42/QTube.",
        usage="python qtube.py [options] or qtube [options]",
    )

    parser.add_argument(
        "-rc",
        "--required_in_channel_name",
        metavar="",
        nargs="+",
        type=str,
        help="Words that must be in channel names, typically channel names themselves. Default: None",
    )

    parser.add_argument(
        "-bc",
        "--banned_in_channel_name",
        metavar="",
        nargs="+",
        type=str,
        help="Words that must not be in channel names, typically channel names themselves. Default: None",
    )

    parser.add_argument(
        "-ic",
        "--include_extra_channels",
        action="store_true",
        help="Determines whether to include channels the user is not subscribed to. Default: False",
    )

    parser.add_argument(
        "-ec",
        "--extra_channel_handles",
        metavar="",
        nargs="+",
        type=str,
        help="Handles of additional channels to be checked. Default: None",
    )

    parser.add_argument(
        "-rt",
        "--required_in_title",
        metavar="",
        nargs="+",
        type=str,
        help="Words that must be in video titles. Default: None",
    )

    parser.add_argument(
        "-bt",
        "--banned_in_title",
        metavar="",
        nargs="+",
        type=str,
        help="Words that must not be in video titles. Default: None",
    )

    parser.add_argument(
        "-ite",
        "--ignore_title_emojis",
        action="store_true",
        help="Determines whether emojis are ignored in video titles. Default: False",
    )

    parser.add_argument(
        "-itp",
        "--ignore_title_punctuation",
        action="store_true",
        help="Determines whether punctuation is ignored in video titles. Default: False",
    )

    parser.add_argument(
        "-itc",
        "--ignore_title_case",
        action="store_true",
        help="Determines whether case is ignored in video titles. Default: False",
    )

    parser.add_argument(
        "-il",
        "--ignore_livestreams",
        action="store_true",
        help="Determines whether currently streaming livestreams are ignored. Default: False",
    )

    parser.add_argument(
        "-ip",
        "--ignore_premieres",
        action="store_true",
        help="Determines whether premieres are ignored. Default: False",
    )

    parser.add_argument(
        "-rd",
        "--required_in_description",
        metavar="",
        nargs="+",
        type=str,
        help="Words that must be in video descriptions. Default: None",
    )

    parser.add_argument(
        "-bd",
        "--banned_in_description",
        metavar="",
        nargs="+",
        type=str,
        help="Words that must not be in video descriptions. Default: None",
    )

    parser.add_argument(
        "-rta",
        "--required_tags",
        metavar="",
        nargs="+",
        type=str,
        help="Tags that must be associated with the videos. Default: None",
    )

    parser.add_argument(
        "-bta",
        "--banned_tags",
        metavar="",
        nargs="+",
        type=str,
        help="Tags that must not be associated with the videos. Default: None",
    )

    parser.add_argument(
        "-pl",
        "--preferred_languages",
        metavar="",
        nargs="+",
        type=str,
        help="Languages the videos need to be in. Default: None",
    )

    parser.add_argument(
        "-rca",
        "--require_captions",
        action="store_true",
        help="Determines whether to add videos with no captions. Default: False",
    )

    parser.add_argument(
        "-co",
        "--caption_options",
        metavar="",
        type=str,
        help="Caption properties such as language, track kind, audio type and accessibility parameters. Default: None",
    )

    parser.add_argument(
        "-ad",
        "--allowed_durations",
        metavar="",
        nargs="+",
        type=int,
        help="Minimum and maximum video durations (in minutes). Default: None",
    )

    parser.add_argument(
        "-ld",
        "--lowest_definition",
        metavar="",
        type=str,
        help="Minimum definition. Default: None",
    )

    parser.add_argument(
        "-lr",
        "--lowest_resolution",
        metavar="",
        type=str,
        help="Minimum resolution. Default: None",
    )

    parser.add_argument(
        "-lf",
        "--lowest_framerate",
        metavar="",
        type=int,
        help="Minimum framerate. Default: None",
    )

    parser.add_argument(
        "-pd",
        "--preferred_dimensions",
        metavar="",
        nargs="+",
        type=str,
        help="Dimension the videos need to be in. Default: None",
    )

    parser.add_argument(
        "-pp",
        "--preferred_projections",
        metavar="",
        nargs="+",
        type=str,
        help="Projection the videos need to be in. Default: None",
    )

    parser.add_argument(
        "-rf",
        "--run_frequency",
        metavar="",
        type=int,
        default=1,
        help="Defines the duration, in days, of the timeframe considered by the software. Default: 1",
    )

    parser.add_argument(
        "-ks",
        "--keep_shorts",
        action="store_false",
        help="Determines whether to add shorts. Default: True",
    )

    parser.add_argument(
        "-kd",
        "--keep_duplicates",
        action="store_true",
        help="Determines whether to add videos that are already in the playlist. Default: False",
    )

    parser.add_argument(
        "-up",
        "--upload_playlist_ID",
        metavar="",
        type=str,
        help="ID of the playlist the videos will be added to. Default: None",
    )

    parser.add_argument(
        "-fm",
        "--fancy_mode",
        metavar="",
        type=str,
        help="Enables fancy mode (colors and emojis) for terminal output. Default: True",
    )

    parser.add_argument(
        "-v",
        "--verbosity",
        metavar="",
        nargs="+",
        type=str,
        help="Controls how much information is shown in the terminal. Default: None",
    )

    return vars(parser.parse_args())


def format_arguments(args_dict):
    """Formats the parsed command line arguments (written with the help of AI, regex is witchcraft to me).

    Args:
        args_dict (dict): Dictionary of parsed command line arguments.

    Returns:
        args_dict (dict): Formatted dictionary of parsed command line arguments.
    """
    if co_str := args_dict.get("caption_options"):
        # Define a regex to match lists and split the values inside the brackets
        co_str2 = re.sub(
            r"(\w+):\s*\[([^\]]*)\]",
            lambda m: f'"{m.group(1)}": ["' + '", "'.join(m.group(2).split(",")) + '"]',
            co_str,
        )

        # Match booleans
        co_str2 = re.sub(r"(\w+):\s*(True|False)", r'"\1": \2', co_str2)

        # Match other key-value pairs
        co_str2 = re.sub(r"(\w+):\s*(\w+)", r'"\1": "\2"', co_str2)

        # Replace single quotes with double quotes to comply with JSON format
        co_str2 = co_str2.replace("'", '"')

        # Lowercase true/false to comply with JSON format
        co_str2 = co_str2.replace("True", "true").replace("False", "false")

        # Convert the formatted string to a dictionary
        co_dict = json.loads(co_str2)

        # Update the dictionary with the parsed caption_options
        args_dict["caption_options"] = co_dict

    return args_dict


def format_arguments_legacy(args_dict):
    """Formats the parsed command line arguments (legacy function).

    Args:
        args_dict (dict): Dictionary of parsed command line arguments.

    Returns:
        args_dict (dict): Formatted dictionary of parsed command line arguments.
    """
    if co_str := args_dict.get("caption_options"):
        co_str1 = re.sub(r"\s+", "", co_str)  # Removes whitespaces
        co_str2 = (
            co_str1.replace("{", "{'")
            .replace(":", "':")
            .replace("[", "['")
            .replace("]", "']")
            .replace(",", "','")
            .replace("]'", "]")
            .replace("False'", "False")
            .replace("True'", "True")
            .replace("'", '"')
            .replace(":", ": ")
            .replace(",", " , ")
            .replace("F", "f")
            .replace("T", "t")
            .replace("audiotracktype", "audioTrackType")
        )  # Format string to a JSON strings in the wonkiest way, but it seems to work

        co_dict = json.loads(co_str2)

        args_dict["caption_options"] = co_dict

    return args_dict
