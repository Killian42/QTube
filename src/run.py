### Libraries importation
from library import *

### User parameters loading
## File opening
user_params_dict = json.load(open("user_params.json"))

## Parameters checking
if check_user_params(user_params_dict) is not True:
    print("User defined parameters are not correct. Check the template and retry.")
    sys.exit()
else:
    print("The user defined parameters are correctly formatted.\n")

## Verbosity options
verb = user_params_dict.get("verbosity")
print(f"The following verbosity options are enabled: {verb}.\n")

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

### Code

## Checking the playlist ID
playlist_ID = user_params_dict.get("upload_playlist_ID")
user_info = handle_http_errors(verb, get_user_info, youtube)
if not handle_http_errors(verb, check_playlist_id, youtube, user_info, playlist_ID):
    sys.exit()


## Dictionnary of subscribed channel names and IDs
subbed_channels_info = handle_http_errors(verb, get_subscriptions, youtube)

## Filtering on channel names
required_channel_words = user_params_dict.get("required_in_channel_name")
banned_channel_words = user_params_dict.get("banned_in_channel_name")

if required_channel_words is None and banned_channel_words is None:  # No filtering
    wanted_channels_info = subbed_channels_info

elif (
    required_channel_words is not None and banned_channel_words is None
):  # Required filtering
    wanted_channels_info = {
        k: v
        for k, v in subbed_channels_info.items()
        if any(rw in k for rw in required_channel_words)
    }

elif (
    required_channel_words is None and banned_channel_words is not None
):  # Banned filtering
    wanted_channels_info = {
        k: v
        for k, v in subbed_channels_info.items()
        if not any(bw in k for bw in banned_channel_words)
    }

else:  # Required and banned filtering
    wanted_channels_info = {
        k: v
        for k, v in subbed_channels_info.items()
        if any(rw in k for rw in required_channel_words)
        and not any(bw in k for bw in banned_channel_words)
    }

## Dictionnary of channels names and their associated upload playlist
split_channels = split_dict(wanted_channels_info, 50)

wanted_channels_upload_playlists = {}
for sub_dict in split_channels:
    partial = handle_http_errors(
        verb, get_uploads_playlists, youtube, list(sub_dict.values())
    )
    partial_dict = dict(zip(list(sub_dict.keys()), partial))
    wanted_channels_upload_playlists.update(partial_dict)


## Dictionnary of the latest videos from selected channels
videos = {}
for ch_name, playlist_Id in wanted_channels_upload_playlists.items():
    latest_partial = handle_http_errors(verb, get_recent_videos, youtube, playlist_Id)

    if latest_partial == "ignore":
        print2(f"Channel {ch_name} has no public videos.", ["all", "func"], verb)
        continue

    videos.update(
        {
            vid_id: {
                **vid_info,
                "channel name": ch_name,
                "upload playlist": playlist_Id,
                "to add": True,
            }
            for vid_id, vid_info in latest_partial.items()
        }
    )


## Upload day filtering
yesterday = str(dt.date.today() - dt.timedelta(days=1))  # Yesterday's date
for vid_ID, vid_info in videos.items():
    if vid_info.get("upload day") != yesterday:
        vid_info.update({"to add": False})


## Additional information retrieving on the videos
split_videos = split_dict(videos, 50)

responses = {}
for sub_dict in split_videos:
    partial = handle_http_errors(verb, make_video_requests, youtube, sub_dict.keys())

    if len(responses) == 0:  # first run of the loop
        responses.update(partial)
    else:
        vid_dicts = partial.get("items")
        responses.get("items").extend(vid_dicts)


# Titles retrieving
titles = get_titles(response=responses)

# Duration retrieving
durations = get_durations(response=responses)

# Shorts retrieving
if user_params_dict.get("keep_shorts") is False:
    shorts = is_short(response=responses)

## Videos' information updating
for index, (vid_ID, vid_info) in enumerate(videos.items()):
    # Title
    vid_info.update({"title": titles[index]})

    # Duration
    vid_info.update({"duration": durations[index]})

    # Short
    if user_params_dict.get("keep_shorts") is False:
        vid_info.update({"is short": shorts[index]})

## Additional information filtering
required_title_words = user_params_dict.get("required_in_video_title")
banned_title_words = user_params_dict.get("banned_in_video_title")

min_max_durations = user_params_dict.get("allowed_durations")

# Title filtering
if required_title_words is None and banned_title_words is None:  # No filtering
    pass

elif (
    required_title_words is not None and banned_title_words is None
):  # Required filtering
    for vid_ID, vid_info in videos.items():
        if vid_info.get("to add") is False:
            continue
        elif any(rw in vid_info.get("title") for rw in required_title_words):
            continue
        else:
            vid_info.update({"to add": False})

elif (
    required_title_words is None and banned_title_words is not None
):  # Banned filtering
    for vid_ID, vid_info in videos.items():
        if vid_info.get("to add") is False:
            continue
        elif not any(bw in vid_info.get("title") for bw in banned_title_words):
            continue
        else:
            vid_info.update({"to add": False})

else:  # Required and banned filtering
    for vid_ID, vid_info in videos.items():
        if vid_info.get("to add") is False:
            continue
        elif any(
            rw in vid_info.get("title") for rw in required_title_words
        ) and not any(bw in vid_info.get("title") for bw in banned_title_words):
            continue
        else:
            vid_info.update({"to add": False})

# Duration filtering
if min_max_durations is not None:
    for vid_info in videos.values():
        if vid_info.get("to add") is False:
            continue
        elif (
            min_max_durations[0] * 60.0
            <= vid_info.get("duration")
            <= min_max_durations[-1] * 60.0
        ):
            pass
        else:
            vid_info.update({"to add": False})

# Short filtering
if user_params_dict.get("keep_shorts") is False:
    for vid_ID, vid_info in videos.items():
        if vid_info.get("to add") is False:
            continue
        elif vid_info.get("is short"):
            vid_info.update({"to add": False})

videos_to_add = {k: v for k, v in videos.items() if v.get("to add")}

## Adding selected videos to a playlist
if videos_to_add is not None:  # Checks if there's actually videos to add
    print2(f"Number of videos added: {len(videos_to_add)}", ["all", "videos"], verb)
    for vid_ID, vid_info in videos_to_add.items():
        handle_http_errors(verb, add_to_playlist, youtube, playlist_ID, vid_ID)

        print2(
            f"From {vid_info.get('channel name')}, the video named: {vid_info.get('title')} was added.",
            ["all", "videos"],
            verb,
        )
else:
    print2("No videos from yesterday to add.", ["all", "videos"], verb)
