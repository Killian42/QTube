import os
import re
import requests


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
        and params_dict.get("include_extra_channels") is False
        or isinstance(params_dict.get("extra_channel_handles"), list)
        and all(
            isinstance(item, str) for item in params_dict.get("extra_channel_handles")
        ),
        # Override JSON parameters
        isinstance(params_dict.get("override_json"), bool),
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
    setup_path = os.path.abspath(os.path.join("..", "setup.py"))

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

    return version, latest_release


def compare_software_versions(version1, version2):
    """Compare two software versions, using version2 as the reference against which version1 is compared.

    Args:
        version1 (str): Software version to be compared (without the v).
        version2 (str): Reference software version (without the v).

    Returns:
        (str): A comment on version1's relationship to version2 (i.e., older, newer or same).
    """
    arr1 = list(map(int, version1.split(".")))
    arr2 = list(map(int, version2.split(".")))
    n = len(arr1)
    m = len(arr2)

    # Pad the shorter list with zeros
    arr1 += [0] * (m - n) if m > n else []
    arr2 += [0] * (n - m) if n > m else []

    for i in range(len(arr1)):
        if arr1[i] > arr2[i]:
            return "newer"
        elif arr2[i] > arr1[i]:
            return "older"
    return "same"
