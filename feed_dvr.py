#! /usr/bin/env python

# Copyright 2014 Christopher Olof Caldwell <chrisolof@gmail.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import json
import urllib2
import sys
import os
from lxml import etree

# Get the location of feed_dvr on the system
feed_dvr_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

# Open our json config file
with open(os.path.join(feed_dvr_dir, 'configuration.json')) as config_json:
    # Decode the json into an object we can work with
    configuration = json.load(config_json)
    # Open our database
    with open(os.path.join(feed_dvr_dir, 'database.json'), 'r+') as database_json:
        # Decode the json into an object we can work with
        database = json.load(database_json)
        # For each feed
        for feed in configuration['feeds']:
            # If the feed is active (feeds are active by default)
            if ( 'active' not in feed or feed['active'] ):
                # Set default number of episodes to keep if setting wasn't
                # specified
                if ( 'keep' not in feed or not feed['keep'] ):
                    keep = 5
                else:
                    keep = feed['keep']
                # Load up our xml tree
                tree = etree.parse(feed['url'])
                newest_episodes = list()
                # Iterate through the items in the feed
                for item in tree.iterfind('channel/item/ns:content', namespaces={'ns': 'http://search.yahoo.com/mrss/'}):
                    if 'url' in item.attrib:
                        newest_episodes.append(item.attrib['url'])
                    # If we're up to our episode limit, break out
                    if len(newest_episodes) == keep:
                        break
                if len(newest_episodes) > 0:
                    if feed['url'] not in database['feeds']:
                        database['feeds'][feed['url']] = list()
                    # Reverse the list so that we download episodes from oldest
                    # to newest.  This is important for keeping the order of
                    # episodes in the database correct on an initial feed
                    # download.
                    newest_episodes.reverse();
                    # Iterate through our new episodes.  If our new episode is
                    # not in the database already, download it and add it into
                    # the database.
                    for new_episode in newest_episodes:
                        # If we don't have this feed in our database, download
                        # it
                        if new_episode not in database['feeds'][feed['url']]:
                            # Grab the filename from the URL
                            filename = new_episode.split('/')[-1]
                            # Open the file for downloading from the remote
                            # server
                            response = urllib2.urlopen(new_episode)
                            # Open the local file for writing
                            with open(os.path.join(feed['destination'], filename), "w") as f:
                                # Download the file
                                print ('Downloading ' + new_episode)
                                f.write(response.read())
                                print ('Downloaded ' + filename + ' to ' + feed['destination'])
                                # Add this to the top of the list of episodes
                                # we're aware of having downloaded for this
                                # feed.
                                database['feeds'][feed['url']].insert(0, new_episode)
                                # If by downloading this episode we've gone over
                                # the number of episodes we're to keep for this
                                # feed, remove the oldest
                                if len(database['feeds'][feed['url']]) > keep:
                                    # Remove oldest file
                                    # Grab the URL of the oldest file we have,
                                    # and at the same time take it out of our
                                    # database.
                                    url_for_removal = database['feeds'][feed['url']].pop()
                                    # From the URL, grab the filename
                                    filename_for_removal = url_for_removal.split('/')[-1]
                                    # Remove the file if it exists
                                    if os.path.isfile(os.path.join(feed['destination'], filename_for_removal)):
                                        print ('Removing ' + filename_for_removal + ' from ' + feed['destination'])
                                        try:
                                            os.remove(os.path.join(feed['destination'], filename_for_removal))
                                        except OSError:
                                            print ('Attempt to remove ' + filename_for_removal + ' from ' + feed['destination'] + ' failed')
                                            pass
                                # Update our database on disk
                                # Move to the start of our file
                                database_json.seek(0)
                                json.dump(database, database_json, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None, indent=4, separators=(',', ': '))
                                database_json.truncate()
