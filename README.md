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
   <a href="#example">Example</a> •
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
* Duration filtering
* Language filtering
* Shorts filtering
* Duplicate checking

## How to use
Before using this software, you first need to get a Youtube API key and create a web app to get a client secrets file (that should look like [this](src/client_secrets_template.json)). This [Corey Schafer video](https://www.youtube.com/watch?v=vQQEaSnQ_bs) goes through the process step by step.

Once that's done, either clone this repository or download the ZIP archive. Then, copy and rename the [user parameters template](src/user_params_template.json) file to *user_params.json*. Modify it so that it fits your needs (more information on how in the [following table](#user-defined-parameters) and in the [example section](#example)).

Verify that you have all of the dependencies installed (see the [requirements](requirements.txt) file).

Finally, execute the [run.py](src/run.py) file to start the software.

I would recommend creating a task to execute the program once a day.

### User-defined parameters
|Parameter|Optional|Description|Possible values|
|--|:--:|:--:|:--:|
|`required_in_channel_name`|Yes|Words that must be in channel names, typically channel names themselves. Videos from channels not containing any of the words of this list in their name will not be added.|Any string|
|`banned_in_channel_name`|Yes|Words that must not be in channel names, typically channel names themselves. Videos from channels containing any of the words of this list in their name will not be added.|Any string|
|`required_in_video_title`|Yes|Words that must be in video titles. Videos with titles not containing any of the words of this list will not be added.|Any string|
|`banned_in_video_title`|Yes|Words that must not be in video titles. Videos with titles containing any of the words of this list will not be added.|Any string|
|`required_in_description`|Yes|Words that must be in video descriptions. Videos with descriptions not containing any of the words of this list will not be added.|Any string|
|`banned_in_description`|Yes|Words that must not be in video descriptions. Videos with descriptions containing any of the words of this list will not be added.|Any string|
|`required_tags`|Yes|Tags that must be associated with the videos.|Any string|
|`banned_tags`|Yes|Tags that must not be associated with the videos.|Any string|
|`allowed_durations`|Yes|Minimum and maximum video durations (in minutes).|Two positive integers|
|`preferred_languages`|Yes|Languages the videos need to be in. Videos with an unspecified language will be added as a precaution.|Any ISO 636-1 code ([wikipedia page](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes))|
|`keep_shorts`|No|Determines whether to add shorts.|boolean
|`keep_duplicates`|No|Determines whether to add videos that are already in the playlist.|boolean
|`upload_playlist_ID`|No|ID of the playlist the videos will be added to. Playlist IDs are found at the end of their URL: `https://www.youtube.com/playlist?list=*playlist_ID*`|Playlist ID
|`verbosity`|No|Controls how much information is shown in the terminal. Options can be combined, so that selecting each option gives the same result as selecting *all*.|*all*: Everything is shown.<br>*none*: Nothing is shown.<br>*func*: Only information regarding function execution is shown.<br>*credentials*: Only information regarding credentials is shown (loading, retrieving and saving).<br>*videos*: Only information regarding added videos is shown (number, channel names and video titles).

All parameters are case-sensitive and if you do not want to use an optional parameter, replace its value with *null* or delete the entry.

### Requirements
See the [requirements](requirements.txt) file.

## Example
Let's say that you don't want to miss any of the less than 15 minutes *$1 vs.* MrBeast videos. Then you would need the following *user_params.json* file:
```
{
"required_in_channel_name": ["MrBeast"],
"banned_in_channel_name": null,
"required_in_video_title": ["$1"],
"banned_in_video_title": null,
"required_in_description":null,
"banned_in_description":null,
"required_tags": null,
"banned_tags": null,
"allowed_durations": [0,15],
"preferred_languages":["en"],
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