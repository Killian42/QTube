def make_caption_requests(youtube, video_IDs: list[str]) -> dict[dict]:
    """Retrieves API caption responses of a list of YT videos

    Args:
        youtube (Resource): YT API resource
        video_IDs (list[str]): List of video IDs

    Returns:
        responses_dict (dict[dict]): Dictionary with video IDs as keys and YT API caption responses as values
    """
    responses_dict = {
        video_ID: youtube.captions().list(part="snippet", videoId=video_ID).execute()
        for video_ID in video_IDs
    }

    return responses_dict


def get_captions(
    youtube=None,
    response: dict = None,
    video_IDs: list[str] = None,
    use_API: bool = False,
) -> dict[dict]:
    """Retrieves the captions of YT videos

    Args:
        youtube (Resource): YT API resource
        response (dict[dict]): YT API response from the make_caption_request function
        video_IDs (list[str]): List of video IDs
        use_API (bool): Determines if a new API request is made or if the response dictionary is used

    Returns:
        captions_dict (dict[dict]): Dictionary with video IDs as keys and caption dictionaries as values
    """
    if use_API:
        response = make_caption_requests(youtube, video_IDs)

    captions_dict = {}
    for video_ID, vid_resp in response.items():
        caption_dict = {
            caption["id"]: caption["snippet"] for caption in vid_resp.get("items", [])
        }
        captions_dict.update({video_ID: caption_dict})

    return captions_dict
