<h1 align="center">
   <br>
   <a href="https://github.com/Killian42/QTube/releases/latest"><img src="logo.png" alt="QTube" width="500"></a>
   <br>
</h1>

<h3 align="center">Automatically add Youtube videos to a playlist.</h3>

<p align="center">
   <a href="https://www.repostatus.org/#active"><img src="https://www.repostatus.org/badges/latest/active.svg" alt="Project Status: Active – The project has reached a stable, usable state and is being actively developed." /></a>
   <a href="https://github.com/Killian42/QTube/releases/latest"><img src="https://img.shields.io/github/v/release/Killian42/QTube" alt="Latest Version"></a>
   <a href="https://github.com/Killian42/QTube/issues"><img src="https://img.shields.io/github/issues/Killian42/QTube" alt="Open Issues"></a>
   <a href="https://github.com/Killian42/QTube/issues?q=is%3Aissue+is%3Aclosed"><img src="https://img.shields.io/github/issues-closed/Killian42/QTube?color=sucess" alt="Closed Issues"></a>
   <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/license-MIT-green" alt="License"></a>
   <a href="https://github.com/psf/black"><img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code style: black"></a>
   <a href="https://github.com/Killian42/QTube"><img src="https://img.shields.io/github/languages/code-size/Killian42/QTube" alt="Code Size"></a>
</p>

<p align="center">
   <a href="#about">About</a> •
   <a href="#features">Features</a> •
   <a href="#how-to-use">How To Use</a> •
   <a href="#examples">Examples</a> •
   <a href="#faq">FAQ</a> •
   <a href="#contact">Contact</a> •
   <a href="#acknowledgments">Acknowledgments</a> •
   <a href="#license">License</a>
</p>

## About
The reason for the existence of this software is Youtube's seemingly random behavior when it comes to notifying people that a new video has been published (late or missing notifications, useless notification bell, videos not appearing in the subscription tab, ...).

With this software, you can set a number of rules that determine which videos are added to a dedicated playlist, so you won't miss any new uploads!

## Features
Each of these rules is based on putting some kind of constraint on video properties. Currently, the following features are available:
* Channel name filtering
* Title filtering
* Description filtering
* Tags filtering
* Language filtering
* Caption filtering
* Duration filtering
* Quality filtering
* Upload date filtering
* Shorts filtering
* Duplicate checking

## How to use
Before using this software, you first need to get a Youtube API key and create a web app to get a client secrets file (that should look like [this](src/client_secrets_template.json)). This [Corey Schafer video](https://www.youtube.com/watch?v=vQQEaSnQ_bs) goes through the process step by step.

Once that's done, either clone this repository or download the ZIP archive. Then, copy and rename the [user parameters template](src/user_params_template.json) file to *user_params.json*. Modify it so that it fits your needs (more information on how in the [following table](#user-defined-parameters) and in the [examples section](#examples)).

Verify that you have all of the dependencies installed (see the [requirements](requirements.txt) file).

Finally, execute the [run.py](src/run.py) file to start the software.

I would recommend creating a task to execute the program regularly (like once a day).

### User-defined parameters
|Parameter|Optional|Description|Possible values|
|--|:--:|:--:|:--:|
|`required_in_channel_name`|Yes|Words that must be in channel names, typically channel names themselves. Videos from channels not containing any of the words of this list in their name will not be added.|Any string|
|`banned_in_channel_name`|Yes|Words that must not be in channel names, typically channel names themselves. Videos from channels containing any of the words of this list in their name will not be added.|Any string|
|`include_extra_channels`|No|Determines whether to include channels the user is not subscribed to.|boolean|
|`extra_channel_handles`|Yes|Handles of additional channels to be checked. Handles are found at the end of a channel's URL: `https://www.youtube.com/@*handle*`|Any channel handle|
|`required_in_title`|Yes|Words that must be in video titles. Videos with titles not containing any of the words of this list will not be added.|Any string|
|`banned_in_title`|Yes|Words that must not be in video titles. Videos with titles containing any of the words of this list will not be added.|Any string|
|`ignore_title_emojis`|No|Determines whether emojis are ignored in video titles.|boolean|
|`ignore_title_punctuation`|No|Determines whether punctuation is ignored in video titles.|boolean|
|`ignore_title_case`|No|Determines whether case is ignored in video titles.|boolean|
|`required_in_description`|Yes|Words that must be in video descriptions. Videos with descriptions not containing any of the words of this list will not be added.|Any string|
|`banned_in_description`|Yes|Words that must not be in video descriptions. Videos with descriptions containing any of the words of this list will not be added.|Any string|
|`required_tags`|Yes|Tags that must be associated with the videos.|Any string|
|`banned_tags`|Yes|Tags that must not be associated with the videos.|Any string|
|`preferred_languages`|Yes|Languages the videos need to be in. Videos with an unspecified language will be added as a precaution.|Any [ISO 639-1 code](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)|
|`require_captions`|No|Determines whether to add videos with no captions.|boolean|
|`caption_options`|Yes|Caption properties such as language, track kind, audio type and accessibility parameters.|See [Youtube captions docs](https://developers.google.com/youtube/v3/docs/captions)|
|`allowed_durations`|Yes|Minimum and maximum video durations (in minutes).|Two positive integers|
|`lowest_definition`|Yes|Minimum definition. Videos with definitions stricly lower than this value will not be added.|*SD* or *HD*|
|`lowest_resolution`|Yes|Minimum resolution. Videos with resolutions stricly lower than this value will not be added.|Any of [Youtube standard resolutions](https://support.google.com/youtube/answer/6375112)|
|`lowest_framerate`|Yes|Minimum framerate. Videos with framerates stricly lower than this value will not be added.|Positive integer|
|`preferred_dimensions`|Yes|Dimension the videos need to be in.|*2D*, *3D* or both|
|`preferred_projections`|Yes|Projection the videos need to be in.|*rectangular*, *360* or both|
|`run_frequency`|No|Defines the duration, in days, of the timeframe considered by the software. Can be interpreted as the frequency the program should be run.|*daily*, *weekly*, *monthly* or any positive integer|
|`keep_shorts`|No|Determines whether to add shorts.|boolean|
|`keep_duplicates`|No|Determines whether to add videos that are already in the playlist.|boolean|
|`upload_playlist_ID`|No|ID of the playlist the videos will be added to. Playlist IDs are found at the end of their URL: `https://www.youtube.com/playlist?list=*playlist_ID*`|Playlist ID|
|`verbosity`|No|Controls how much information is shown in the terminal. Options can be combined, so that selecting each option gives the same result as selecting *all*. <br>1: Everything is shown.<br>2: Nothing is shown.<br>3: Only information regarding function execution is shown.<br>4: Only information regarding credentials is shown (loading, retrieving and saving).<br>5: Only information regarding added videos is shown (number, channel names and video titles).|<br>*all*<sup> 1 </sup>, <br>*none*<sup> 2 </sup> , <br>*func*<sup> 3 </sup>, <br>*credentials*<sup> 4 </sup> ,<br>*videos*<sup> 5 </sup>.|

All parameters are case-sensitive by default and if you do not want to use an optional parameter, replace its value with *null* or delete the entry.

For further information about each parameter, check the note associated with the [release](https://github.com/Killian42/QTube/releases) they were introduced in.
### Requirements
See the [requirements](requirements.txt) file.

## Examples
This section presents examples of user parameters json files for concrete use-cases.
<p align="center">
   <a href="#example-1---every-videos-from-subscribed-channels">Every videos from subscribed channels</a> •
   <a href="#example-2---higher-quality-videos">Higher quality videos</a> •
   <a href="#example-3---specific-video-series-from-a-creator">Video series from a creator</a> 
</p>

### Example 1 - Every videos from subscribed channels
The following *user_params.json* file would add every new videos from channels you are subcribed to.
```
{
"required_in_channel_name": null,
"banned_in_channel_name": null,
"include_extra_channels": false,
"extra_channel_handles": null,
"required_in_title": null,
"banned_in_title": null,
"ignore_title_emojis": false,
"ignore_title_punctuation": false,
"ignore_title_case": false,
"required_in_description": null,
"banned_in_description": null,
"required_tags": null,
"banned_tags": null,
"preferred_languages": null,
"require_captions":false,
"caption_options": null,
"allowed_durations": null,
"preferred_dimensions": null,
"preferred_projections": null,
"lowest_definition": null,
"lowest_resolution": null,
"lowest_framerate": null,
"run_frequency":"daily",
"keep_shorts": true,
"keep_duplicates": false,
"upload_playlist_ID": "your_playlist_ID",
"verbosity": ["credentials","videos"]
}
```
### Example 2 - Higher quality videos
The following *user_params.json* file would only add videos with good quality.
```
{
"required_in_channel_name": null,
"banned_in_channel_name": null,
"include_extra_channels": false,
"extra_channel_handles": null,
"required_in_title": null,
"banned_in_title": null,
"ignore_title_emojis": false,
"ignore_title_punctuation": false,
"ignore_title_case": false,
"required_in_description": null,
"banned_in_description": null,
"required_tags": null,
"banned_tags": null,
"preferred_languages": null,
"require_captions":false,
"caption_options": null,
"allowed_durations": null,
"preferred_dimensions": ["2D"],
"preferred_projections": ["rectangular"],
"lowest_definition": "HD",
"lowest_resolution": null,
"lowest_framerate": null,
"run_frequency":"daily",
"keep_shorts": true,
"keep_duplicates": false,
"upload_playlist_ID": "your_playlist_ID",
"verbosity": ["credentials","videos"]
}
```
### Example 3 - Specific video series from a creator
The following *user_params.json* file would only add the *$1 vs.* MrBeast videos.
```
{
"required_in_channel_name": ["MrBeast"],
"banned_in_channel_name": null,
"include_extra_channels": false,
"extra_channel_handles": null,
"required_in_title": ["$1 vs."],
"banned_in_title": null,
"ignore_title_emojis": true,
"ignore_title_punctuation": false,
"ignore_title_case": true,
"required_in_description": null,
"banned_in_description": null,
"required_tags": null,
"banned_tags": null,
"preferred_languages": ["en"],
"require_captions": false,
"caption_options": null,
"allowed_durations": null,
"preferred_dimensions": ["2D"],
"preferred_projections": ["rectangular"],
"lowest_definition": "HD",
"lowest_resolution": null,
"lowest_framerate": null,
"run_frequency":"daily",
"keep_shorts": false,
"keep_duplicates": false,
"upload_playlist_ID": "your_playlist_ID",
"verbosity": ["credentials","videos"]
}
```

## FAQ
There are none yet. But don't hesitate to ask by sending me an [email](mailto:killian.lebreton35@gmail.com).

## Contact
You can reach me by [email](mailto:killian.lebreton35@gmail.com). Please put *QTube* in the subject line.

## Acknowledgments
Big thanks [Corey Schafer](https://github.com/CoreyMSchafer) for his great tutorials, as well as for providing the OAuth snippets used in this software.

## License
This project is licensed under the [MIT License](LICENSE.txt).