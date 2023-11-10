# QTube
QTube is a software that automatically adds Youtube videos to a playlist for you!
## About
The reason for the existence of this software is Youtube's seemingly random behavior when it comes to notifying people that a new video has been published (late or missing notifications, useless notification bell, videos not appearing in the subscription tab, ...).

With this software, you can set a number of rules that determine which videos are added to a dedicated playlist, so you won't miss any new uploads!

## How to use
* Clone the repo
* Get a Youtube API key
* Create a web app to get a client secrets file. It should look like [this](src/client_secrets_template.json)
* Copy and rename the [user parameters template file](src/user_params_template.json) to *user_params.json*. Modify it so that it fits your needs
* Execute the [run.py](src/run.py) file

I would personally recommend to create a task to execute the program once a day.

To get more information on setting up the API key and client secrets, you can watch this [video](https://www.youtube.com/watch?v=vQQEaSnQ_bs) from Corey Schafer. Big thanks to him for making this helpful and detailed video, as well as providing the OAuth snippets.

## User parameters:
* *required_in_channel_name* (optional): Words that must be in channel names, typically channel names themselves (case sensitive). Videos from channels not containing any of the words of this list in their name will not be added.
* *banned_in_channel_name* (optional): Words that must not be in channel names, typically channel names themselves (case sensitive). Videos from channels containing any of the words of this list in their name will not be added.
* *required_in_video_title* (optional): Words that must be in video titles (case sensitive). Videos with titles not containing any of the words of this list will not be added.
* *banned_in_video_title* (optional): Words that must not be in video titles (case sensitive). Videos with titles containing any of the words of this list will not be added.
* *required_tags* (optional): Tags that must be associated with the videos (case sensitive).
* *banned_tags* (optional): Tags that must not be associated with the videos (case sensitive).
* *allowed_durations* (optional): Minimum and maximum video durations (in minutes).
* *preferred_languages* (optional): Languages the videos need to be in. See this [wikipedia page](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) for the language codes. Videos with an unspecified language will be added as a precaution.
* *keep_shorts* (required): Determines whether to add shorts.
* *keep_duplicates* (required): Determines whether to add videos that are already in the playlist.
* *upload_playlist_ID* (required): ID of the playlist the videos will be added to. The playlist ID can be found in the playlist URL after the equal sign: `https://www.youtube.com/playlist?list=*playlist_ID*`
* *verbosity* (required): Controls how much information is shown in the terminal. Options are:
  * *all*: Everything is shown.
  * *none*: Nothing is shown.
  * *func*: Only information regarding function execution is shown.
  * *credentials*: Only information regarding credentials is shown (loading, retrieving and saving).
  * *videos*: Only information regarding added videos is shown (number, channel names and video titles).
  
  Options can be combined, so that selecting each option gives the same result as selecting *all*.

If you do not want to use an optional parameter, replace it with *null* or delete the entry.