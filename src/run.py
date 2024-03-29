### Libraries importation
from library import *

### Software version checking
version, latest_release = check_version()
if version != latest_release and latest_release is not None:
    latest_url = "https://github.com/Killian42/QTube/releases/latest"
    print(
        f"You are currently running version {version}.\nConsider upgrading to {latest_release} at {latest_url}."
    )

### User parameters loading
## File opening
try:
    user_params_dict = json.load(open("user_params.json"))
except FileNotFoundError:
    print(
        f"Error: user_params.json file not found.\nCheck that your parameter file is properly named."
    )
    sys.exit()
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    sys.exit()

## Parameters checking
if check_user_params(user_params_dict) is not True:
    print("User defined parameters are not correct. Check the template and retry.")
    sys.exit()
else:
    print("The user defined parameters are correctly formatted.\n")

## Verbosity options
verb = user_params_dict["verbosity"]
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
            "client_secrets.json",
            scopes=[
                "https://www.googleapis.com/auth/youtube",
                "https://www.googleapis.com/auth/youtube.force-ssl",
            ],
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
playlist_ID = user_params_dict["upload_playlist_ID"]
user_info = handle_http_errors(verb, get_user_info, youtube)
if not handle_http_errors(verb, check_playlist_id, youtube, user_info, playlist_ID):
    sys.exit()

## Dictionnary of subscribed channels names and IDs
subbed_channels_info = handle_http_errors(verb, get_subscriptions, youtube)

## Dictionnary of extra channels names and IDs
include_extra_channels = user_params_dict["include_extra_channels"]
extra_channel_handles = user_params_dict.get("extra_channel_handles")

extra_channels_info = {}
if include_extra_channels:
    for handle in extra_channel_handles:
        extra_channels_info[handle] = get_channel_info(youtube, handle)

## Merging subbed and extra channel dictionnaries
channels_info = merge_dicts([subbed_channels_info, extra_channels_info])

## Filtering on channel names
required_channel_words = user_params_dict.get("required_in_channel_name")
banned_channel_words = user_params_dict.get("banned_in_channel_name")

if required_channel_words is None and banned_channel_words is None:  # No filtering
    wanted_channels_info = channels_info

elif (
    required_channel_words is not None and banned_channel_words is None
):  # Required filtering
    wanted_channels_info = {
        k: v
        for k, v in channels_info.items()
        if any(rw in k for rw in required_channel_words)
    }

elif (
    required_channel_words is None and banned_channel_words is not None
):  # Banned filtering
    wanted_channels_info = {
        k: v
        for k, v in channels_info.items()
        if not any(bw in k for bw in banned_channel_words)
    }

else:  # Required and banned filtering
    wanted_channels_info = {
        k: v
        for k, v in channels_info.items()
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
recent_videos = {}
for ch_name, playlist_Id in wanted_channels_upload_playlists.items():
    latest_partial = handle_http_errors(verb, get_recent_videos, youtube, playlist_Id)

    if latest_partial == "ignore":
        print2(f"Channel {ch_name} has no public videos.", ["all", "func"], verb)
        continue

    recent_videos.update(
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
run_freq_dict = {"daily": 1, "weekly": 7, "monthly": 30}
today = dt.datetime.combine(dt.date.today(), dt.datetime.min.time())

run_freq = user_params_dict["run_frequency"]

if isinstance(run_freq, int):
    run_freq_dict = merge_dicts([run_freq_dict, {"custom": run_freq}])
    run_freq = "custom"

upload_date_threshold = today - dt.timedelta(days=run_freq_dict[run_freq])

for vid_ID, vid_info in recent_videos.items():
    if not (upload_date_threshold <= vid_info["upload day"] <= today):
        vid_info.update({"to add": False})

videos = {
    vid_ID: vid_info for vid_ID, vid_info in recent_videos.items() if vid_info["to add"]
}


## Additional information retrieving on the videos
split_videos = split_dict(videos, 50)

responses = {}
for sub_dict in split_videos:
    partial = handle_http_errors(verb, make_video_requests, youtube, sub_dict.keys())

    if len(responses) == 0:  # first run of the loop
        responses.update(partial)
    else:
        vid_dicts = partial["items"]
        responses["items"].extend(vid_dicts)


# Titles retrieving
titles = get_titles(response=responses)

# Duration retrieving
durations = get_durations(response=responses)

# Shorts retrieving
shorts = is_short(response=responses)

# Languages retrieving
languages = get_languages(response=responses)

# Descriptions retrieving
descriptions = get_descriptions(response=responses)

# Tags retrieving
tags = get_tags(response=responses)

# Dimensions retrieving
dimensions = get_dimensions(response=responses)

# Definitions retrieving
definitions = get_definitions(response=responses)

# Resolutions retrieving (does not use YT API)
lowest_resolution = user_params_dict.get("lowest_resolution")
if lowest_resolution is not None:
    resolutions = get_resolutions(video_IDs=responses.keys())

# Framerates retrieving (does not use YT API)
lowest_framerate = user_params_dict.get("lowest_framerate")
if lowest_framerate is not None:
    framerates = get_framerates(video_IDs=responses.keys())

## Caption information retrieving
need_captions = user_params_dict["require_captions"]
if need_captions:
    captions_responses = handle_http_errors(
        verb, make_caption_requests, youtube, videos.keys()
    )

    captions = get_captions(response=captions_responses)


## Videos' information updating
for index, (vid_ID, vid_info) in enumerate(videos.items()):
    # Title
    vid_info.update({"title": titles[index]})
    vid_info.update({"original title": titles[index]})

    # Duration
    vid_info.update({"duration": durations[index]})

    # Short
    vid_info.update({"is short": shorts[index]})

    # Language
    vid_info.update({"language": languages[index]})

    # Descriptions
    vid_info.update({"description": descriptions[index]})

    # Tags
    vid_info.update({"tags": tags[index]})

    # Definitions
    vid_info.update({"definition": definitions[index]})

    # Dimensions
    vid_info.update({"dimension": dimensions[index]})

    # Resolutions
    if lowest_resolution is not None:
        vid_info.update({"resolutions": resolutions[index]})

    # Framerates
    if lowest_framerate is not None:
        vid_info.update({"framerates": framerates[index]})

    # Captions
    if need_captions:
        vid_info.update({"captions": captions[vid_ID]})

## Title preparing
no_emojis = user_params_dict.get("ignore_title_emojis")
no_punctuation = user_params_dict.get("ignore_title_punctuation")
no_case = user_params_dict.get("ignore_title_case")
required_title_words = user_params_dict.get("required_in_title")
banned_title_words = user_params_dict.get("banned_in_title")

if no_emojis:
    for vid_info in videos.values():
        vid_info["title"] = strip_emojis(vid_info["title"])
    if required_title_words is not None:
        required_title_words = [strip_emojis(word) for word in required_title_words]
    if banned_title_words is not None:
        banned_title_words = [strip_emojis(word) for word in banned_title_words]

if no_punctuation:
    for vid_info in videos.values():
        vid_info["title"] = strip_punctuation(vid_info["title"])
    if required_title_words is not None:
        required_title_words = [
            strip_punctuation(word) for word in required_title_words
        ]
    if banned_title_words is not None:
        banned_title_words = [strip_punctuation(word) for word in banned_title_words]

if no_case:
    for vid_info in videos.values():
        vid_info["title"] = make_lowercase(vid_info["title"])
    if required_title_words is not None:
        required_title_words = [make_lowercase(word) for word in required_title_words]
    if banned_title_words is not None:
        banned_title_words = [make_lowercase(word) for word in banned_title_words]


## Additional information filtering
min_max_durations = user_params_dict.get("allowed_durations")

preferred_languages = user_params_dict.get("preferred_languages")

required_in_description = user_params_dict.get("required_in_description")
banned_in_description = user_params_dict.get("banned_in_description")

required_tags = user_params_dict.get("required_tags")
banned_tags = user_params_dict.get("banned_tags")

lowest_definition = user_params_dict.get("lowest_definition")
preferred_dimensions = user_params_dict.get("preferred_dimensions")

# Title filtering
if required_title_words is None and banned_title_words is None:  # No filtering
    pass

elif (
    required_title_words is not None and banned_title_words is None
):  # Required filtering
    for vid_ID, vid_info in videos.items():
        if vid_info["to add"] is False:
            continue
        elif any(rw in vid_info["title"] for rw in required_title_words):
            continue
        else:
            vid_info.update({"to add": False})

elif (
    required_title_words is None and banned_title_words is not None
):  # Banned filtering
    for vid_ID, vid_info in videos.items():
        if vid_info["to add"] is False:
            continue
        elif not any(bw in vid_info["title"] for bw in banned_title_words):
            continue
        else:
            vid_info.update({"to add": False})

else:  # Required and banned filtering
    for vid_ID, vid_info in videos.items():
        if vid_info["to add"] is False:
            continue
        elif any(rw in vid_info["title"] for rw in required_title_words) and not any(
            bw in vid_info["title"] for bw in banned_title_words
        ):
            continue
        else:
            vid_info.update({"to add": False})

# Duration filtering
if min_max_durations is not None:
    for vid_info in videos.values():
        if vid_info["to add"] is False:
            continue
        elif (
            min_max_durations[0] * 60.0
            <= vid_info["duration"]
            <= min_max_durations[-1] * 60.0
        ):
            pass
        else:
            vid_info.update({"to add": False})

# Short filtering
if user_params_dict["keep_shorts"] is False:
    for vid_ID, vid_info in videos.items():
        if vid_info["to add"] is False:
            continue
        elif vid_info["is short"]:
            vid_info.update({"to add": False})

# Duplicates filtering
if user_params_dict["keep_duplicates"] is False:
    old_vid_IDs = get_playlist_content(youtube, playlist_ID)
    new_vid_IDs = [
        vid_ID for (vid_ID, vid_info) in videos.items() if vid_info["to add"]
    ]

    for vid_ID in old_vid_IDs:
        if vid_ID in new_vid_IDs:
            videos[vid_ID].update({"to add": False})

# Language filtering
if preferred_languages is not None:
    preferred_languages.append("unknown")
    for vid_ID, vid_info in videos.items():
        if vid_info["to add"] is False:
            continue
        else:
            if vid_info["language"] not in preferred_languages:
                vid_info.update({"to add": False})

# Quality filtering
if lowest_definition is not None:
    for vid_ID, vid_info in videos.items():
        if vid_info["to add"] is False:
            continue
        else:
            if (
                vid_info["definition"] != lowest_definition.lower()
                and lowest_definition == "HD"
            ):
                vid_info.update({"to add": False})

if preferred_dimensions is not None:
    for vid_ID, vid_info in videos.items():
        if vid_info["to add"] is False:
            continue
        else:
            if vid_info["dimension"].upper() not in preferred_dimensions:
                vid_info.update({"to add": False})

if lowest_resolution is not None:
    for vid_ID, vid_info in videos.items():
        if vid_info["to add"] is False:
            continue
        else:
            if sorted(vid_info["resolutions"])[-1] >= int(
                lowest_resolution.split("p")[0]
            ):
                vid_info.update({"to add": False})

if lowest_framerate is not None:
    for vid_ID, vid_info in videos.items():
        if vid_info["to add"] is False:
            continue
        else:
            if sorted(vid_info["framerates"])[-1] >= lowest_framerate:
                vid_info.update({"to add": False})

# Description filtering
if required_in_description is None and banned_in_description is None:  # No filtering
    pass

elif (
    required_in_description is not None and banned_in_description is None
):  # Required filtering
    for vid_ID, vid_info in videos.items():
        if vid_info["to add"] is False or vid_info["description"] is None:
            continue
        elif any(rw in vid_info["description"] for rw in required_in_description):
            continue
        else:
            vid_info.update({"to add": False})

elif (
    required_in_description is None and banned_in_description is not None
):  # Banned filtering
    for vid_ID, vid_info in videos.items():
        if vid_info["to add"] is False or vid_info["description"] is None:
            continue
        elif not any(bw in vid_info["description"] for bw in banned_in_description):
            continue
        else:
            vid_info.update({"to add": False})

else:  # Required and banned filtering
    for vid_ID, vid_info in videos.items():
        if vid_info["to add"] is False or vid_info["description"] is None:
            continue
        elif any(
            rw in vid_info["description"] for rw in required_in_description
        ) and not any(bw in vid_info["description"] for bw in banned_in_description):
            continue
        else:
            vid_info.update({"to add": False})

# Tags filtering
if required_tags is None and banned_tags is None:  # No filtering
    pass

elif required_tags is not None and banned_tags is None:  # Required filtering
    for vid_ID, vid_info in videos.items():
        if vid_info["to add"] is False or vid_info["tags"] is None:
            continue
        elif any(rw in vid_info["tags"] for rw in required_tags):
            continue
        else:
            vid_info.update({"to add": False})

elif required_tags is None and banned_tags is not None:  # Banned filtering
    for vid_ID, vid_info in videos.items():
        if vid_info["to add"] is False or vid_info["tags"] is None:
            continue
        elif not any(bw in vid_info["tags"] for bw in banned_tags):
            continue
        else:
            vid_info.update({"to add": False})

else:  # Required and banned filtering
    for vid_ID, vid_info in videos.items():
        if vid_info["to add"] is False or vid_info["tags"] is None:
            continue
        elif any(rw in vid_info["tags"] for rw in required_tags) and not any(
            bw in vid_info["tags"] for bw in banned_tags
        ):
            continue
        else:
            vid_info.update({"to add": False})

# Captions filtering
if need_captions:
    captions_options = user_params_dict.get("caption_options")
    for vid_ID, vid_info in videos.items():
        if vid_info["to add"] is False:
            continue

        captions = vid_info["captions"].values()

        # Check that at least one caption is good
        if not any(
            all(
                (
                    caption["trackKind"] in captions_options.get("trackKind"),
                    caption["language"] in captions_options.get("languages"),
                    caption["audioTrackType"] in captions_options.get("audioTrackType"),
                    caption["status"] in captions_options.get("status"),
                    caption["isCC"] == captions_options.get("isCC"),
                    caption["isLarge"] == captions_options.get("isLarge"),
                    caption["isEasyReader"] == captions_options.get("isEasyReader"),
                    caption["isAutoSynced"] == captions_options.get("isAutoSynced"),
                )
            )
            for caption in captions
        ):
            vid_info.update({"to add": False})

## Selecting correct videos
videos_to_add = {
    vid_ID: vid_info for vid_ID, vid_info in videos.items() if vid_info["to add"]
}

## Adding selected videos to a playlist
if videos_to_add is not None:  # Checks if there's actually videos to add
    print2(f"Number of videos added: {len(videos_to_add)}", ["all", "videos"], verb)
    for vid_ID, vid_info in videos_to_add.items():
        handle_http_errors(verb, add_to_playlist, youtube, playlist_ID, vid_ID)

        print2(
            f"From {vid_info['channel name']}, the video named: {vid_info['original title']} has been added.",
            ["all", "videos"],
            verb,
        )
else:
    print2("No videos from yesterday to add.", ["all", "videos"], verb)
