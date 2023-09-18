### Libraries
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

import os
import pickle
import datetime as dt
import time
import json
import isodate
import sys


### Functions


## Local interactions


# Checks
def check_user_params(params_dict: dict) -> bool:
    """Checks if the user defined parameters are correctly formatted

    Args:
        params_dict (dict): Dictionnary of the user defined parameters

    Returns:
        ok (bool): True if all checks are passed, False otherwise
    """

    check_0 = params_dict.get("required_in_channel_name") == None or not any(
        type(item) != str for item in params_dict.get("required_in_channel_name")
    )
    check_1 = params_dict.get("banned_in_channel_name") == None or not any(
        type(item) != str for item in params_dict.get("banned_in_channel_name")
    )
    check_2 = type(params_dict.get("upload_playlist_ID")) == str
    check_3 = type(params_dict.get("keep_shorts")) == bool
    check_4 = params_dict.get("verbosity") == None or all(
        v in ["all", "videos", "credentials", "func"]
        for v in params_dict.get("verbosity")
    )

    ok = bool(check_0 * check_1 * check_2 * check_3 * check_4)

    return ok


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
                    "Your quota limit has been reached, please try again in a few hours. \nYou can check your usage at the following url: https://console.cloud.google.com/apis/dashboard"
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
            "upload day": item["contentDetails"]["videoPublishedAt"].split("T")[0]
        }
        for item in response.get("items", [])
    }

    return recent_vids


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

    titles = [vid["snippet"]["title"] for vid in response.get("items")]

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

    descriptions = [vid["snippet"]["description"] for vid in response["items"]]
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
