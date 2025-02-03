### Imports
## Standard library modules
import datetime as dt
import json
import os
import pickle
import sys

## Third party librairies
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

## Local modules
import QTube.utils.checks
import QTube.utils.helpers
import QTube.utils.parsing
import QTube.utils.youtube.captions
import QTube.utils.youtube.channels
import QTube.utils.youtube.playlists
import QTube.utils.youtube.videos


def main():
    """Checks Youtube for new videos and add a selection of these videos to a playlist, based on user defined parameters."""
    ### User parameters loading
    ## JSON parameters file opening
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

    ## Command line arguments
    override_json = user_params_dict["override_json"]
    if override_json:
        args = QTube.utils.parsing.parse_arguments()
        formatted_args = QTube.utils.parsing.format_arguments(args)

        # Rewrites JSON file parameters if options are provided in the terminal
        for k, v in formatted_args.items():
            if v is not None:
                user_params_dict[k] = v

    ## Parameters checking
    if QTube.utils.checks.check_user_params(user_params_dict) is not True:
        print(
            "User defined parameters are not correctly formatted. Check the template and retry."
        )
        sys.exit()

    ## Verbosity and fancy text options loading
    fancy = user_params_dict["fancy_mode"]
    verb = user_params_dict["verbosity"]

    ### Software version checking
    version, latest_release = QTube.utils.checks.check_version()
    latest_url = "https://github.com/Killian42/QTube/releases/latest"

    QTube.utils.helpers.print2(
        f"QTube v{version}\n", fancy, "info", ["internal"], ["internal"]
    )

    if latest_release is None:
        QTube.utils.helpers.print2(
            "Failed to check the latest release version:\n",
            fancy,
            "fail",
            ["internal"],
            ["internal"],
        )
    else:
        comp = QTube.utils.checks.compare_software_versions(version, latest_release)
        if comp == "same":
            QTube.utils.helpers.print2(
                f"The latest stable version of the software, v{version}, is currently runnning.\n",
                fancy,
                "success",
                ["internal"],
                ["internal"],
            )
        elif comp == "older":
            QTube.utils.helpers.print2(
                f"You are currently running version v{version}.\nConsider upgrading to the latest stable release (v{latest_release}) at {latest_url}.\n",
                fancy,
                "warning",
                ["internal"],
                ["internal"],
            )
        elif comp == "newer":
            QTube.utils.helpers.print2(
                f"You are currently running version {version}.\nThis version is not a stable release. Consider installing the latest stable release ({latest_release}) at {latest_url}.\n",
                fancy,
                "warning",
                ["internal"],
                ["internal"],
            )
        elif comp == "pre-release":
            QTube.utils.helpers.print2(
                f"You are currently running version v{version}.\nThis is a pre-release version. Consider installing the latest stable release (v{latest_release}) at {latest_url}.\n",
                fancy,
                "warning",
                ["internal"],
                ["internal"],
            )

    ## Verbosity and fancy text options displaying
    if fancy:
        QTube.utils.helpers.print2(
            f"The fancy text option is enabled.",
            fancy,
            "info",
            ["internal"],
            ["internal"],
        )
    else:
        QTube.utils.helpers.print2(
            f"The fancy text option is disabled.",
            fancy,
            "info",
            ["internal"],
            ["internal"],
        )
    QTube.utils.helpers.print2(
        f"The following verbosity options are enabled: {', '.join(verb)}.\n",
        fancy,
        "info",
        ["internal"],
        ["internal"],
    )

    ### Youtube API login
    credentials = None

    ## token.pickle stores the user's credentials from previously successful logins
    if os.path.exists("token.pickle"):
        QTube.utils.helpers.print2(
            "Loading credentials from pickle file...",
            fancy,
            "info",
            ["all", "credentials"],
            verb,
        )

        with open("token.pickle", "rb") as token:
            credentials = pickle.load(token)

            QTube.utils.helpers.print2(
                "Credentials loaded from pickle file",
                fancy,
                "success",
                ["all", "credentials"],
                verb,
            )

    ## If there are no valid credentials available, then either refresh the token or log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            QTube.utils.helpers.print2(
                "Refreshing access token...",
                fancy,
                "info",
                ["all", "credentials"],
                verb,
            )

            credentials.refresh(Request())
            QTube.utils.helpers.print2(
                "Access token refreshed\n",
                fancy,
                "success",
                ["all", "credentials"],
                verb,
            )
        else:
            QTube.utils.helpers.print2(
                "Fetching New Tokens...", fancy, "info", ["all", "credentials"], verb
            )
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

            QTube.utils.helpers.print2(
                "New token fetched\n", fancy, "success", ["all", "credentials"], verb
            )

            # Save the credentials for the next run
            with open("token.pickle", "wb") as f:
                QTube.utils.helpers.print2(
                    "Saving Credentials for Future Use...",
                    fancy,
                    "info",
                    ["all", "credentials"],
                    verb,
                )

                pickle.dump(credentials, f)
                QTube.utils.helpers.print2(
                    "Credentials saved\n",
                    fancy,
                    "success",
                    ["all", "credentials"],
                    verb,
                )

    ### Building API resource
    youtube = build("youtube", "v3", credentials=credentials)

    ### Code

    ## Checking the playlist ID
    playlist_ID = user_params_dict["upload_playlist_ID"]
    user_info = QTube.utils.helpers.handle_http_errors(
        verb, fancy, QTube.utils.youtube.channels.get_user_info, youtube
    )
    if not QTube.utils.helpers.handle_http_errors(
        verb,
        fancy,
        QTube.utils.checks.check_playlist_id,
        youtube,
        user_info,
        playlist_ID,
    ):
        sys.exit()

    ## Dictionnary of subscribed channels names and IDs
    subbed_channels_info = QTube.utils.helpers.handle_http_errors(
        verb, fancy, QTube.utils.youtube.channels.get_subscriptions, youtube
    )

    ## Dictionnary of extra channels names and IDs
    include_extra_channels = user_params_dict["include_extra_channels"]
    extra_channel_handles = user_params_dict.get("extra_channel_handles")

    extra_channels_info = {}
    if include_extra_channels:
        for handle in extra_channel_handles:
            extra_channels_info[handle] = QTube.utils.channels.get_channel_info(
                youtube, handle
            )

    ## Merging subbed and extra channel dictionnaries
    channels_info = QTube.utils.helpers.merge_dicts(
        [subbed_channels_info, extra_channels_info]
    )

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
    split_channels = QTube.utils.helpers.split_dict(wanted_channels_info, 50)

    wanted_channels_upload_playlists = {}
    for sub_dict in split_channels:
        partial = QTube.utils.helpers.handle_http_errors(
            verb,
            fancy,
            QTube.utils.youtube.channels.get_uploads_playlists,
            youtube,
            list(sub_dict.values()),
        )
        partial_dict = dict(zip(list(sub_dict.keys()), partial))
        wanted_channels_upload_playlists.update(partial_dict)

    ## Dictionnary of the latest videos from selected channels
    recent_videos = {}
    for ch_name, playlist_Id in wanted_channels_upload_playlists.items():
        latest_partial = QTube.utils.helpers.handle_http_errors(
            verb,
            fancy,
            QTube.utils.youtube.playlists.get_recent_videos,
            youtube,
            playlist_Id,
        )

        if latest_partial == "ignore":
            QTube.utils.helpers.print2(
                f"Channel {ch_name} has no public videos.",
                fancy,
                "warning",
                ["all", "func"],
                verb,
            )
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

    ## Upload datetime and filtering
    run_freq_dict = {"daily": 1, "weekly": 7, "monthly": 30}
    today = dt.datetime.now(dt.timezone.utc)

    run_freq = user_params_dict["run_frequency"]

    if isinstance(run_freq, int):
        run_freq_dict = QTube.utils.helpers.merge_dicts(
            [run_freq_dict, {"custom": run_freq}]
        )
        run_freq = "custom"

    upload_date_threshold = today - dt.timedelta(days=run_freq_dict[run_freq])

    for vid_ID, vid_info in recent_videos.items():
        if not (upload_date_threshold <= vid_info["upload datetime"] <= today):
            vid_info.update({"to add": False})

    videos = {
        vid_ID: vid_info
        for vid_ID, vid_info in recent_videos.items()
        if vid_info["to add"]
    }

    ## Additional information retrieving on the videos
    split_videos = QTube.utils.helpers.split_dict(videos, 50)

    responses = {}
    for sub_dict in split_videos:
        partial = QTube.utils.helpers.handle_http_errors(
            verb,
            fancy,
            QTube.utils.youtube.videos.make_video_requests,
            youtube,
            sub_dict.keys(),
        )

        if len(responses) == 0:  # first run of the loop
            responses.update(partial)
        else:
            vid_dicts = partial["items"]
            responses["items"].extend(vid_dicts)

    video_IDs_lst = [vid["id"] for vid in responses["items"]]

    # Titles retrieving
    titles = QTube.utils.youtube.videos.get_titles(response=responses)

    # Duration retrieving
    durations = QTube.utils.youtube.videos.get_durations(response=responses)

    # Shorts retrieving
    shorts = QTube.utils.youtube.videos.is_short(
        response=responses, video_IDs=video_IDs_lst
    )

    # Languages retrieving
    languages = QTube.utils.youtube.videos.get_languages(response=responses)

    # Descriptions retrieving
    descriptions = QTube.utils.youtube.videos.get_descriptions(response=responses)

    # Tags retrieving
    tags = QTube.utils.youtube.videos.get_tags(response=responses)

    # Dimensions retrieving
    dimensions = QTube.utils.youtube.videos.get_dimensions(response=responses)

    # Definitions retrieving
    definitions = QTube.utils.youtube.videos.get_definitions(response=responses)

    # Live status retrieving
    live_statuses = QTube.utils.youtube.videos.is_live(response=responses)

    # View counts retrieving
    view_counts = QTube.utils.youtube.videos.get_view_counts(response=responses)

    # Like counts retrieving
    like_counts = QTube.utils.youtube.videos.get_like_counts(response=responses)

    # Comment counts retrieving
    comment_counts = QTube.utils.youtube.videos.get_comment_counts(response=responses)

    # Likes/views ratio retrieving
    likes_to_views_ratio = QTube.utils.youtube.videos.get_likes_to_views_ratio(
        like_counts, view_counts
    )

    # Comments/views ratio retrieving
    comments_to_views_ratio = QTube.utils.youtube.videos.get_likes_to_views_ratio(
        comment_counts, view_counts
    )

    # Paid promotions retrieving
    paid_advertising = QTube.utils.youtube.videos.has_paid_advertising(
        response=responses
    )

    # Made for Kids retrieving
    made_for_kids = QTube.utils.youtube.videos.is_made_for_kids(response=responses)

    # Resolutions retrieving (does not use YT API)
    lowest_resolution = user_params_dict.get("lowest_resolution")
    if lowest_resolution is not None:
        resolutions = QTube.utils.youtube.videos.get_resolutions(
            video_IDs=responses.keys()
        )

    # Framerates retrieving (does not use YT API)
    lowest_framerate = user_params_dict.get("lowest_framerate")
    if lowest_framerate is not None:
        framerates = QTube.utils.youtube.videos.get_framerates(
            video_IDs=responses.keys()
        )

    ## Caption information retrieving
    need_captions = user_params_dict["require_captions"]
    if need_captions:
        captions_responses = QTube.utils.helpers.handle_http_errors(
            verb,
            fancy,
            QTube.utils.youtube.captions.make_caption_requests,
            youtube,
            videos.keys(),
        )

        captions = QTube.utils.youtube.captions.get_captions(
            response=captions_responses
        )

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

        # Live statuses
        vid_info.update({"live status": live_statuses[index]})

        # Views
        vid_info.update({"views": view_counts[index]})

        # Likes
        vid_info.update({"likes": like_counts[index]})

        # Comments
        vid_info.update({"comments": comment_counts[index]})

        # Likes/views
        vid_info.update({"likes_to_views_ratio": likes_to_views_ratio[index]})

        # Comments/views
        vid_info.update({"comments_to_views_ratio": comments_to_views_ratio[index]})

        # Paid promotions
        vid_info.update({"has_paid_ad": paid_advertising[index]})

        # Made for kids
        vid_info.update({"made_for_kids": made_for_kids[index]})

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
            vid_info["title"] = QTube.utils.helpers.strip_emojis(vid_info["title"])
        if required_title_words is not None:
            required_title_words = [
                QTube.utils.helpers.strip_emojis(word) for word in required_title_words
            ]
        if banned_title_words is not None:
            banned_title_words = [
                QTube.utils.helpers.strip_emojis(word) for word in banned_title_words
            ]

    if no_punctuation:
        for vid_info in videos.values():
            vid_info["title"] = QTube.utils.helpers.strip_punctuation(vid_info["title"])
        if required_title_words is not None:
            required_title_words = [
                QTube.utils.helpers.strip_punctuation(word)
                for word in required_title_words
            ]
        if banned_title_words is not None:
            banned_title_words = [
                QTube.utils.helpers.strip_punctuation(word)
                for word in banned_title_words
            ]

    if no_case:
        for vid_info in videos.values():
            vid_info["title"] = QTube.utils.helpers.make_lowercase(vid_info["title"])
        if required_title_words is not None:
            required_title_words = [
                QTube.utils.helpers.make_lowercase(word)
                for word in required_title_words
            ]
        if banned_title_words is not None:
            banned_title_words = [
                QTube.utils.helpers.make_lowercase(word) for word in banned_title_words
            ]

    ## Additional information filtering
    min_max_durations = user_params_dict.get("allowed_durations")
    ignore_livestreams = user_params_dict.get("ignore_livestreams")
    ignore_premieres = user_params_dict.get("ignore_premieres")

    preferred_languages = user_params_dict.get("preferred_languages")

    required_in_description = user_params_dict.get("required_in_description")
    banned_in_description = user_params_dict.get("banned_in_description")

    required_tags = user_params_dict.get("required_tags")
    banned_tags = user_params_dict.get("banned_tags")

    lowest_definition = user_params_dict.get("lowest_definition")
    preferred_dimensions = user_params_dict.get("preferred_dimensions")

    views_threshold = user_params_dict.get("views_threshold")
    likes_threshold = user_params_dict.get("likes_threshold")
    comments_threshold = user_params_dict.get("comments_threshold")
    likes_to_views_ratio_threshold = user_params_dict.get("likes_to_views_ratio")
    comments_to_views_ratio_threshold = user_params_dict.get("comments_to_views_ratio")

    # Duration filtering
    if min_max_durations is not None:
        for vid_info in videos.values():
            if vid_info["to add"] is False:
                continue
            elif vid_info["live status"] == "live" and ignore_livestreams is False:
                vid_info.update({"to add": True})
            elif vid_info["live status"] == "upcoming" and ignore_premieres is False:
                vid_info.update({"to add": True})
            elif vid_info["duration"] == 3.141593:
                vid_info.update({"to add": False})
            elif (
                min_max_durations[0] * 60.0
                <= vid_info["duration"]
                <= min_max_durations[-1] * 60.0
            ):
                pass
            else:
                vid_info.update({"to add": False})

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
            elif any(
                rw in vid_info["title"] for rw in required_title_words
            ) and not any(bw in vid_info["title"] for bw in banned_title_words):
                continue
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
        old_vid_IDs = QTube.utils.youtube.playlists.get_playlist_content(
            youtube, playlist_ID
        )
        new_vid_IDs = [
            vid_ID for (vid_ID, vid_info) in videos.items() if vid_info["to add"]
        ]

        for vid_ID in old_vid_IDs:
            if vid_ID in new_vid_IDs:
                videos[vid_ID].update({"to add": False})

    # Paid advertisement filtering
    if user_params_dict["allow_paid_promotions"] is False:
        for vid_ID, vid_info in videos.items():
            if vid_info["to add"] is False:
                continue
            elif vid_info["has_paid_ad"]:
                vid_info.update({"to add": False})

    # Made for kids filtering
    if user_params_dict["only_made_for_kids"] is True:
        for vid_ID, vid_info in videos.items():
            if vid_info["to add"] is False:
                continue
            elif not vid_info["made_for_kids"]:
                vid_info.update({"to add": False})

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
    if (
        required_in_description is None and banned_in_description is None
    ):  # No filtering
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
            ) and not any(
                bw in vid_info["description"] for bw in banned_in_description
            ):
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
                        caption["audioTrackType"]
                        in captions_options.get("audioTrackType"),
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

    # Views filtering
    if views_threshold > 0:
        for vid_ID, vid_info in videos.items():
            if vid_info["to add"] and vid_info["views"] < views_threshold:
                vid_info.update({"to add": False})

    # Likes Filtering
    if likes_threshold > 0:
        for vid_ID, vid_info in videos.items():
            if vid_info["to add"] and vid_info["likes"] < likes_threshold:
                vid_info.update({"to add": False})

    # Comments filtering
    if comments_threshold > 0:
        for vid_ID, vid_info in videos.items():
            if vid_info["to add"] and vid_info["comments"] < comments_threshold:
                vid_info.update({"to add": False})

    # Likes/views ratio filtering
    if likes_to_views_ratio_threshold > 0:
        for vid_ID, vid_info in videos.items():
            if (
                vid_info["to add"]
                and vid_info["likes_to_views_ratio"] < likes_to_views_ratio_threshold
            ):
                vid_info.update({"to add": False})

    # Comments/views ratio filtering
    if comments_to_views_ratio_threshold > 0:
        for vid_ID, vid_info in videos.items():
            if (
                vid_info["to add"]
                and vid_info["comments_to_views_ratio"]
                < comments_to_views_ratio_threshold
            ):
                vid_info.update({"to add": False})

    ## Selecting correct videos
    videos_to_add = {
        vid_ID: vid_info for vid_ID, vid_info in videos.items() if vid_info["to add"]
    }

    ## Adding selected videos to a playlist
    playlist_title = QTube.utils.youtube.playlists.get_playlists_titles(
        youtube, [playlist_ID]
    )[0]
    playlist_video_count = QTube.utils.youtube.playlists.get_playlists_video_counts(
        youtube, [playlist_ID]
    )[0]

    if len(videos_to_add) != 0:  # Checks if there are actually videos to add
        if (
            playlist_video_count + len(videos_to_add) > 5000
        ):  # Checks if current video count + new videos would exceed 5k (YT playlist size limit)
            QTube.utils.helpers.print2(
                f"The {playlist_title} playlist would reach or exceed the 5000 size limit if the following videos were added to it:",
                fancy,
                "fail",
                ["all", "videos"],
                verb,
            )
            for vid_ID, vid_info in videos_to_add.items():
                QTube.utils.helpers.print2(
                    f"From {vid_info['channel name']}, the video named: {vid_info['original title']} would have been added.\n It is available at: https://www.youtube.com/watch?v={vid_ID}",
                    fancy,
                    "video",
                    ["all", "videos"],
                    verb,
                )
            QTube.utils.helpers.print2(
                f"Remove at least {len(videos_to_add)} videos from the {playlist_title} playlist so that the new one(s) can be added.",
                fancy,
                "warning",
                ["all", "videos"],
                verb,
            )
        else:
            QTube.utils.helpers.print2(
                f"The following videos will be added to the {playlist_title} playlist:",
                fancy,
                "info",
                ["all", "videos"],
                verb,
            )
            for vid_ID, vid_info in videos_to_add.items():
                QTube.utils.helpers.handle_http_errors(
                    verb,
                    fancy,
                    QTube.utils.youtube.playlists.add_to_playlist,
                    youtube,
                    playlist_ID,
                    vid_ID,
                )

                QTube.utils.helpers.print2(
                    f"From {vid_info['channel name']}, the video named: {vid_info['original title']} has been added.",
                    fancy,
                    "video",
                    ["all", "videos"],
                    verb,
                )
    else:
        QTube.utils.helpers.print2(
            f"No new videos to add to the {playlist_title} playlist.",
            fancy,
            "info",
            ["all", "videos"],
            verb,
        )


if __name__ == "__main__":
    main()
