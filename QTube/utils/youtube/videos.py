import isodate

from pytube import YouTube

from QTube.utils import helpers


def make_video_requests(youtube, video_IDs: list[str]) -> dict:
    """Retrieves information on a list of YT videos.

    Args:
        youtube (Resource): YT API resource.
        video_IDs (list[str]): List of video IDs.

    Returns:
        response (dict[dict]): YT API response.
    """
    video_IDs_str = ",".join(video_IDs)
    response = (
        youtube.videos()
        .list(part="snippet,contentDetails,statistics", id=video_IDs_str)
        .execute(num_retries=5)
    )
    return response


def get_titles(
    youtube=None,
    response: dict = None,
    video_IDs: list[str] = None,
    use_API: bool = False,
) -> list[str]:
    """Retrieves the titles of a list of YT videos.

    Args:
        youtube (Resource): YT API resource.
        response (dict[dict]): YT API response from the make_video_request function.
        video_IDs (list[str]): List of video IDs.
        use_API (bool): Determines if a new API request is made or if the response dictionary is used.

    Returns:
        titles (list[str]): List of YT videos titles.
    """
    if use_API:
        video_IDs_str = ",".join(video_IDs)
        response = (
            youtube.videos()
            .list(part="snippet", id=video_IDs_str)
            .execute(num_retries=5)
        )

    titles = [vid["snippet"]["title"] for vid in response["items"]]

    return titles


def get_tags(
    youtube=None,
    response: dict = None,
    video_IDs: list[str] = None,
    use_API: bool = False,
) -> list[list[str] | None]:
    """Retrieves the tags of YT videos.

    Args:
        youtube (Resource): YT API resource.
        response (dict[dict]): YT API response from the make_video_request function.
        video_IDs (list[str]): List of video IDs.
        use_API (bool): Determines if a new API request is made or if the response dictionary is used.

    Returns:
        tags (list[list[str]|None]): List of YT videos tags, or None if there are no tags for this video.
    """
    if use_API:
        video_IDs_str = ",".join(video_IDs)
        response = (
            youtube.videos()
            .list(part="snippet", id=video_IDs_str)
            .execute(num_retries=5)
        )

    tags = [
        vid["snippet"]["tags"] if "tags" in vid["snippet"] else None
        for vid in response.get("items", [])
    ]

    return tags


def get_descriptions(
    youtube=None,
    response: dict = None,
    video_IDs: list[str] = None,
    use_API: bool = False,
) -> list[str]:
    """Retrieves the descriptions of YT videos.

    Args:
        youtube (Resource): YT API resource.
        response (dict[dict]): YT API response from the make_video_request function.
        video_IDs (list[str]): List of video IDs.
        use_API (bool): Determines if a new API request is made or if the response dictionary is used.

    Returns:
        description (list[str]): YT videos descriptions.
    """
    if use_API:
        video_IDs_str = ",".join(video_IDs)  # Join the video IDs with commas
        response = (
            youtube.videos()
            .list(part="snippet", id=video_IDs_str)
            .execute(num_retries=5)
        )

    descriptions = [vid["snippet"]["description"] for vid in response.get("items", [])]
    return descriptions


def get_durations(
    youtube=None,
    response: dict = None,
    video_IDs: list[str] = None,
    use_API: bool = False,
) -> list[float]:
    """Retrieves the duration of YT videos.

    Args:
        youtube (Resource): YT API resource.
        response (dict[dict]): YT API response from the make_video_request function.
        video_IDs (list[str]): List of video IDs.
        use_API (bool): Determines if a new API request is made or if the response dictionary is used.

    Returns:
        durations (list[float]): List of YT videos durations in seconds.
    """
    if use_API:
        video_IDs_str = ",".join(video_IDs)
        response = (
            youtube.videos()
            .list(part="contentDetails", id=video_IDs_str)
            .execute(num_retries=5)
        )

    durations_iso = [
        vid["contentDetails"].get("duration", "PT0M3.14159265S")
        for vid in response["items"]
    ]  # Set the duration of videos without duration info to pi seconds to identify them without breaking the iso conversion
    durations = [isodate.parse_duration(d).total_seconds() for d in durations_iso]
    return durations


def get_languages(
    youtube=None,
    response: dict = None,
    video_IDs: list[str] = None,
    use_API: bool = False,
) -> list[str]:
    """Retrieves the original language of YT videos.

    Args:
        youtube (Resource): YT API resource.
        response (dict[dict]): YT API response from the make_video_request function.
        video_IDs (list[str]): List of video IDs.
        use_API (bool): Determines if a new API request is made or if the response dictionary is used.

    Returns:
        languages (list[str]): List of YT videos languages.
    """
    if use_API:
        video_IDs_str = ",".join(video_IDs)
        response = (
            youtube.videos()
            .list(part="snippet", id=video_IDs_str)
            .execute(num_retries=5)
        )

    languages = [
        (
            vid["snippet"]["defaultAudioLanguage"]
            if "defaultAudioLanguage" in vid["snippet"]
            else (
                vid["snippet"]["defaultLanguage"]
                if "defaultLanguage" in vid["snippet"]
                else "unknown"
            )
        ).split("-")[
            0
        ]  # strips regional specifiers
        for vid in response["items"]
    ]

    return languages


def get_dimensions(
    youtube=None,
    response: dict = None,
    video_IDs: list[str] = None,
    use_API: bool = False,
) -> list[str]:
    """Retrieves the dimension of YT videos (2D or 3D).

    Args:
        youtube (Resource): YT API resource.
        response (dict[dict]): YT API response from the make_video_request function.
        video_IDs (list[str]): List of video IDs.
        use_API (bool): Determines if a new API request is made or if the response dictionary is used.

    Returns:
        dimensions (list[str]): List of YT videos dimensions.
    """
    if use_API:
        video_IDs_str = ",".join(video_IDs)
        response = (
            youtube.videos()
            .list(part="contentDetails", id=video_IDs_str)
            .execute(num_retries=5)
        )

    dimensions = [vid["contentDetails"]["dimension"] for vid in response["items"]]
    return dimensions


def get_definitions(
    youtube=None,
    response: dict = None,
    video_IDs: list[str] = None,
    use_API: bool = False,
) -> list[str]:
    """Retrieves the definition (sd or hd) of YT videos.

    Args:
        youtube (Resource): YT API resource.
        response (dict[dict]): YT API response from the make_video_request function.
        video_IDs (list[str]): List of video IDs.
        use_API (bool): Determines if a new API request is made or if the response dictionary is used.

    Returns:
        definitions (list[str]): List of YT videos definitions.
    """
    if use_API:
        video_IDs_str = ",".join(video_IDs)
        response = (
            youtube.videos()
            .list(part="contentDetails", id=video_IDs_str)
            .execute(num_retries=5)
        )

    definitions = [vid["contentDetails"]["definition"] for vid in response["items"]]
    return definitions


def get_resolutions(video_IDs: list[str] = None) -> dict[str, list[int]]:
    """Retrieves the resolutions of YT videos.
    This function does not rely on the YT API but on a third party
    package (pytube), so it takes longer to run.

    Args:
        video_IDs (list[str]): List of video IDs.

    Returns:
        resolutions (dict[str, list[int]]): Dictionary mapping video IDs to the resolutions.
    """
    base_url = "http://youtube.com/watch?v"
    resolutions = {}

    for vid_ID in video_IDs:
        url = f"{base_url}={vid_ID}"

        try:
            yt = YouTube(url)
            vid_resolutions = list(
                {
                    int(stream.resolution.split("p")[0])
                    for stream in yt.streams.filter(type="video")
                }
            )
            resolutions[vid_ID] = vid_resolutions
        except Exception as e:
            print(f"Error processing video {vid_ID}: {e}")

    return resolutions


def get_framerates(video_IDs: list[str] = None) -> dict[str, list[int]]:
    """Retrieves the framerates of YT videos.
    This function does not rely on the YT API but on a third party
    package (pytube), so it takes longer to run.

    Args:
        video_IDs (list[str]): List of video IDs.

    Returns:
        framerates (dict[str, list[int]]): Dictionary mapping video IDs to the framerates.
    """
    base_url = "http://youtube.com/watch?v"
    framerates = {}

    for vid_ID in video_IDs:
        url = f"{base_url}={vid_ID}"

        try:
            yt = YouTube(url)
            vid_framerates = list(
                {stream.fps for stream in yt.streams.filter(type="video")}
            )
            framerates[vid_ID] = vid_framerates
        except Exception as e:
            print(f"Error processing video {vid_ID}: {e}")

    return framerates


def get_projections(
    youtube=None,
    response: dict = None,
    video_IDs: list[str] = None,
    use_API: bool = False,
) -> list[str]:
    """Retrieves the projection (360 or rectangular) of YT videos.

    Args:
        youtube (Resource): YT API resource.
        response (dict[dict]): YT API response from the make_video_request function.
        video_IDs (list[str]): List of video IDs.
        use_API (bool): Determines if a new API request is made or if the response dictionary is used.

    Returns:
        projections (list[str]): List of YT videos projections.
    """
    if use_API:
        video_IDs_str = ",".join(video_IDs)
        response = (
            youtube.videos()
            .list(part="contentDetails", id=video_IDs_str)
            .execute(num_retries=5)
        )

    projections = [vid["contentDetails"]["projection"] for vid in response["items"]]
    return projections


def get_view_counts(
    youtube=None,
    response: dict = None,
    video_IDs: list[str] = None,
    use_API: bool = False,
) -> list[int]:
    """Retrieves the number of views of a list of YT videos.

    Args:
        youtube (Resource): YT API resource.
        response (dict[dict]): YT API response from the make_video_request function.
        video_IDs (list[str]): List of video IDs.
        use_API (bool): Determines if a new API request is made or if the response dictionary is used.

    Returns:
        views (list[int]): List of YT videos views.
    """
    if use_API:
        video_IDs_str = ",".join(video_IDs)
        response = (
            youtube.videos()
            .list(part="statistics", id=video_IDs_str)
            .execute(num_retries=5)
        )

    views = [int(vid["statistics"]["viewCount"]) for vid in response["items"]]

    return views


def get_like_counts(
    youtube=None,
    response: dict = None,
    video_IDs: list[str] = None,
    use_API: bool = False,
) -> list[int]:
    """Retrieves the number of likes of a list of YT videos.

    Args:
        youtube (Resource): YT API resource.
        response (dict[dict]): YT API response from the make_video_request function.
        video_IDs (list[str]): List of video IDs.
        use_API (bool): Determines if a new API request is made or if the response dictionary is used.

    Returns:
        likes (list[int]): List of YT videos likes.
    """
    if use_API:
        video_IDs_str = ",".join(video_IDs)
        response = (
            youtube.videos()
            .list(part="statistics", id=video_IDs_str)
            .execute(num_retries=5)
        )

    likes = [int(vid["statistics"]["likeCount"]) for vid in response["items"]]

    return likes


def get_comment_counts(
    youtube=None,
    response: dict = None,
    video_IDs: list[str] = None,
    use_API: bool = False,
) -> list[int]:
    """Retrieves the number of comments of a list of YT videos.

    Args:
        youtube (Resource): YT API resource.
        response (dict[dict]): YT API response from the make_video_request function.
        video_IDs (list[str]): List of video IDs.
        use_API (bool): Determines if a new API request is made or if the response dictionary is used.

    Returns:
        comment_counts (list[int]): List of YT videos comment counts.
    """
    if use_API:
        video_IDs_str = ",".join(video_IDs)
        response = (
            youtube.videos()
            .list(part="statistics", id=video_IDs_str)
            .execute(num_retries=5)
        )

    comment_counts = [
        int(vid["statistics"]["commentCount"]) for vid in response["items"]
    ]

    return comment_counts


def get_likes_to_views_ratio(
    likes,
    views,
    youtube=None,
    response: dict = None,
    video_IDs: list[str] = None,
    use_API: bool = False,
) -> list[int | float]:
    """Retrieves the likes to views ratio of a list of YT videos.

    Args:
        likes (list[int]): List of the number of likes.
        views (list[int]): List of the number of views.
        youtube (Resource): YT API resource.
        response (dict[dict]): YT API response from the make_video_request function.
        video_IDs (list[str]): List of video IDs.
        use_API (bool): Determines if a new API request is made or if the response dictionary is used.

    Returns:
        ratio (list[int|float]): List of YT videos' likes to views ratios.
    """
    if use_API:
        views = get_view_counts(youtube, response, video_IDs, use_API)
        likes = get_like_counts(youtube, response, video_IDs, use_API)

    ratio = helpers.divide_lists(likes, views, False)

    return ratio


def get_comments_to_views_ratio(
    likes,
    views,
    youtube=None,
    response: dict = None,
    video_IDs: list[str] = None,
    use_API: bool = False,
) -> list[int | float]:
    """Retrieves the comments to views ratio of a list of YT videos.

    Args:
        comments (list[int]): List of the number of comments.
        views (list[int]): List of the number of views.
        youtube (Resource): YT API resource.
        response (dict[dict]): YT API response from the make_video_request function.
        video_IDs (list[str]): List of video IDs.
        use_API (bool): Determines if a new API request is made or if the response dictionary is used.

    Returns:
        views (list[int|float]): List of YT videos' comments to views ratios.
    """
    if use_API:
        views = get_view_counts(youtube, response, video_IDs, use_API)
        comments = get_comment_counts(youtube, response, video_IDs, use_API)

    ratio = helpers.divide_lists(comments, views, False)

    return ratio


def has_captions(
    youtube=None,
    response: dict = None,
    video_IDs: list[str] = None,
    use_API: bool = False,
) -> list[bool]:
    """Determines if YT videos have captions.

    Args:
        youtube (Resource): YT API resource.
        response (dict[dict]): YT API response from the make_video_request function.
        video_IDs (list[str]): List of video IDs.
        use_API (bool): Determines if a new API request is made or if the response dictionary is used.

    Returns:
        captions (list[bool]): True if the video has captions, False otherwise.
    """
    if use_API:
        video_IDs_str = ",".join(video_IDs)
        response = (
            youtube.videos()
            .list(part="contentDetails", id=video_IDs_str)
            .execute(num_retries=5)
        )

    captions = [vid["contentDetails"]["caption"] for vid in response["items"]]
    return captions


def is_short(
    youtube=None,
    response: dict = None,
    video_IDs: list[str] = None,
    use_API: bool = False,
) -> list[bool]:
    """Determines if videos are a short or not by putting a threshold on video duration.

    Args:
        youtube (Resource): YT API resource.
        response (dict[dict]): YT API response from the make_video_request function.
        video_IDs (list[str]): List of video IDs.
        use_API (bool): Determines if a new API request is made or if the response dictionary is used.

    Returns:
        is_short (list[bool]): True if the video is shorter than 65 seconds, False otherwise.
    """
    durations = get_durations(youtube, response, video_IDs, use_API=use_API)

    is_short = [True if length <= 65.0 else False for length in durations]

    return is_short


def is_live(
    youtube=None,
    response: dict = None,
    video_IDs: list[str] = None,
    use_API: bool = False,
) -> list[str]:
    """Retrieves the live status of YT videos.

    Args:
        youtube (Resource): YT API resource.
        response (dict[dict]): YT API response from the make_video_request function.
        video_IDs (list[str]): List of video IDs.
        use_API (bool): Determines if a new API request is made or if the response dictionary is used.

    Returns:
        live_statuses (list[str]): live if the video is live, upcoming if it is a premiere and none otherwise.
    """
    if use_API:
        video_IDs_str = ",".join(video_IDs)
        response = (
            youtube.videos()
            .list(part="snippet", id=video_IDs_str)
            .execute(num_retries=5)
        )

    live_statuses = [
        vid["snippet"]["liveBroadcastContent"] for vid in response["items"]
    ]

    return live_statuses
