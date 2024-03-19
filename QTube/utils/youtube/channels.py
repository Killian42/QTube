def get_subscriptions(youtube, next_page_token=None) -> dict:
    """Retrieves the subscriptions of the logged user.

    Args:
        youtube (Resource): YT API resource.
        next_page_token (str): Token of the subscription page (optional).

    Returns:
        channels (dict): Dictionary of channel names (keys) and channel IDs (values).
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


def get_channel_info(youtube, handle: str):
    """Retrieves basic information about a YT channel.

    Args:
        youtube (Resource): YT API resource.
        handle (str): Handle of the YT channel.

    Returns:
        response (dict): Dictionary containing basic information on the requested YT channel.
    """
    channel = {}

    response = youtube.channels().list(part="snippet", forHandle=handle).execute()

    if "items" in response.keys():
        title = response["items"][0]["snippet"]["title"]
        channel_id = response["items"][0]["id"]
        channel[title] = channel_id
    else:
        print(
            f"Could not find a YT channel associated with the following handle: {handle}."
        )

    return channel


def get_uploads_playlists(youtube, channel_IDs: list[str]) -> list[str]:
    """Retrieves the upload playlists of YT channels.

    Args:
        youtube (Resource): YT API ressource.
        channel_IDs (list[str]): Channel IDs of YT channels.

    Returns:
        upload_pl_ids (list[str]): IDs of the uploads playlist of the YT channels.
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


def get_user_info(youtube) -> dict:
    """Retrieves information about the logged-in user channel.

    Args:
        youtube (Resource): YT API resource.

    Returns:
        response (dict): Dictionary containing information on the logged-in user channel.
    """
    response = (
        youtube.channels()
        .list(part="snippet,contentDetails,statistics", mine=True)
        .execute()
    )

    return response
