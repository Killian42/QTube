import re
import string
import sys
import time

from googleapiclient.errors import HttpError


def handle_http_errors(verbosity: list[str], func, *args, **kwargs):
    """Handles http errors when making API queries.
    If after 5 tries, the function could not be executed, it shuts the program down.

    Args:
        verbosity (list[str]): User defined verbosity.
        func (function): Function to be executed, with its arguments and keyword arguments.
        args (any): Arguments of func.
        kwargs (any): Keyword arguments of func.

    Returns:
        res (any): Whatever the function is supposed to return if no http error occur otherwise, it depends on the function.
    """
    for i, t in enumerate(
        [5, 10, 30, 180, 300]
    ):  # Run 5 times with increasing retrying times
        try:
            res = func(*args, **kwargs)
            print2(
                f"{func.__name__} successfully executed.", ["all", "func"], verbosity
            )
            return res  # Return the response if no error occurs
        except HttpError as err:
            if (
                func.__name__ == "get_recent_videos" and err.status_code == 404
            ):  # Channel has no videos
                return "ignore"  # Ignore this channel in the main code
            elif (
                all(
                    word in err.reason
                    for word in ["request", "cannot", "exceeded", "quota"]
                )
                and err.status_code == 403
            ):  # Quota limit exceeded, the program cannot continue
                print(
                    "The quota limit has been reached, please try again later. Check your usage at the following urls: \nUsed quota: https://console.cloud.google.com/iam-admin/quotas?pageState=(%22allQuotasTable%22:(%22c%22:%5B%22displayDimensions%22,%22serviceName%22,%22metricName%22,%22limitName%22,%22monitoredResource%22%5D)) \nCalls made: https://console.cloud.google.com/apis/dashboard"
                )
                sys.exit()
            else:  # General case
                print(
                    f"During the execution of function {func.__name__}, error {err.status_code} occured: {err.reason}"
                )
                print(
                    f"Retrying in {t} seconds. This was attempt number {i+1} out of 5."
                )
                time.sleep(t)
        if t == 4:
            print(
                f"Function {func.__name__} could not be executed after 5 tries. Please check your internet connection, Youtube's API status and retry later."
            )
            sys.exit()  # Exit the program after 5 retries


def print2(message: str, verb_level: list, verbosity: list) -> None:
    """Prints text in the terminal depending on the choosen verbosity.

    Args:
        message (str): Text to be printed in the terminal.
        verb_level (list[str]): Verbosity associated to the text.
        verbosity (list[str]): User defined verbosity.

    Returns:
        None
    """

    if any(v in verb_level for v in verbosity):
        print(message)


def split_list(input_list: list, chunk_size: int) -> list:
    """Splits a list into several lists with a specified length.
    If the number of elements is not divisible by the wanted size, one of the sub-lists will be shorter.

    Args:
        input_list (list): List to be split.
        chunk_size (int): Wanted length of the sub-lists.

    Returns:
        (list): List of the sub-lists.
    """
    return [
        input_list[i : i + chunk_size] for i in range(0, len(input_list), chunk_size)
    ]


def split_dict(input_dict: dict, chunk_size: int) -> list[dict]:
    """Splits a dictionary into several dictionaries with a specified length.
    If the number of elements is not divisible by the wanted size, one of the sub-dictionaries will be shorter.

    Args:
        input_dict (dict): Dictionary to be split.
        chunk_size (int): Wanted length of the sub-dictionaries.

    Returns:
        (list[dict]): List of the sub-dictionaries.
    """
    items = list(input_dict.items())
    return [
        {k: v for k, v in items[i : i + chunk_size]}
        for i in range(0, len(items), chunk_size)
    ]


def merge_dicts(list_of_dicts: list) -> dict:
    """Merges a list of dictionaries into one.

    Args:
        list of dict (list): list of dictionaries to be merged.

    Returns:
        (dict): single dictionary containing the the dictionaries from the list.
    """
    return {key: value for d in list_of_dicts for key, value in d.items()}


def strip_emojis(text):
    """Strips emojis from a string.

    Args:
        text (str): Text string containing emojis.

    Returns:
        (str): Same Text string, but emojis are replaces by spaces.
    """
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F700-\U0001F77F"  # alchemical symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE,
    )
    clean_text = emoji_pattern.sub(r"", text)
    return remove_multiple_spaces(clean_text)


def strip_punctuation(text):
    """Strips punctuation from a string (all of these characters: !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~).

    Args:
        text (str): Text string containing punctuation.

    Returns:
        (str): Same text string, but the punctuation is replaced by a space.
    """
    translation_table = str.maketrans(string.punctuation, " " * len(string.punctuation))
    clean_text = text.translate(translation_table)
    return remove_multiple_spaces(clean_text)


def make_lowercase(text):
    """Converts all uppercase letters to lowercase from a string.

    Args:
        text (str): Text string containing lowercase and uppercase letters.

    Returns:
        (str): Same Text string, but all in lowercase.
    """

    return text.lower()


def remove_multiple_spaces(text):
    """Removes multiple spaces in a string and replaces them with a single space.

    Args:
        text (str): Text string with multiple spaces.

    Returns:
        (str): Same text string, but with multiple spaces replaced by a single space.
    """
    return re.sub(" +", " ", text)
