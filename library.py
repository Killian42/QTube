### Functions ###
# Returns tokens of the subscription pages#
def get_tokens(youtube):
    """
    Retrieves the tokens of the subscription pages of the logged user.

    Inputs:
    param youtube: Youtube API ressource

    Returns:
    tokens: List of the tokens of the subscription pages of the logged user, type=list
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


# Returns the dictionnary containing all subscribed channels' name and ID from logged user#
def get_youtube_subscriptions(youtube, next_page_token):
    """
    Retrieves the subscriptions of the logged user

    Inputs:
    param youtube: Youtube API ressource
    next_page_token: Token of the subscription page, type=str

    Returns:
    channels: Dictionnary of channel names (keys) and channel IDs (values), type=dict
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


# Returns the upload playlist of a YT channel#
def get_uploads_playlists(youtube, channel_Id):
    """
    Retrieves the upload playlist of a YT channel

    Inputs:
    param youtube: Youtube API ressource
    channel_Id: Channel ID of a YT channel, type=str

    Returns:
    upload_pl_id: ID of the uploads playlist of the YT channel
    """
    response = (
        youtube.channels()
        .list(part="contentDetails", id=channel_Id, maxResults=50)
        .execute()
    )
    upload_pl_id = response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    return upload_pl_id


# Returns the last 5 videos IDs and upload date of a playlist#
def get_recent_videos(youtube, playlist_Id):
    """
    Retrieves the last 5 videos of a YT playlist

    Inputs:
    param youtube: Youtube API ressource
    playlist_Id: ID of the playlist, type=str

    Returns:
    recent_vids: Dictionnary containing the ID (key) and upload date (values) of the last 5 videos in the playlist, type=dict
    """
    response = (
        youtube.playlistItems()
        .list(part="contentDetails", playlistId=playlist_Id)
        .execute()
    )
    recent_vids = {}
    nb_vids = len(response["items"])

    for i in range(nb_vids):
        date = response["items"][i]["contentDetails"]["videoPublishedAt"].split("T")[0]
        vid_id = response["items"][i]["contentDetails"]["videoId"]
        temp = {vid_id:{"upload day":date}}

        recent_vids.update(temp)
    return recent_vids


# Adds a video to a playlist#
def add_to_playlist(youtube, playlist_Id, video_Id):
    """
    Adds a  YT video to the YT playlist

    Inputs:
    param youtube: Youtube API ressource
    playlist_Id: ID of the playlist, type=str
    video_Id: ID of the video, type=str

    Returns:
    Nothing
    """
    response = (
        youtube.playlistItems()
        .insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": playlist_Id,
                    # "position": 0,
                    "resourceId": {"kind": "youtube#video", "videoId": video_Id},
                }
            },
        )
        .execute()
    )
    return


# Returns the title of a video#
def get_title(youtube, video_Id):
    """
    Retrieves the title of a YT video

    Inputs:
    param youtube: Youtube API ressource
    video_Id: ID of the video, type=str

    Returns:
    title: Title of the YT video, type=str
    """
    response = youtube.videos().list(part="snippet", id=video_Id).execute()
    title = response["items"][0]["snippet"]["title"]
    return title


# Returns the tags of a video#
def get_tags(youtube, video_Id):
    """
    Retrieves the tags of a YT video

    Inputs:
    param youtube: Youtube API ressource
    video_Id: ID of the video, type=str

    Returns:
    title: Tags of the YT video, type=lst
    """
    response = youtube.videos().list(part="snippet", id=video_Id).execute()
    tags = response["items"][0]["snippet"]["tags"]
    return tags


# Returns the description of a video#
def get_description(youtube, video_Id):
    """
    Retrieves the description of a YT video

    Inputs:
    param youtube: Youtube API ressource
    video_Id: ID of the video, type=str

    Returns:
    title: Description of the YT video, type=str
    """
    response = youtube.videos().list(part="snippet", id=video_Id).execute()
    description = response["items"][0]["snippet"]["description"]
    return description