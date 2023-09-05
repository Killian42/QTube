### Libraries importation
from library import *

### User parameters loading
## File opening
user_param_dict = json.load(open("user_params.json"))

## Parameters checking
if check_user_params(user_param_dict) is not True:
    print("User defined parameters are not correct. Check the template and retry.")
    sys.exit()
else:
    print("The user defined parameters are correctly formatted.\n")

## Verbosity parameter
verb = user_param_dict["verbosity"]
print(f"You have choosen the following verbosity options: {verb}.\n")

### Youtube API login
credentials = None

## token.pickle stores the user's credentials from previously successful logins
if os.path.exists("token.pickle"):
    print2("Loading credentials from pickle file...", ["all", "credentials"], verb)

    with open("token.pickle", "rb") as token:
        credentials = pickle.load(token)

        print2("Credentials loaded from pickle file", ["all", "credentials"], verb)

## If there are no valid credentials available, then either refresh the token or log in.
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

### Building API resource
youtube = build("youtube", "v3", credentials=credentials)

### Actual code

## Dictionnary of all subscribed channels' names and IDs
tokens = handle_http_errors(verb, get_tokens, youtube)

subbed_channels_info = {}
for tk in tokens:
    subbed_partial_info = get_youtube_subscriptions(youtube, tk)
    subbed_channels_info.update(subbed_partial_info)

## Filtering on channel names
required_words = user_param_dict["required_in_channel_name"]
banned_words = user_param_dict["banned_in_channel_name"]

if required_words is None and banned_words is None:  # No filtering
    wanted_channels_info = subbed_channels_info

elif required_words is not None and banned_words is None:  # Required filtering
    wanted_channels_info = {
        k: v
        for k, v in subbed_channels_info.items()
        if any(aw in k for aw in required_words)
    }

elif required_words is None and banned_words is not None:  # Banned filtering
    wanted_channels_info = {
        k: v
        for k, v in subbed_channels_info.items()
        if not any(bw in k for bw in banned_words)
    }

else:  # Required and banned filtering
    wanted_channels_info = {
        k: v
        for k, v in subbed_channels_info.items()
        if any(aw in k for aw in required_words)
        and not any(bw in k for bw in banned_words)
    }

## Dictionnary of channels names and their associated upload playlist
wanted_channels_upload_playlists = {}
for ch_name, ch_Id in wanted_channels_info.items():
    upload_playlist = handle_http_errors(verb, get_uploads_playlists, youtube, ch_Id)
    desired_playlists_partial = {ch_name: upload_playlist}
    wanted_channels_upload_playlists.update(desired_playlists_partial)

## Dictionnary of the latest videos from selected channels
videos = {}
for ch_name, playlist_Id in wanted_channels_upload_playlists.items():
    latest_partial = handle_http_errors(verb, get_recent_videos, youtube, playlist_Id)

    if latest_partial == "ignore":
        print2(f"Channel {ch_name} has no public videos.", ["all", "func"], verb)
        continue

    for vid_info in latest_partial.values():
        vid_info.update(
            {"channel name": ch_name, "upload playlist": playlist_Id, "to add": True}
        )

    videos.update(latest_partial)

## Information retrieving on retrieved videos
for ID, vid_info in videos.items():
    # Title
    title = handle_http_errors(verb, get_title, youtube, ID)
    vid_info.update({"title": title})

    # Short
    short = handle_http_errors(verb, is_short, youtube, ID)
    short_dict = {"is short": short}

    vid_info.update(short_dict)

## Yesterday's date
yesterday = str(dt.date.today() - dt.timedelta(days=1))

## Filtering on videos information
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

videos_to_add = {k: v for k, v in videos.items() if v["to add"] == True}

## Adding selected videos to a playlist
playlist_ID = user_param_dict["upload_playlist_ID"]

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
