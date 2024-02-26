### Libraries
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pytube import YouTube

import datetime as dt
import isodate
import json
import os
import pickle
import re
import requests
import sys
import time
import string


### Functions


## Local interactions


# Checks
def check_user_params(params_dict: dict) -> bool:
    """Checks if the user-defined parameters are correctly formatted

    Args:
        params_dict (dict): Dictionary of the user-defined parameters

    Returns:
        ok (bool): True if all checks are passed, False otherwise
    """

    # Data used for comparison
    languages_options = [
        "aa",
        "ab",
        "af",
        "ak",
        "sq",
        "am",
        "ar",
        "an",
        "hy",
        "as",
        "av",
        "ae",
        "ay",
        "az",
        "ba",
        "bm",
        "eu",
        "be",
        "bn",
        "bh",
        "bi",
        "bs",
        "br",
        "bg",
        "my",
        "ca",
        "km",
        "ch",
        "ce",
        "ny",
        "zh",
        "cu",
        "cv",
        "kw",
        "co",
        "cr",
        "hr",
        "cs",
        "da",
        "dv",
        "nl",
        "dz",
        "en",
        "eo",
        "et",
        "ee",
        "fo",
        "fj",
        "fi",
        "fr",
        "ff",
        "gl",
        "ka",
        "de",
        "el",
        "gn",
        "gu",
        "ht",
        "ha",
        "he",
        "hz",
        "hi",
        "ho",
        "hu",
        "ia",
        "id",
        "ie",
        "ga",
        "ig",
        "ik",
        "io",
        "is",
        "it",
        "iu",
        "ja",
        "jv",
        "kl",
        "kn",
        "kr",
        "ks",
        "kk",
        "km",
        "ki",
        "rw",
        "ky",
        "kv",
        "kg",
        "ko",
        "ku",
        "kj",
        "la",
        "lb",
        "lg",
        "li",
        "ln",
        "lo",
        "lt",
        "lu",
        "lv",
        "gv",
        "mk",
        "mg",
        "ms",
        "ml",
        "mt",
        "mr",
        "mh",
        "mn",
        "na",
        "nv",
        "nd",
        "ne",
        "ng",
        "nb",
        "nn",
        "no",
        "ii",
        "nr",
        "oc",
        "oj",
        "cu",
        "om",
        "or",
        "os",
        "pa",
        "pi",
        "fa",
        "pl",
        "ps",
        "pt",
        "qu",
        "ro",
        "rm",
        "rn",
        "ru",
        "sg",
        "sa",
        "si",
        "sk",
        "sl",
        "se",
        "sm",
        "sn",
        "sd",
        "so",
        "st",
        "es",
        "su",
        "sw",
        "ss",
        "sv",
        "ta",
        "te",
        "tg",
        "th",
        "ti",
        "bo",
        "tk",
        "tl",
        "tn",
        "to",
        "tr",
        "ts",
        "tt",
        "tw",
        "ty",
        "ug",
        "uk",
        "ur",
        "uz",
        "ve",
        "vi",
        "vo",
        "cy",
        "wa",
        "wo",
        "xh",
        "yi",
        "yo",
        "za",
        "zu",
    ]
    verbosity_options = ["all", "videos", "credentials", "func", "none"]
    frequency_options = ["daily", "weekly", "monthly"]
    definition_options = ["HD", "SD"]
    dimension_options = ["3D", "2D"]
    resolution_options = [
        "144p",
        "240p",
        "360p",
        "480p",
        "720p",
        "1080p",
        "1440p",
        "2160p",
        "4320p ",
    ]
    projections_options = ["rectangular", "360"]
    caption_options = [
        "trackKind",
        "languages",
        "audioTrackType",
        "isCC",
        "isLarge",
        "isEasyReader",
        "isAutoSynced",
        "status",
    ]

    # List of checks
    checks = [
        # Channel name
        params_dict.get("required_in_channel_name") is None
        or all(
            isinstance(item, str)
            for item in params_dict.get("required_in_channel_name")
        ),
        # Channel name
        params_dict.get("banned_in_channel_name") is None
        or all(
            isinstance(item, str) for item in params_dict.get("banned_in_channel_name")
        ),
        # Playlist ID
        isinstance(params_dict.get("upload_playlist_ID"), str),
        # Shorts
        isinstance(params_dict.get("keep_shorts"), bool),
        # Verbosity
        all(v in verbosity_options for v in params_dict.get("verbosity", ["failsafe"])),
        # Title
        params_dict.get("required_in_title") is None
        or all(isinstance(item, str) for item in params_dict.get("required_in_title")),
        # Title
        params_dict.get("banned_in_title") is None
        or all(isinstance(item, str) for item in params_dict.get("banned_in_title")),
        # Duration
        params_dict.get("allowed_durations") is None
        or (
            len(params_dict.get("allowed_durations")) == 2
            and all(
                isinstance(item, int) and item >= 0
                for item in params_dict.get("allowed_durations")
            )
        ),
        # Duplicates
        isinstance(params_dict.get("keep_duplicates"), bool),
        # Languages
        params_dict.get("preferred_languages") is None
        or all(
            item in languages_options for item in params_dict.get("preferred_languages")
        ),
        # Tags
        params_dict.get("required_tags") is None
        or all(isinstance(item, str) for item in params_dict.get("required_tags")),
        # Tags
        params_dict.get("banned_tags") is None
        or all(isinstance(item, str) for item in params_dict.get("banned_tags")),
        # Upload date
        (
            isinstance(params_dict.get("run_frequency"), int)
            and params_dict.get("run_frequency") > 0
        )
        or params_dict.get("run_frequency") in frequency_options,
        # Definition
        params_dict.get("lowest_definition") is None
        or params_dict.get("lowest_definition") in definition_options,
        # Dimension
        params_dict.get("preferred_dimensions") is None
        or all(
            item in dimension_options
            for item in params_dict.get("preferred_dimensions")
        ),
        # Resolution
        params_dict.get("lowest_resolution") is None
        or params_dict.get("lowest_resolution") in resolution_options,
        # Framerate
        params_dict.get("lowest_framerate") is None
        or (
            isinstance(params_dict.get("lowest_framerate"), int)
            and params_dict.get("lowest_framerate") > 0
        ),
        # Projection
        params_dict.get("preferred_projections") is None
        or all(
            item in projections_options
            for item in params_dict.get("preferred_projections")
        ),
        # Caption
        isinstance(params_dict.get("require_captions"), bool),
        # Caption
        params_dict.get("caption_options") is None
        and params_dict.get("require_captions") is False
        or isinstance(params_dict.get("caption_options"), dict)
        and all(
            item in caption_options
            for item in params_dict.get("caption_options").keys()
        ),
        # Title emojis
        isinstance(params_dict.get("ignore_title_emojis"), bool),
        # Title punctuation
        isinstance(params_dict.get("ignore_title_punctuation"), bool),
        # Title case
        isinstance(params_dict.get("ignore_title_case"), bool),
        # Extra channels
        isinstance(params_dict.get("include_extra_channels"), bool),
        # Extra channels
        params_dict.get("extra_channel_handles") is None
        or all(
            isinstance(item, str) for item in params_dict.get("extra_channel_handles")
        ),
    ]

    ok = all(checks)

    return ok


def check_playlist_id(youtube, user_info: dict, test_playlist_ID: str) -> bool:
    """Checks if the user can upload the playlist provided in the paramaters file.

    Args:
        youtube (Resource): YT API resource
        user_info (dict): Dictionary containing information on the logged-in user channel
        test_playlist_ID (str): YT playlist ID to test

    Returns:
        (bool): True if the playlist belongs to the user, False otherwise.
    """
    user_channel_ID = user_info["items"][0]["id"]

    response = youtube.playlists().list(part="snippet", id=test_playlist_ID).execute()

    if "items" in response and len(response["items"]) > 0:
        playlist_owner = response["items"][0]["snippet"]["channelId"]

        if user_channel_ID == playlist_owner:
            return True
        else:
            print(
                "Invalid playlist ID: This playlist does not belong to you. Check the parameters file."
            )
            return False

    else:
        print(
            "Invalid playlist ID: This playlist does not exist. Check the parameters file."
        )
        return False


def check_version() -> tuple[str]:
    """Checks that the local software version is up to date with the latest GitHub release

    Returns:
        version, latest_release (tuple[str]): local version and latest release
    """
    setup_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "setup.py")
    )

    with open(setup_path) as setup_file:
        contents = setup_file.read()

        version = re.search(r"version=['\"]([^'\"]+)['\"]", contents).group(1)

        github_url = "https://api.github.com/repos/Killian42/QTube/releases/latest"

        try:
            response = requests.get(github_url)
            response.raise_for_status()  # Raise an error for non-200 status codes
            tag = response.json().get("tag_name")
            latest_release = tag.split("v")[-1]
        except requests.RequestException as e:
            latest_release = None
            print(f"Failed to check the latest release:\n{e}")

    return version, latest_release


def handle_http_errors(verbosity: list[str], func, *args, **kwargs):
    """Handles http errors when making API queries.
    If after 5 tries, the function could not be executed, it shuts the program down.

    Args:
        verbosity (list[str]): User defined verbosity
        func (function): Function to be executed, with its arguments and keyword arguments
        args (any): Arguments of func
        kwargs (any): Keyword arguments of func

    Returns:
        res (any): Whatever the function is supposed to return if no http error occur otherwise, it depends on the function
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


# Helpers
def print2(message: str, verb_level: list, verbosity: list) -> None:
    """Prints text in the terminal depending on the choosen verbosity

    Args:
        message (str): Text to be printed in the terminal
        verb_level (list[str]): Verbosity associated to the text
        verbosity (list[str]): User defined verbosity

    Returns:
        None
    """

    if any(v in verb_level for v in verbosity):
        print(message)


def split_list(input_list: list, chunk_size: int) -> list:
    """Splits a list into several lists with a specified length.
    If the number of elements is not divisible by the wanted size, one of the sub-lists will be shorter

    Args:
        input_list (list): List to be split
        chunk_size (int): Wanted length of the sub-lists

    Returns:
        (list): List of the sub-lists
    """
    return [
        input_list[i : i + chunk_size] for i in range(0, len(input_list), chunk_size)
    ]


def split_dict(input_dict: dict, chunk_size: int) -> list[dict]:
    """Splits a dictionary into several dictionaries with a specified length.
    If the number of elements is not divisible by the wanted size, one of the sub-dictionaries will be shorter

    Args:
        input_dict (dict): Dictionary to be split
        chunk_size (int): Wanted length of the sub-dictionaries

    Returns:
        (list[dict]): List of the sub-dictionaries
    """
    items = list(input_dict.items())
    return [
        {k: v for k, v in items[i : i + chunk_size]}
        for i in range(0, len(items), chunk_size)
    ]


def merge_dicts(list_of_dicts: list) -> dict:
    """Merges a list of dictionaries into one

    Args:
        list of dict (list): list of dictionaries to be merged

    Returns:
        (dict): single dictionary containing the the dictionaries from the list
    """
    return {key: value for d in list_of_dicts for key, value in d.items()}


def strip_emojis(text):
    """Strips emojis from a string

    Args:
        text (str): Text string containing emojis

    Returns:
        (str): Same Text string, but emojis are replaces by spaces
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
    """Strips punctuation from a string (all of these characters: !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~)

    Args:
        text (str): Text string containing punctuation

    Returns:
        (str): Same text string, but the punctuation is replaced by a space
    """
    translation_table = str.maketrans(string.punctuation, " " * len(string.punctuation))
    clean_text = text.translate(translation_table)
    return remove_multiple_spaces(clean_text)


def make_lowercase(text):
    """Converts all uppercase letters to lowercase from a string

    Args:
        text (str): Text string containing lowercase and uppercase letters

    Returns:
        (str): Same Text string, but all in lowercase
    """

    return text.lower()


def remove_multiple_spaces(text):
    """Removes multiple spaces in a string and replaces them with a single space.

    Args:
        text (str): Text string with multiple spaces

    Returns:
        (str): Same text string, but with multiple spaces replaced by a single space
    """
    return re.sub(" +", " ", text)


## Youtube API interactions


# Channels
def get_subscriptions(youtube, next_page_token=None) -> dict:
    """Retrieves the subscriptions of the logged user

    Args:
        youtube (Resource): YT API resource
        next_page_token (str): Token of the subscription page (optional)

    Returns:
        channels (dict): Dictionary of channel names (keys) and channel IDs (values)
    """
    channels = {}

    while True:
        response = (
            youtube.subscriptions()
            .list(
                part="snippet",
                mine=True,
                maxResults=50,
                order="alphabetical",
                pageToken=next_page_token,
            )
            .execute()
        )

        for item in response.get("items", []):
            title = item["snippet"]["title"]
            channel_id = item["snippet"]["resourceId"]["channelId"]
            channels[title] = channel_id

        next_page_token = response.get("nextPageToken")

        if not next_page_token:
            break

    return channels


def get_channel_info(youtube, handle: str):
    """Retrieves basic information about a YT channel

    Args:
        youtube (Resource): YT API resource
        handle (str): Handle of the YT channel

    Returns:
        response (dict): Dictionary containing basic information on the requested YT channel
    """
    channel = {}

    response = youtube.channels().list(part="snippet", forHandle=handle).execute()

    if "items" in response.keys():
        title = response["items"][0]["snippet"]["title"]
        channel_id = response["items"][0]["id"]
        channel[title] = channel_id
    else:
        print(
            f"Could not find a YT channel associated with the following handle: {handle}."
        )

    return channel


def get_uploads_playlists(youtube, channel_IDs: list[str]) -> list[str]:
    """Retrieves the upload playlists of YT channels

    Args:
        youtube (Resource): YT API ressource
        channel_IDs (list[str]): Channel IDs of YT channels

    Returns:
        upload_pl_ids (list[str]): IDs of the uploads playlist of the YT channels
    """
    channel_IDs_str = ",".join(channel_IDs)
    response = (
        youtube.channels().list(part="contentDetails", id=channel_IDs_str).execute()
    )
    # Create a dictionary to store the mapping between channel IDs and upload playlist IDs
    channel_to_upload_map = {
        item["id"]: item["contentDetails"]["relatedPlaylists"]["uploads"]
        for item in response.get("items", [])
    }

    # Generate the resulting list in the same order as the input channel IDs
    upload_pl_ids = [channel_to_upload_map[channel_ID] for channel_ID in channel_IDs]

    return upload_pl_ids


def get_user_info(youtube) -> dict:
    """Retrieves information about the logged-in user channel

    Args:
        youtube (Resource): YT API resource

    Returns:
        response (dict): Dictionary containing information on the logged-in user channel
    """
    response = (
        youtube.channels()
        .list(part="snippet,contentDetails,statistics", mine=True)
        .execute()
    )

    return response


# Playlists
def get_recent_videos(youtube, playlist_ID: str) -> dict:
    """Retrieves the last 5 videos of a YT playlist

    Args:
        youtube (Resource): YT API resource
        playlist_ID (str): ID of the playlist

    Returns:
        recent_vids (dict): Dictionary containing the ID (keys) and upload date (values) of the last 5 videos in the playlist
    """
    response = (
        youtube.playlistItems()
        .list(part="contentDetails", playlistId=playlist_ID, maxResults=5)
        .execute()
    )

    recent_vids = {
        item["contentDetails"]["videoId"]: {
            "upload day": dt.datetime.strptime(
                item["contentDetails"]["videoPublishedAt"].split("T")[0], "%Y-%m-%d"
            )
        }
        for item in response.get("items", [])
    }

    return recent_vids


def get_playlist_content(youtube, playlist_ID: str) -> list[str]:
    """Retrieves the IDs of videos saved in a YT playlist

    Args:
        youtube (Resource): YT API resource
        playlist_ID (str): ID of the playlist

    Returns:
        videos_IDs (list[str]): List containing the IDs of the videos saved in the playlist
    """
    next_page_token = None
    videos_IDs = []
    while True:
        response = (
            youtube.playlistItems()
            .list(
                part="contentDetails",
                playlistId=playlist_ID,
                maxResults=50,
                pageToken=next_page_token,
            )
            .execute()
        )

        temp_videos_IDs = [
            item["contentDetails"]["videoId"] for item in response.get("items")
        ]
        videos_IDs.extend(temp_videos_IDs)

        next_page_token = response.get("nextPageToken")

        if not next_page_token:
            break

    return videos_IDs


# Videos
def make_video_requests(youtube, video_IDs: list[str]) -> dict:
    """Retrieves information on a list of YT videos

    Args:
        youtube (Resource): YT API resource
        video_IDs (list[str]): List of video IDs

    Returns:
        response (dict[dict]): YT API response
    """
    video_IDs_str = ",".join(video_IDs)
    response = (
        youtube.videos().list(part="snippet,contentDetails", id=video_IDs_str).execute()
    )
    return response


def get_titles(
    youtube=None,
    response: dict = None,
    video_IDs: list[str] = None,
    use_API: bool = False,
) -> list[str]:
    """Retrieves the titles of a list of YT videos

    Args:
        youtube (Resource): YT API resource
        response (dict[dict]): YT API response from the make_video_request function
        video_IDs (list[str]): List of video IDs
        use_API (bool): Determines if a new API request is made or if the response dictionary is used

    Returns:
        titles (list[str]): List of YT videos titles
    """
    if use_API:
        video_IDs_str = ",".join(video_IDs)
        response = youtube.videos().list(part="snippet", id=video_IDs_str).execute()

    titles = [vid["snippet"]["title"] for vid in response["items"]]

    return titles


def get_tags(
    youtube=None,
    response: dict = None,
    video_IDs: list[str] = None,
    use_API: bool = False,
) -> list[list[str] | None]:
    """Retrieves the tags of YT videos

    Args:
        youtube (Resource): YT API resource
        response (dict[dict]): YT API response from the make_video_request function
        video_IDs (list[str]): List of video IDs
        use_API (bool): Determines if a new API request is made or if the response dictionary is used

    Returns:
        tags (list[list[str]|None]): List of YT videos tags, or None if there are no tags for this video
    """
    if use_API:
        video_IDs_str = ",".join(video_IDs)
        response = youtube.videos().list(part="snippet", id=video_IDs_str).execute()

    tags = [
        vid["snippet"]["tags"] if "tags" in vid["snippet"] else None
        for vid in response.get("items", [])
    ]

    return tags


def get_descriptions(
    youtube=None,
    response: dict = None,
    video_IDs: list[str] = None,
    use_API: bool = False,
) -> list[str]:
    """Retrieves the descriptions of YT videos

    Args:
        youtube (Resource): YT API resource
        response (dict[dict]): YT API response from the make_video_request function
        video_IDs (list[str]): List of video IDs
        use_API (bool): Determines if a new API request is made or if the response dictionary is used

    Returns:
        description (list[str]): YT videos descriptions
    """
    if use_API:
        video_IDs_str = ",".join(video_IDs)  # Join the video IDs with commas
        response = youtube.videos().list(part="snippet", id=video_IDs_str).execute()

    descriptions = [vid["snippet"]["description"] for vid in response.get("items", [])]
    return descriptions


def get_durations(
    youtube=None,
    response: dict = None,
    video_IDs: list[str] = None,
    use_API: bool = False,
) -> list[float]:
    """Retrieves the duration of YT videos

    Args:
        youtube (Resource): YT API resource
        response (dict[dict]): YT API response from the make_video_request function
        video_IDs (list[str]): List of video IDs
        use_API (bool): Determines if a new API request is made or if the response dictionary is used

    Returns:
        durations (list[float]): List of YT videos durations in seconds
    """
    if use_API:
        video_IDs_str = ",".join(video_IDs)
        response = (
            youtube.videos().list(part="contentDetails", id=video_IDs_str).execute()
        )

    durations_iso = [vid["contentDetails"]["duration"] for vid in response["items"]]
    durations = [isodate.parse_duration(d).total_seconds() for d in durations_iso]
    return durations


def get_languages(
    youtube=None,
    response: dict = None,
    video_IDs: list[str] = None,
    use_API: bool = False,
) -> list[str]:
    """Retrieves the original language of YT videos

    Args:
        youtube (Resource): YT API resource
        response (dict[dict]): YT API response from the make_video_request function
        video_IDs (list[str]): List of video IDs
        use_API (bool): Determines if a new API request is made or if the response dictionary is used

    Returns:
        languages (list[str]): List of YT videos languages
    """
    if use_API:
        video_IDs_str = ",".join(video_IDs)
        response = youtube.videos().list(part="snippet", id=video_IDs_str).execute()

    languages = [
        (
            vid["snippet"]["defaultAudioLanguage"]
            if "defaultAudioLanguage" in vid["snippet"]
            else (
                vid["snippet"]["defaultLanguage"]
                if "defaultLanguage" in vid["snippet"]
                else "unknown"
            )
        ).split("-")[
            0
        ]  # strips regional specifiers
        for vid in response["items"]
    ]

    return languages


def get_dimensions(
    youtube=None,
    response: dict = None,
    video_IDs: list[str] = None,
    use_API: bool = False,
) -> list[str]:
    """Retrieves the dimension of YT videos (2D or 3D)

    Args:
        youtube (Resource): YT API resource
        response (dict[dict]): YT API response from the make_video_request function
        video_IDs (list[str]): List of video IDs
        use_API (bool): Determines if a new API request is made or if the response dictionary is used

    Returns:
        dimensions (list[str]): List of YT videos dimensions
    """
    if use_API:
        video_IDs_str = ",".join(video_IDs)
        response = (
            youtube.videos().list(part="contentDetails", id=video_IDs_str).execute()
        )

    dimensions = [vid["contentDetails"]["dimension"] for vid in response["items"]]
    return dimensions


def get_definitions(
    youtube=None,
    response: dict = None,
    video_IDs: list[str] = None,
    use_API: bool = False,
) -> list[str]:
    """Retrieves the definition (sd or hd) of YT videos

    Args:
        youtube (Resource): YT API resource
        response (dict[dict]): YT API response from the make_video_request function
        video_IDs (list[str]): List of video IDs
        use_API (bool): Determines if a new API request is made or if the response dictionary is used

    Returns:
        definitions (list[str]): List of YT videos definitions
    """
    if use_API:
        video_IDs_str = ",".join(video_IDs)
        response = (
            youtube.videos().list(part="contentDetails", id=video_IDs_str).execute()
        )

    definitions = [vid["contentDetails"]["definition"] for vid in response["items"]]
    return definitions


def get_resolutions(video_IDs: list[str] = None) -> dict[str, list[int]]:
    """Retrieves the resolutions of YT videos.
    This function does not rely on the YT API but on a third party
    package (pytube), so it takes longer to run.

    Args:
        video_IDs (list[str]): List of video IDs

    Returns:
        resolutions (dict[str, list[int]]): Dictionary mapping video IDs to the resolutions
    """
    base_url = "http://youtube.com/watch?v"
    resolutions = {}

    for vid_ID in video_IDs:
        url = f"{base_url}={vid_ID}"

        try:
            yt = YouTube(url)
            vid_resolutions = list(
                {
                    int(stream.resolution.split("p")[0])
                    for stream in yt.streams.filter(type="video")
                }
            )
            resolutions[vid_ID] = vid_resolutions
        except Exception as e:
            print(f"Error processing video {vid_ID}: {e}")

    return resolutions


def get_framerates(video_IDs: list[str] = None) -> dict[str, list[int]]:
    """Retrieves the framerates of YT videos.
    This function does not rely on the YT API but on a third party
    package (pytube), so it takes longer to run.

    Args:
        video_IDs (list[str]): List of video IDs

    Returns:
        framerates (dict[str, list[int]]): Dictionary mapping video IDs to the framerates
    """
    base_url = "http://youtube.com/watch?v"
    framerates = {}

    for vid_ID in video_IDs:
        url = f"{base_url}={vid_ID}"

        try:
            yt = YouTube(url)
            vid_framerates = list(
                {stream.fps for stream in yt.streams.filter(type="video")}
            )
            framerates[vid_ID] = vid_framerates
        except Exception as e:
            print(f"Error processing video {vid_ID}: {e}")

    return framerates


def get_projections(
    youtube=None,
    response: dict = None,
    video_IDs: list[str] = None,
    use_API: bool = False,
) -> list[str]:
    """Retrieves the projection (360 or rectangular) of YT videos

    Args:
        youtube (Resource): YT API resource
        response (dict[dict]): YT API response from the make_video_request function
        video_IDs (list[str]): List of video IDs
        use_API (bool): Determines if a new API request is made or if the response dictionary is used

    Returns:
        projections (list[str]): List of YT videos projections
    """
    if use_API:
        video_IDs_str = ",".join(video_IDs)
        response = (
            youtube.videos().list(part="contentDetails", id=video_IDs_str).execute()
        )

    projections = [vid["contentDetails"]["projection"] for vid in response["items"]]
    return projections


def has_captions(
    youtube=None,
    response: dict = None,
    video_IDs: list[str] = None,
    use_API: bool = False,
) -> list[bool]:
    """Determines if YT videos have captions

    Args:
        youtube (Resource): YT API resource
        response (dict[dict]): YT API response from the make_video_request function
        video_IDs (list[str]): List of video IDs
        use_API (bool): Determines if a new API request is made or if the response dictionary is used

    Returns:
        captions (list[bool]): True if the video has captions, False otherwise
    """
    if use_API:
        video_IDs_str = ",".join(video_IDs)
        response = (
            youtube.videos().list(part="contentDetails", id=video_IDs_str).execute()
        )

    captions = [vid["contentDetails"]["caption"] for vid in response["items"]]
    return captions


def is_short(
    youtube=None,
    response: dict = None,
    video_IDs: list[str] = None,
    use_API: bool = False,
) -> list[str]:
    """Determines if videos are a short or not by putting a threshold on video duration

    Args:
        youtube (Resource): YT API resource
        response (dict[dict]): YT API response from the make_video_request function
        video_IDs (list[str]): List of video IDs
        use_API (bool): Determines if a new API request is made or if the response dictionary is used

    Returns:
        is_short (list[bool]): True if the video is shorter than 65 seconds, False otherwise
    """
    durations = get_durations(youtube, response, video_IDs, use_API=use_API)

    is_short = [True if length <= 65.0 else False for length in durations]

    return is_short


# Captions
def make_caption_requests(youtube, video_IDs: list[str]) -> dict[dict]:
    """Retrieves API caption responses of a list of YT videos

    Args:
        youtube (Resource): YT API resource
        video_IDs (list[str]): List of video IDs

    Returns:
        responses_dict (dict[dict]): Dictionary with video IDs as keys and YT API caption responses as values
    """
    responses_dict = {
        video_ID: youtube.captions().list(part="snippet", videoId=video_ID).execute()
        for video_ID in video_IDs
    }

    return responses_dict


def get_captions(
    youtube=None,
    response: dict = None,
    video_IDs: list[str] = None,
    use_API: bool = False,
) -> dict[dict]:
    """Retrieves the captions of YT videos

    Args:
        youtube (Resource): YT API resource
        response (dict[dict]): YT API response from the make_caption_request function
        video_IDs (list[str]): List of video IDs
        use_API (bool): Determines if a new API request is made or if the response dictionary is used

    Returns:
        captions_dict (dict[dict]): Dictionary with video IDs as keys and caption dictionaries as values
    """
    if use_API:
        response = make_caption_requests(youtube, video_IDs)

    captions_dict = {}
    for video_ID, vid_resp in response.items():
        caption_dict = {
            caption["id"]: caption["snippet"] for caption in vid_resp.get("items", [])
        }
        captions_dict.update({video_ID: caption_dict})

    return captions_dict


# Actions
def add_to_playlist(youtube, playlist_ID: str, video_ID: str) -> None:
    """Adds a  YT video to the YT playlist

    Args:
        youtube (Resource): YT API resource
        playlist_ID (str): Playlist ID
        video_ID (str): Video ID

    Returns:
        None
    """
    response = (
        youtube.playlistItems()
        .insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": playlist_ID,
                    "resourceId": {"kind": "youtube#video", "videoId": video_ID},
                }
            },
        )
        .execute()
    )
    return
