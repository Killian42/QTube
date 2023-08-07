### Librairy importation ###
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
        print("Error " + str(err.status_code) + " occured:" + err.reason)
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
allowed_words = user_param_dict["required_in_channel_name"]
banned_words = user_param_dict["banned_in_channel_name"]

wanted_channels_info = {
    k: v for k, v in subbed_channels_info.items() if any(aw in k for aw in allowed_words) and not any(bw in k for bw in banned_words)
}

# Gives a dictionnary of the channels names and their upload playlist#
wanted_channels_upload_playlists = {}
for ch_name, ch_Id in wanted_channels_info.items():
    upload_playlist = get_uploads_playlists(youtube, ch_Id)
    desired_playlists_partial = {ch_name: upload_playlist}
    wanted_channels_upload_playlists.update(desired_playlists_partial)
# try to use dict comprehension here

# Gives a dictionnary of the latest videos from the selected channels#
videos = {}
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

    for vid_info in latest_partial.values():
        vid_info.update(
            {"channel name": ch_name, "upload playlist": playlist_Id, "to add": True}
        )
    # latest_partial.update()

    videos.update(latest_partial)

# Adds info to the info dictionnary for each video
for ID, vid_info in videos.items():
    # Tags
    try:
        tags = get_tags(youtube, ID)
        tags_dict = {"tags": tags}
    except:
        tags_dict = {"tags": ["No tags"]}

    vid_info.update(tags_dict)

    # Title
    title = get_title(youtube, ID)
    vid_info.update({"title": title})

    # Short
    short = is_short(youtube, ID)
    short_dict = {"is short": short}

    vid_info.update(short_dict)

# Gives yesterday's date#
yesterday = str(dt.date.today() - dt.timedelta(days=1))

# Applies filters#
for ID, vid_info in videos.items():
    # Upload day
    upload_day = vid_info["upload day"]
    if upload_day != yesterday:
        vid_info.update({"to add": False})
    else:
        pass
    # Short
    if user_param_dict["keep_shorts"] == False and vid_info["is short"] == True:
        vid_info.update({"to add": False})
    else:
        pass

# Adds the videos to a playlist#
playlist_ID = user_param_dict["upload_playlist_ID"]

videos_to_add = {k: v for k, v in videos.items() if v["to add"] == True}

if videos_to_add is not None:  # Checks if there's actually videos to add
    print("\n")
    print("Number of videos added: ", len(videos_to_add))
    for ID, vid_info in videos_to_add.items():
        add_to_playlist(youtube, playlist_ID, ID)

        print(
            "From "
            + vid_info["channel name"]
            + ", the video named: "
            + vid_info["title"]
            + " was added."
        )
else:
    print("No videos from yesterday to add.")
