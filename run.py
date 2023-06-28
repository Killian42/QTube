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

from library import *

### User parameters loading ###
user_param_dict = json.load(open("user_params.json"))

### Youtube API login ###
credentials = None

# token.pickle stores the user's credentials from previously successful logins
if os.path.exists("token.pickle"):
    print("Loading credentials from pickle file...")

    with open("token.pickle", "rb") as token:
        credentials = pickle.load(token)

        print("Credentials loaded from pickle file")

# If there are no valid credentials available, then either refresh the token or log in.
if not credentials or not credentials.valid:
    if credentials and credentials.expired and credentials.refresh_token:
        print("Refreshing access token...")

        credentials.refresh(Request())
        print("Access token refreshed")
    else:
        print("Fetching New Tokens...")
        flow = InstalledAppFlow.from_client_secrets_file(
            "client_secrets.json", scopes=["https://www.googleapis.com/auth/youtube"]
        )

        flow.run_local_server(
            port=8080, prompt="consent", authorization_prompt_message=""
        )

        credentials = flow.credentials

        print("New token fetched")

        # Save the credentials for the next run
        with open("token.pickle", "wb") as f:
            print("Saving Credentials for Future Use...")

            pickle.dump(credentials, f)
            print("Credentials saved")

### Retrieving data ###
youtube = build("youtube", "v3", credentials=credentials)

### Actual code ###
# Gives a dictionnary of all subscribed channels' names and IDs#
tries = ["1", "2", "3", "4", "5"]
for t in tries:
    try:
        tokens = get_tokens(youtube)
    except HttpError as err:
        print(
            "Could not get subscription tokens, retrying in 5 seconds. This was attempt number "
            + t
            + " out of 5."
        )
        time.sleep(5)
    else:
        print("Subscription tokens successfully retrieved.")
        break

subbed_channels_info = {}
for tk in tokens:
    subbed_partial_info = get_youtube_subscriptions(youtube, tk)
    subbed_channels_info.update(subbed_partial_info)

# Gives a dictionnary of desired channels' names and IDs#
word_filter = user_param_dict["words_in_channel_names"]

wanted_channels_info = {
    k: v for k, v in subbed_channels_info.items() if any(w in k for w in word_filter)
}

# Gives a dictionnary of the channels names and their upload playlist#
wanted_channels_upload_playlists = {}
for ch_name, ch_Id in wanted_channels_info.items():
    upload_playlist = get_uploads_playlists(youtube, ch_Id)
    desired_playlists_partial = {ch_name: upload_playlist}
    wanted_channels_upload_playlists.update(desired_playlists_partial)
# try to use dict comprehension here

# Gives yesterday's date#
yesterday = str(dt.date.today() - dt.timedelta(days=1))

# Check if videos were uploaded yesterday in the playlist#
latest_videos = {}
for ch_name, playlist_Id in wanted_channels_upload_playlists.items():
    try:
        latest_partial = get_recent_videos(youtube, playlist_Id)
    except HttpError as err:
        print(
            "Channel: ",
            ch_name,
            " throws an HTTP error.\n",
            "Their upload playlist ID is: ",
            playlist_Id,
        )
        pass
    for k, v in latest_partial.items():
        if k in latest_videos.keys():
            latest_videos[k] += v
        else:
            temp = {k: v}
            latest_videos.update(temp)

# Gives a list of the IDs of the videos that were uploaded yesterday#
videos_to_add = latest_videos.get(yesterday)

# Adds the videos to a playlist#
playlist_ID = user_param_dict["upload_playlist_ID"]

if videos_to_add is not None:  # Checks if there's actually videos to add
    print("\n")
    print("Number of videos added: ", len(videos_to_add))
    print("The videos added to the specified playlist are: \n")
    for vid_ID in videos_to_add:
        add_to_playlist(youtube, playlist_ID, vid_ID)

        print(get_title(youtube, vid_ID) + " (ID: " + vid_ID + ")")
else:
    print("No videos from yesterday to add.")
