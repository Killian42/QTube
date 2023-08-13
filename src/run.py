### Libraries importation ###
from library import *

### User parameters loading ###
user_param_dict = json.load(open("user_params.json"))
verb = user_param_dict["verbosity"]

if check_user_params(user_param_dict) is not True:
    print("User defined parameters are not correct. Check the template and retry.")
    sys.exit()
else:
    print(
        f"The user defined parameters are correctly formatted.\nYou have choosen the following verbosity options: {verb}.\n"
    )


### Youtube API login ###
credentials = None

# token.pickle stores the user's credentials from previously successful logins
if os.path.exists("token.pickle"):
    print2("Loading credentials from pickle file...", ["all", "credentials"], verb)

    with open("token.pickle", "rb") as token:
        credentials = pickle.load(token)

        print2("Credentials loaded from pickle file", ["all", "credentials"], verb)

# If there are no valid credentials available, then either refresh the token or log in.
if not credentials or not credentials.valid:
    if credentials and credentials.expired and credentials.refresh_token:
        print2("Refreshing access token...", ["all", "credentials"], verb)

        credentials.refresh(Request())
        print2("Access token refreshed\n", ["all", "credentials"], verb)
    else:
        print2("Fetching New Tokens...", ["all", "credentials"], verb)
        flow = InstalledAppFlow.from_client_secrets_file(
            "client_secrets.json", scopes=["https://www.googleapis.com/auth/youtube"]
        )

        flow.run_local_server(
            port=8080, prompt="consent", authorization_prompt_message=""
        )

        credentials = flow.credentials

        print2("New token fetched\n", ["all", "credentials"], verb)

        # Save the credentials for the next run
        with open("token.pickle", "wb") as f:
            print2("Saving Credentials for Future Use...", ["all", "credentials"], verb)

            pickle.dump(credentials, f)
            print2("Credentials saved\n", ["all", "credentials"], verb)

### Retrieving data ###
youtube = build("youtube", "v3", credentials=credentials)

### Actual code ###
# Gives a dictionnary of all subscribed channels' names and IDs#
tokens = handle_http_errors(verb, get_tokens, youtube)

subbed_channels_info = {}
for tk in tokens:
    subbed_partial_info = get_youtube_subscriptions(youtube, tk)
    subbed_channels_info.update(subbed_partial_info)

# Gives a dictionnary of desired channels' names and IDs#
allowed_words = user_param_dict["required_in_channel_name"]
banned_words = user_param_dict["banned_in_channel_name"]

wanted_channels_info = {
    k: v
    for k, v in subbed_channels_info.items()
    if any(aw in k for aw in allowed_words) and not any(bw in k for bw in banned_words)
}

# Gives a dictionnary of the channels names and their upload playlist#
wanted_channels_upload_playlists = {}
for ch_name, ch_Id in wanted_channels_info.items():
    upload_playlist = handle_http_errors(verb, get_uploads_playlists, youtube, ch_Id)
    desired_playlists_partial = {ch_name: upload_playlist}
    wanted_channels_upload_playlists.update(desired_playlists_partial)
# try to use dict comprehension here

# Gives a dictionnary of the latest videos from the selected channels#
videos = {}
for ch_name, playlist_Id in wanted_channels_upload_playlists.items():
    # try:
    #     latest_partial = get_recent_videos(youtube, playlist_Id)
    # except HttpError as err:
    #     print2(
    #         "Channel: ",
    #         ch_name,
    #         " throws an HTTP error.\n",
    #         "Their upload playlist ID is: ",
    #         playlist_Id,
    #     )
    #     pass

    latest_partial = handle_http_errors(verb, get_recent_videos, youtube, playlist_Id)

    for vid_info in latest_partial.values():
        vid_info.update(
            {"channel name": ch_name, "upload playlist": playlist_Id, "to add": True}
        )

    videos.update(latest_partial)

# Adds info to the info dictionnary for each video
for ID, vid_info in videos.items():
    # Tags
    try:
        tags = handle_http_errors(verb, get_tags, youtube, ID)
        tags_dict = {"tags": tags}
    except:
        tags_dict = {"tags": ["No tags"]}

    vid_info.update(tags_dict)

    # Title
    title = handle_http_errors(verb, get_title, youtube, ID)
    vid_info.update({"title": title})

    # Short
    short = handle_http_errors(verb, is_short, youtube, ID)
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
    print2(f"Number of videos added: {len(videos_to_add)}", ["all", "videos"], verb)
    for ID, vid_info in videos_to_add.items():
        handle_http_errors(verb, add_to_playlist, youtube, playlist_ID, ID)

        print2(
            f"From {vid_info['channel name']}, the video named: {vid_info['title']} was added.",
            ["all", "videos"],
            verb,
        )
else:
    print2("No videos from yesterday to add.", ["all", "videos"], verb)
