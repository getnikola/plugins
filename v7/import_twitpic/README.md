This plugin imports Twitpic pics (including twitted text) as new posts.

This plugin:

* Creates post as a rst file using the tweet text and the `figure` directive
* Copies images to images/POSTS_OUTPUT_FOLDER/POST_SLUG/
* Uses original tweet date as post date
* Uses "Twitpic: DATE" as title
* Adds "Twitpic" as tag plus the ones passed as arguments
* Adds mentionds as hashtags as tags, but if the site already have a similar tag
it use that (to avoid "ERROR: Nikola: You have tags that are too similar")

Note: Twitpic export is a folder cotaining all your images plus a tweets.txt file.