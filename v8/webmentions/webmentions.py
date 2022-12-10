# -*- coding: utf-8 -*-

# Copyright © 2022 B Tasker.
#
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

import requests
import re

from blinker import signal
from lxml import html

from nikola.utils import get_logger, STDERR_HANDLER
from nikola.plugin_categories import SignalHandler


class WebMentions(SignalHandler):
    name = "webmentions"
    
    # Doc https://www.getnikola.com/extending.html says
    #
    # The easiest way to do this is to reimplement set_site() and just connect to whatever signals you want there.
    # 
    # so taking the easy route
    def set_site(self, site):
        self.site = site
        self.logger = get_logger(self.name, STDERR_HANDLER)

        # Bind to the signal
        ready = signal('deployed')
        
        # Trigger analyse_posts when the signal's received
        ready.connect(self.analyse_posts)
        
        
    def analyse_posts(self, event):
        '''
            We should get an event dict
            
            Within that, there will be deployed" which gives details of all posts that have been deployed
            
            Format of that object is here: https://nikola.readthedocs.io/en/latest/nikola.html#module-nikola.post
            
            Note: Nikola won't trigger this hook for posts with a Date (or Updated) that's before the last recorded deploy. So we won't end up re-sending webmentions if we make changes to an existing post.
            
        '''
        
        # Iterate over each post listed in "deployed"
        for post in event["deployed"]:      
            title = post.title()
            
            # Don't send for drafts
            if post.is_draft or post.post_status != "published":
                self.logger.info('Skipping Draft Post {0} with status {1}'.format(title, post.post_status))
                continue
            
            # Extract some details
            link = post.permalink(absolute=True)
            text = post.text()
            self.logger.info('Processing {0}'.format(link))

            # Calculate and retrieve the state-key for this URL
            key = "webmention-info-{0}".format(link)
            observed_links = self.site.state.get(key)
            
            if not observed_links:
                observed_links = []
        
            # Extract links from within the rendered page
            links = self.extract_links(text)
            
            # Set up a requests session so that HTTP keep-alives can be used where possible
            # this reduces connection overhead etc
            session = requests.session()
            
            # Set the user-agent for all requests in this session
            session.headers.update({"User-Agent": "Nikola SSG Webmention plugin"})
            
            # Send mentions for each
            for dest in links:
                
                # See whether a webmention's already been sent for this page and url
                # means we won't reping links every time a post is updated
                if dest in observed_links:
                    continue
                
                sent, has_mentions = self.send_webmention(link, dest, session)
                
                # We want to cache two categories of link
                #
                # Has webmentions, sent successfully
                # Does not have webmentions
                
                if sent or not has_mentions:
                    observed_links.append(dest) 

            # Now that all links have been processed, save the state
            self.site.state.set(key, observed_links)

        
    def extract_links(self, post_text):
        ''' Receive a HTML post, iterate through it looking for links out and extract the relevant URLs
        
            return: list
        '''
        tree = html.fromstring(post_text)
        
        # Map out element types and the attributes we're looking for
        # keep it simple to begin with
        #
        attribs = {
            "href" : ["a", "area"],
            "cite" : ["blockquote"]
            }
        
        urls = []
    
        # Iterate over each attribute type
        for attrib in attribs:
            for element in attribs[attrib]:
                # Find elements of type element with attribute
                xpath = "//{0}[@{1}]".format(element, attrib)
                for match in tree.xpath(xpath):
                    # Remove URL fragments
                    u = match.get('href').split("#")[0]
                    urls.append(u)
        
        # Make the list unique
        urls = list(set(urls))
        return urls
        

    def send_webmention(self, ownlink, dest, session):
        ''' Send a webmention to a destination link
        
        This involves
        
        - Retrieving the link
        - checking for rel=webmention in the response headers
        - checking for rel=webmention in meta tags
        
        If either is found (header takes precedence) then send a webmention to
        the specified endpoint
        '''
        
        # don't ping absolute links to own domain
        if dest.startswith(self.site.config['SITE_URL']):
            return False, False
        
        # Skip relative links
        if not dest.startswith("http://") and not dest.startswith("https://"):
            return False, False
        
        # Check for a webmention endpoint
        ep = self.get_webmention_endpoint(dest, session)
        
        if not ep:
            return False, False
        
        # Now we actually send the webmention
        #
        # This is fairly simple, we're placing a form request with
        #
        # source = [our url]
        # target = [linked url]
        data = {
                "source" : ownlink,
                "target" : dest
            }
        
        self.logger.info('Sending WebMention to {0} for {1}'.format(ep, dest))
        r = session.post(ep, data=data)
        if r.status_code not in [200, 201, 202, 204]:
            self.logger.info('Received {0}'.format(r.status_code))
            return False, True
        
        return True, True
    
    
    def get_webmention_endpoint(self, dest, session):
        ''' Place a request to the linked target and 
            look for information about webmentions 
            
            - link headers
            - HTML meta tags (TODO)
        '''
        
        # Place a HEAD for the path
        r = session.head(dest)
        if r.status_code != 200:
            return False
        
        # See if there's a Link header. 
        # 
        # Note: if there are multiple (there often are), requests will have collapsed them into
        # a single comma seperated entry
        #
        # Note2: lookup is not case-sensitive: requests will accept "Link", "link", "lINk" etc
        if "link" not in r.headers:
            # Pass off to the HTML link extractor
            return self.get_html_link(dest, session)
        
        # Need to see if any of the headers are for webmentions
        for link_h in r.headers["link"].split(","):
            mention_link = self.check_link_header_for_webmention(link_h)
            if mention_link:
                # found one
                return mention_link

        # If we reached this point, there was no webmention header
        # but, the spec also allows them in HTML meta-tags
        #
        #
        # It's true that there's a call to this earlier
        # but this isn't a mistake
        # it may be that there were non-webmention link headers returned
        return self.get_html_link(dest, session)
            
            
    def get_html_link(self, dest, session):
        ''' Fetch a destination link and extra webmention tags if present
        '''
        # Fetch the link
        r = session.get(dest)
        if r.status_code != 200:
            return False

        # ensure the linked dest *is* HTML
        if "content-type" not in r.headers or "html" not in r.headers["content-type"].lower():
            # Not HTML, don't bother
            return False

        # Feed into lxml
        tree = html.fromstring(r.content.decode("utf-8"))
        
        # Look for relevant tags
        #
        # We need to look for link and a
        # https://www.w3.org/TR/webmention/#sender-discovers-receiver-webmention-endpoint
        #
        # Must be ordered in document order, so we need to do it in one query :(
        xpath_q = '(//link|//a)[contains(concat(" ", @rel, " "), " webmention ") or contains(@rel, "webmention.org")]'
        
        # Do it
        for match in tree.xpath(xpath_q):
            # Don't return empty values
            if len(match.get('href')) > 0:
                return match.get('href')
        
        return False
        
    
    def check_link_header_for_webmention(self, header):
        ''' Process a header and look for webmention related entries
        '''
        
        regexes = [
            '<(.[^>]+)>;\s+rel\s?=\s?[\"\']?(http:\/\/)?webmention(\.org)?\/?[\"\']?'
            ]
        
        if "webmention" not in header:
            return False
        
        for regex in regexes:
            m = re.search(regex, header, re.IGNORECASE)
            if m:
                return m.group(1)

        # Must not have found anything
        return False
        
