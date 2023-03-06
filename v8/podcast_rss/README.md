# rss_ogg
Used for producing podcast rss.xml files when trying to publish mp3 and ogg feeds. 

# usage
Add 
`.. ogg_enclosure: <file>` 
and
`.. ogg_enclosure_length: <size in bytes>` 
to your source files to provide the ogg file and length to create a separate ogg feed. 

# Other notes
Even if you're not creating multiple feeds, many podcatchers require enclosures to have an accurate length. Please consider setting it.
