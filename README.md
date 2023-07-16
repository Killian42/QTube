# Youtube_Bot
Youtube Bot is a software that automatically adds Youtube videos to a playlist for you!
## About
This reason behind the existence of this software is Youtube's apparent quasi-random behavior about informing people that a new video came out (no notification even when the bell is clicked, videos not showing up the subscription tab, ...). 

With this software, you can specify a certain number of rules that will define what videos are added to a dedicated playlist, so that you won't miss any new uploads!

## How to use
* Clone the repo
* Get a Youtube API key
* Create a web app to get a client secrets file. It should look like [this](client_secrets_template.json)
* Copy and rename the [user parameters template file](user_params_template.json) to *user_params.json*. Modify it so that it fits your needs
* Execute the [run.py](run.py) file

I would personally recommend to create a task to execute the program once a day.

To get more information on setting up the API key and cliens secrets, watch this [video](https://www.youtube.com/watch?v=vQQEaSnQ_bs) from Corey Schafer (and big thanks to him for providing the code to use oauth!)

## User parameters:
* *upload_playlist_ID* : ID of the playlist the videos will be added to.
* *words_in_channel_names* : Whitelist of words present in channel names, typically channel names themselves. Videos from channels not containing any of the words will not be considered.
* *keep_shorts* : Determines if shorts are added to the playlist.