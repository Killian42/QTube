import datetime as dt


def get_recent_videos(youtube, playlist_ID: str) -> dict:
    """Retrieves the last 5 videos of a YT playlist.

    Args:
        youtube (Resource): YT API resource.
        playlist_ID (str): ID of the playlist.

    Returns:
        recent_vids (dict): Dictionary containing the ID (keys) and upload date (values) of the last 5 videos in the playlist.
    """
    response = (
        youtube.playlistItems()
        .list(part="contentDetails", playlistId=playlist_ID, maxResults=5)
        .execute(num_retries=5)
    )

    recent_vids = {
        item["contentDetails"]["videoId"]: {
            "upload datetime": dt.datetime.fromisoformat(
                item["contentDetails"]["videoPublishedAt"]
            )
        }
        for item in response.get("items", [])
    }

    return recent_vids


def get_playlist_content(youtube, playlist_ID: str) -> list[str]:
    """Retrieves the IDs of videos saved in a YT playlist.

    Args:
        youtube (Resource): YT API resource.
        playlist_ID (str): ID of the playlist.

    Returns:
        videos_IDs (list[str]): List containing the IDs of the videos saved in the playlist.
    """
    next_page_token = None
    videos_IDs = []
    while True:
        response = (
            youtube.playlistItems()
            .list(
                part="contentDetails",
                playlistId=playlist_ID,
                maxResults=50,
                pageToken=next_page_token,
            )
            .execute(num_retries=5)
        )

        temp_videos_IDs = [
            item["contentDetails"]["videoId"] for item in response.get("items")
        ]
        videos_IDs.extend(temp_videos_IDs)

        next_page_token = response.get("nextPageToken")

        if not next_page_token:
            break

    return videos_IDs


def get_playlists_titles(youtube=None, playlist_IDs: list[str] = None):
    """Retrieves the titles of a list of YT playlists.

    Args:
        youtube (Resource): YT API resource.
        playlists_IDs (list[str]): List of playlist IDs.

    Returns:
        titles (list[str]): List of YT playlist titles.
    """
    playlist_IDs_str = ",".join(playlist_IDs)
    response = (
        youtube.playlists()
        .list(part="snippet", id=playlist_IDs_str)
        .execute(num_retries=5)
    )

    titles = [playlist["snippet"]["title"] for playlist in response["items"]]

    return titles


def add_to_playlist(youtube, playlist_ID: str, video_ID: str) -> None:
    """Adds a  YT video to the YT playlist.

    Args:
        youtube (Resource): YT API resource.
        playlist_ID (str): Playlist ID.
        video_ID (str): Video ID.

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
                    "resourceId": {"kind": "youtube#video", "videoId": video_ID},
                }
            },
        )
        .execute(num_retries=5)
    )
    return
