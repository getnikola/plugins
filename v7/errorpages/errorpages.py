# -*- coding: utf-8 -*-

# Copyright © 2016 Felix Fontein
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

from nikola.plugin_categories import Task

import os
import os.path


class CreateErrorPages(Task):
    name = "errorpages"

    http_status_codes = {
        100: 'Continue',
        101: 'Switching Protocols',
        102: 'Processing',
        200: 'OK',
        201: 'Created',
        202: 'Accepted',
        203: 'Non-Authoritative Information',
        204: 'No Content',
        205: 'Reset Content',
        206: 'Partial Content',
        207: 'Multi-Status',
        208: 'Already Reported',
        226: 'IM Used',
        300: 'Multiple Choices',
        301: 'Moved Permanently',
        302: 'Found',
        303: 'See Other',
        304: 'Not Modified',
        305: 'Use Proxy',
        306: 'Switch Proxy',
        307: 'Temporary Redirect',
        308: 'Permanent Redirect',
        400: 'Bad Request',
        401: 'Unauthorized',
        402: 'Payment Required',
        403: 'Forbidden',
        404: 'Not Found',
        405: 'Method Not Allowed',
        406: 'Not Acceptable',
        407: 'Proxy Authentication Required',
        408: 'Request Timeout',
        409: 'Conflict',
        410: 'Gone',
        411: 'Length Required',
        412: 'Precondition Failed',
        413: 'Payload Too Large',
        414: 'URI Too Long',
        415: 'Unsupported Media Type',
        416: 'Range Not Satisfiable',
        417: 'Expectation Failed',
        418: 'I\'m a teapot',
        421: 'Misdirected Request',
        422: 'Unprocessable Entity',
        423: 'Locked',
        424: 'Failed Dependency',
        426: 'Upgrade Required',
        428: 'Precondition Required',
        429: 'Too Many Requests',
        431: 'Request Header Fields Too Large',
        451: 'Unavailable For Legal Reasons',
        500: 'Internal Server Error',
        501: 'Not Implemented',
        502: 'Bad Gateway',
        503: 'Service Unavailable',
        504: 'Gateway Timeout',
        505: 'HTTP Version Not Supported',
        506: 'Variant Also Negotiates',
        507: 'Insufficient Storage',
        508: 'Loop Detected',
        510: 'Not Extended',
        511: 'Network Authentication Required',
    }

    def _error_page_path(self, name, lang):
        return [self.site.config['TRANSLATIONS'][lang], self.output_pattern.format(code=name, lang=lang)]

    def set_site(self, site):
        super(CreateErrorPages, self).set_site(site)
        self.output_pattern = self.site.config.get('HTTP_ERROR_PAGE_OUTPUT_PATTERN', '{code}.html')
        self.site.register_path_handler('errorpage', self._error_page_path)

    def _prepare_error_page(self, destination, lang, http_error_code, template):
        http_error_message = self.http_status_codes.get(http_error_code)

        title = self.site.MESSAGES[lang].get('http-error-code-{0}'.format(http_error_code))
        if title is None and http_error_message is not None:
            title = self.site.MESSAGES[lang].get(http_error_message, http_error_message)

        context = {}
        context['http_error_code'] = http_error_code
        context['http_error_message'] = http_error_message
        context['permalink'] = self.site.link('errorpage', http_error_code, lang)
        if title is not None:
            context['title'] = title

        url_type = None
        if self.site.config['URL_TYPE'] == 'rel_path':
            url_type = 'full_path'

        task = self.site.generic_renderer(lang, destination, template, self.site.config["FILTERS"], context=context, url_type=url_type)
        task['basename'] = self.name
        yield task

    def gen_tasks(self):
        yield self.group_task()

        template_pattern = self.site.config.get('HTTP_ERROR_PAGE_TEMPLATE_PATTERN', '{code}.tmpl')

        for error in self.site.config.get('CREATE_HTTP_ERROR_PAGES', []):
            for lang in self.site.config['TRANSLATIONS'].keys():
                destination = os.path.normpath(os.path.join(self.site.config['OUTPUT_FOLDER'], self.site.path('errorpage', error, lang)))
                yield self._prepare_error_page(destination, lang, error, template_pattern.format(code=error, lang=lang))
