# -*- coding: utf-8 -*-

# Copyright © 2013–2014 Daniel Aleksandersen and others.

# Permission is hereby granted, free of charge, to any
# person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the
# Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the
# Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice
# shall be included in all copies or substantial portions of
# the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
# OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from __future__ import print_function
import codecs
from datetime import datetime
import os
import sys
import time
import pytz

if sys.version_info[0] == 2:
    import robotparser as robotparser
    from urlparse import urljoin
    import urllib2 as web_browser
elif sys.version_info[0] >= 3:
    import urllib.robotparser as robotparser
    from urllib.parse import urljoin
    import urllib.request as web_browser

from nikola.plugin_categories import Command
from nikola.utils import get_logger


class Iarchiver(Command):
    """Archive site updates."""
    name = "iarchiver"

    doc_usage = ""
    doc_purpose = "Save new posts in the Internet Archives"

    logger = None

    def _execute(self, command, args):

        self.logger = get_logger('iarchiver', self.site.loghandlers)

        """ /robots.txt must be in root, so this use of urljoin() is intentional """
        iatestbot = robotparser.RobotFileParser(urljoin(self.site.config['SITE_URL'], "/robots.txt"))
        iatestbot.read()

        timestamp_path = os.path.join(self.site.config['CACHE_FOLDER'], 'lastiarchive')
        tzinfo = pytz.timezone(self.site.config['TIMEZONE'])
        new_iarchivedate = datetime.now(pytz.UTC)

        try:
            with codecs.open(timestamp_path, 'rb', 'utf8') as inf:
                last_iarchivedate = datetime.strptime(inf.read().strip(), "%Y-%m-%dT%H:%M:%S.%f%z")
            firstrun = False
        except (IOError, Exception) as e:
            self.logger.debug("Problem when reading `{0}`: {1}".format(timestamp_path, e))
            last_iarchivedate = datetime(1970, 1, 1).replace(tzinfo=tzinfo)
            firstrun = True

        self.site.scan_posts()

        sent_requests = False
        self.logger.info("Beginning submission of archive requests. This can take some time....")

        for post in self.site.timeline:
            postdate = datetime.strptime(post.formatted_date("%Y-%m-%dT%H:%M:%S.%f"), "%Y-%m-%dT%H:%M:%S.%f")
            postdate = postdate.replace(tzinfo=tzinfo)
            print(postdate)
            if (firstrun or last_iarchivedate <= postdate):
                post_permalink = post.permalink(absolute=True)
                archival_request = "http://web.archive.org/save/{0}".format(post_permalink)
                if (iatestbot.can_fetch("ia_archiver", post_permalink)):
                    try:
                        """ Intentionally not urlencoded """
                        web_browser.urlopen(archival_request).read()
                        self.logger.info("==> sent archive request for {0}".format(post_permalink))
                    except Exception as e:
                        self.logger.warn("==> unknown problem when archiving {0}: ({1})".format(post_permalink, e))

                    """ Throttle requests """
                    time.sleep(4)
                    sent_requests = True
                else:
                    self.logger.warn("==> /robots.txt directives blocked archiving of ({0})".format(post_permalink))

        """ Record archival time """
        with codecs.open(timestamp_path, 'wb+', 'utf8') as outf:
            outf.write(new_iarchivedate.strftime("%Y-%m-%dT%H:%M:%S.%f%z"))

        if sent_requests:
            self.logger.notice("Archival requests sent to the Internet Archive.")
        else:
            self.logger.notice("Nothing new to archive")
