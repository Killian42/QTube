### Librairies ###
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


### Functions ###


## Checks ##
def check_user_params(params_dict):
    """Checks if the user defined parameters are correctly formatted

    Args:
        params_dict (dict): Dictionnary of the user defined parameters

    Returns:
        ok (boolean): True if all checks are passed, False otherwise
    """

    check_0 = not any(
        type(item) != str for item in params_dict["required_in_channel_name"]
    )
    check_1 = not any(
        type(item) != str for item in params_dict["banned_in_channel_name"]
    )
    check_2 = type(params_dict["upload_playlist_ID"]) == str
    check_3 = type(params_dict["keep_shorts"]) == bool
    check_4 = params_dict["verbosity"] in ["all", "none", "videos"]

    ok = bool(check_0 * check_1 * check_2 * check_3 * check_4)

    return ok


def handle_http_errors(func, *args, **kwargs):
    """Handles http errors when making API queries.
    If after 5 tries, the function could not be executed, it shuts the program down.

    Args:
        func (function): function to be executed, with its arguments and keyword arguments

    Returns:
        res (any): whatever the function is supposed to return if no http error occur
    """
    tries = ["1", "2", "3", "4", "5"]
    for t in tries:
        try:
            res = func(*args, **kwargs)
        except HttpError as err:
            print(
                f"During the execution of function {func.__name__}, error {err.status_code} occured: {err.reason}"
            )
            print(f"Retrying in 5 seconds. This was attempt number {t} out of 5.")
            time.sleep(5)
        else:
            print(f"{func.__name__} successfully executed.")
            return res
    print(
        f"Function {func.__name__} could not be executed after 5 tries. Please check your internet connection, Youtube's API status and retry later."
    )
    sys.exit()


## Channel interactions ##
def get_tokens(youtube):
    """Retrieves the tokens of the subscription pages of the logged user

    Args:
        youtube (_type_): YT API ressource

    Returns:
        tokens (list): List of the tokens of the subscription pages of the logged user
    """
    tokens = [""]
    response = youtube.subscriptions().list(part="snippet", mine=True).execute()
    while "nextPageToken" in response:
        tk = response["nextPageToken"]
        tokens.append(tk)
        response = (
            youtube.subscriptions()
            .list(part="snippet", mine=True, order="alphabetical", pageToken=tk)
            .execute()
        )
    return tokens


def get_youtube_subscriptions(youtube, next_page_token):
    """Retrieves the subscriptions of the logged user

    Args:
        youtube (_type_): YT API ressource
        next_page_token (str): Token of the subscription page

    Returns:
        channels (dict): Dictionnary of channel names (keys) and channel IDs (values)
    """
    channels = {}
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
    for i in range(0, len(response["items"])):
        b = {
            response["items"][i]["snippet"]["title"]: response["items"][i]["snippet"][
                "resourceId"
            ]["channelId"]
        }
        channels.update(b)
    return channels


def get_uploads_playlists(youtube, channel_ID):
    """Retrieves the upload playlist of a YT channel

    Args:
        youtube (_type_): YT API ressource
        channel_ID (str): Channel ID of a YT channel

    Returns:
        upload_pl_id (str): ID of the uploads playlist of the YT channel
    """
    response = (
        youtube.channels()
        .list(part="contentDetails", id=channel_ID, maxResults=50)
        .execute()
    )
    upload_pl_id = response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    return upload_pl_id


def get_recent_videos(youtube, playlist_ID):
    """Retrieves the last 5 videos of a YT playlist

    Args:
        youtube (_type_): YT API ressource
        playlist_ID (str): ID of the playlist

    Returns:
        recent_vids (dict): Dictionnary containing the ID (keys) and upload date (values) of the last 5 videos in the playlist
    """
    response = (
        youtube.playlistItems()
        .list(part="contentDetails", playlistId=playlist_ID)
        .execute()
    )
    recent_vids = {}
    nb_vids = len(response["items"])

    for i in range(nb_vids):
        date = response["items"][i]["contentDetails"]["videoPublishedAt"].split("T")[0]
        vid_id = response["items"][i]["contentDetails"]["videoId"]
        temp = {vid_id: {"upload day": date}}

        recent_vids.update(temp)
    return recent_vids


## Video interactions ##
def get_title(youtube, video_ID):
    """Retrieves the title of a YT video

    Args:
        youtube (_type_): YT API ressource
        video_ID (str): ID of the video

    Returns:
        title (str): Title of the YT video
    """
    response = youtube.videos().list(part="snippet", id=video_ID).execute()
    title = response["items"][0]["snippet"]["title"]
    return title


def get_tags(youtube, video_ID):
    """Retrieves the tags of a YT video

    Args:
        youtube (_type_): YT API ressource
        video_ID (str): ID of the video

    Returns:
        tags (lst): Tags of the YT video
    """
    response = youtube.videos().list(part="snippet", id=video_ID).execute()
    tags = response["items"][0]["snippet"]["tags"]
    return tags


def get_description(youtube, video_ID):
    """Retrieves the description of a YT video

    Args:
        youtube (_type_): YT API ressource
        video_ID (str): ID of the video

    Returns:
        description (lst): Description of the YT video
    """
    response = youtube.videos().list(part="snippet", id=video_ID).execute()

    description = response["items"][0]["snippet"]["description"]
    return description


def get_duration(youtube, video_ID):
    """Retrieves the duration of a YT video

    Args:
        youtube (_type_): YT API ressource
        video_ID (str): ID of the YT video

    Returns:
        duration (float): Duration of the YT video in seconds
    """

    response = youtube.videos().list(part="contentDetails", id=video_ID).execute()

    duration_iso = response["items"][0]["contentDetails"]["duration"]
    duration = isodate.parse_duration(duration_iso).total_seconds()
    return duration


def is_short(youtube, video_ID):
    """Determines if a video is a short or not by putting a threshold on video duration

    Args:
        youtube (_type_): YT API ressource
        video_ID (str): ID of the YT video

    Returns:
        (boolean): True if the video is shorter than 65 seconds, False otherwise
    """

    length = get_duration(youtube, video_ID)

    if length <= 65.0:
        return True
    else:
        return False


## Actions ##
def add_to_playlist(youtube, playlist_ID, video_ID):
    """Adds a  YT video to the YT playlist

    Args:
        youtube (_type_): YT API ressource
        playlist_ID (str): ID of the playlist
        video_ID (str): ID of the video

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
                    # "position": 0,
                    "resourceId": {"kind": "youtube#video", "videoId": video_ID},
                }
            },
        )
        .execute()
    )
    return


def print2(message, verb_level, verbosity):
    """Prints text in the terminal depending on the choosen verbosity

    Args:
        message (str): Text to be printed in the terminal
        verb_level (str or str lst): Verbosity associated to the text
        verbosity (str): User defined verbosity

    Returns:
        None
    """
    if type(verb_level) == str:
        verb_level = [verb_level]

    if verbosity in verb_level:
        print(message)
