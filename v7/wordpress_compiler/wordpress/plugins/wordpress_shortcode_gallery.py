# -*- coding: utf-8 -*-

# A WordPress compiler plugin for Nikola
#
# Copyright (C) 2014-2015 by Felix Fontein
# Copyright (C) by the WordPress contributors
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import re
import nikola.plugin_categories
from nikola.utils import get_logger, STDERR_HANDLER

_LOGGER = get_logger('wordpress_shortcode_gallery', STDERR_HANDLER)


def sanitize_html_class(clazz):
    # Strip out percent encoded octets
    clazz = re.sub('%[a-fA-F0-9][a-fA-F0-9]', '', clazz)
    # Limit to A-Z,a-z,0-9,_,-
    clazz = re.sub('[^A-Za-z0-9_-]', '', clazz)
    return clazz


def sanitize_html_text(text, sanitize_quotes=False):
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    if sanitize_quotes:
        text = text.replace('"', '&quot;')
    return text


class Gallery(nikola.plugin_categories.CompilerExtension):
    name = 'wordpress_shortcode_gallery'
    compiler_name = 'wordpress'

    def __init__(self):
        super(Gallery, self).__init__()

    def _choose_size(self, w, h, size, meta=None):
        # Determine maximal size
        if meta and 'width' in meta and 'height' in meta:
            max_w = meta['width']
            max_h = meta['height']
        elif size == 'thumb' or size == 'thumbnail':
            max_w = 128
            max_h = 96
        elif size == 'medium':
            # Depends on theme. We pick some 'random' values here
            max_w = 150
            max_h = 150
        elif size == 'large':
            # Depends on theme. We pick some 'random' values here
            max_w = 500
            max_h = 500
        else:
            max_w = w
            max_h = h
        # Make sure that w x h is at most as large as max_w x max_h
        w = float(w)
        h = float(h)
        if w > max_w:
            h = h / w * max_w
            w = float(max_w)
        if h > max_h:
            w = w / h * max_h
            h = float(max_h)
        return int(w), int(h)

    def _process_gallery_tags(self, args, content, tag, context):
        # Get gallery counter per post
        gallery_counter = context.inc_plugin_counter('wordpress_shortcode_gallery', 'counter')

        # Load attachments
        attachments = context.get_additional_data('attachments')
        if attachments is None:
            _LOGGER.error("Cannot find attachments for post {0}!".format(context.get_name()))
            return "(Error loading gallery)"

        # Load images
        if 'ids' not in args:
            _LOGGER.error("We only support galleries where all images are explicitly listed! (Post {0})".format(context.get_name()))
            return "(Error loading gallery)"
        ids = args.pop('ids')
        ids = [id for id in ids.split(',')]
        images = []
        for id in ids:
            attachment = attachments.get(id)
            if attachment is None:
                _LOGGER.error("Cannot find attachment {1} for post {0}!".format(context.get_name(), id))
                return "(Error loading gallery)"
            images.append(attachment)

        # Empty gallery
        if len(images) == 0:
            return ''

        # Load arguments
        columns = int(args.pop('columns', '3'))  # 0 = no breaks
        link = args.pop('link', 'file')  # 'file' or 'none'
        itemtag = args.pop('itemtag', 'dl')
        icontag = args.pop('icontag', 'dt')
        captiontag = args.pop('captiontag', 'dd')
        size = args.pop('size', 'thumbnail')
        rtl = False

        # Render gallery
        gallery_id = '{0}-{1}'.format(hex(context.id), gallery_counter)
        gallery_name = 'wordpress-gallery-{0}'.format(gallery_id)
        result = ''
        result += '''<style type="text/css">
#{0} {{
  margin: auto;
}}
#{0} .wordpress-gallery-item {{
  float: {1};
  margin-top: 10px;
  text-align: center;
  width: {2}%;
}}
#{0} img {{
  border: 2px solid #cfcfcf;
}}
#{0} .wordpress-gallery-caption {{
  margin-left: 0;
}}
</style>'''.format(gallery_name, 'right' if rtl else 'left', 100.0 / columns if columns > 0 else 100)

        size_class = sanitize_html_class(size)
        result += '<div id="{0}" class="wordpress-gallery wordpress-gallery-id-{1} gallery-columns-{2} gallery-size-{3}">'.format(gallery_name, gallery_id, columns, size_class)
        for i, image in enumerate(images):
            if columns > 0 and i > 0 and i % columns == 0:
                result += '<br style="clear: both;"/>'
            url = image['files'][0]
            alt_text = image.get('excerpt', image.get('title', ''))
            caption = image.get('excerpt', None)
            if 'files_meta' in image and 'width' in image['files_meta'][0] and 'height' in image['files_meta'][0]:
                w = image['files_meta'][0]['width']
                h = image['files_meta'][0]['height']
                orientation = 'portrait' if h > w else 'landscape'
            else:
                orientation = None
            # Determine file
            file_index = 0
            if 'files_meta' in image:
                for index in range(1, len(image['files'])):
                    if size == image['files_meta'][index].get('size'):
                        file_index = index
            # Render entry
            result += '<{0} class="wordpress-gallery-item">'.format(itemtag)
            result += '<{0} class="wordpress-gallery-icon{1}">'.format(icontag, (' ' + orientation) if orientation else '')
            if link == 'file':
                result += '<a href="{0}">'.format(url)
            file = image['files'][file_index]
            if 'files_meta' in image and 'width' in image['files_meta'][file_index] and 'height' in image['files_meta'][file_index]:
                w = image['files_meta'][file_index]['width']
                h = image['files_meta'][file_index]['height']
                w, h = self._choose_size(w, h, size, image['files_meta'][file_index] if file_index > 0 else None)
                result += '<img src="{0}" class="wordpress-gallery-thumb" class="{1}" width="{2}" height="{3}" alt="{4}"/>'.format(file, size_class, w, h, sanitize_html_text(caption, True))
            else:
                result += '<img src="{0}" class="wordpress-gallery-thumb" class="{1}" alt="{2}"/>'.format(file, size_class, sanitize_html_text(alt_text, True))
            if link == 'file':
                result += '</a>'
            result += '</{0}>'.format(icontag)
            if caption and captiontag:
                result += '<{0} class="wordpress-gallery-caption">'.format(captiontag)
                result += sanitize_html_text(caption)
                result += '</{0}>'.format(captiontag)
            result += '</{0}>'.format(itemtag)
        if len(images) > 0:
            result += '<br style="clear: both;"/>'
        result += '</div>'
        return result

    def register(self, compile_wordpress, wordpress_modules):
        self._user_logged_in = False
        self._compile_wordpress = compile_wordpress
        compile_wordpress.register_shortcode('gallery', self._process_gallery_tags)
