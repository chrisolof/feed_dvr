Documentation surrounding the use and configuration of Feed DVR
===============================================================


About
------------------------------------------

Feed DVR is a simple tool designed to keep the latest episodes of your favorite 
internet-broadcast shows available on your device.

Feed DVR harvests episodes from feeds much like a DVR harvests video content
from television broadcast channels.

How you consume these episodes is up to you.


System Requirements
-------------------
  * Python
  * A scheduled task (such as a cron job) that runs feed_dvr.py on a regular 
basis to keep your feed content fresh.


Configuration (held in configuration.json)
------------------------------------------

**url**:  (required, no default) URL to the feed


**active**:  (optional, defaults to true) false = skip over this feed, true = 
process the feed


**destination**:  (required, no default) Path to destination folder for feed 
downloads.  No trailing slash.  Using an absolute path is a good idea.


**keep**:  (optional, defaults to 5) Number of episodes to keep.  As new 
episodes become available and are downloaded, old episodes are deleted.
