# -*- coding: utf-8 -*-

# Copyright © 2014-2017 Felix Fontein
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

"""Tag cloud rendering engine."""

import math
import hashlib


def create_tag_cloud_data(tags, max_number_of_levels=10, max_tags=-1, minimal_number_of_appearances=1):
    """Create tag cloud data.

    The input is a list of tuples ``(name, count, url)`` as ``tags``.
    Here, ``name`` should be the name of the tag, ``count`` the number of
    posts with that tag, and ``url`` the link to the tag's page.

    The output is a pair ``tags, level_weights``, where ``tags`` is a list
    of tuples ``(index, name, level_weight, level_index, url)`` and
    ``level_weights`` is a list of floats.

    For every tuple in the ``tags`` return value, ``index`` is the index of
    the tag in the input ``tags`` list; ``name`` is the name of that element;
    ``level_weight`` is the assigned level; ``level_index`` is the index in
    the return value ``level_weights`` yielding ``level_weight``; and ``url``
    is the URL of the ``index``-th element of the input ``tags`` list.

    The level is a discretized version of the count. It is a value between
    zero and one.

    The returned information will be used by ``create_tag_cloud_css`` and
    ``create_tag_cloud_html`` to create the tag cloud's CSS and HTML code,
    respectively.

    The argument ``max_number_of_levels`` determines the maximal number of
    levels. The argument ``max_tags`` ensures that no more than the given
    number of tags appear in the cloud. The argument
    ``minimal_number_of_appearances`` will prune all elements with a lower
    ``count`` from the input ``tags`` list.
    """
    # Group tags by weights
    weights = dict()
    for i, (name, count, url) in enumerate(tags):
        if count < minimal_number_of_appearances:
            continue
        if count not in weights:
            weights[count] = []
        weights[count].append((name, url, i))

    weighted_tags = sorted(weights.items(), key=lambda x: -x[0])

    # Ensure max_tags
    if max_tags > 0:
        # Make sure there are at most max_tags tags, by dropping tasks with lowest weight
        count = 0
        for weight, tags in weighted_tags:
            if count < max_tags:
                if count + len(tags) > max_tags:
                    tags.sort(key=lambda tag: hashlib.md5(tag[0].encode('utf-8')).hexdigest())
                    # ... deterministic random sort ...
                    del tags[max_tags - count:]
            else:
                tags.clear()
            count += len(tags)

        while len(weighted_tags) > 0 and len(weighted_tags[-1][1]) == 0:
            del weighted_tags[-1]

    # Get list of weights
    weights = [weight for weight, tags in weighted_tags]

    # Cluster weights into levels
    clusters = []
    for left_count in range(max_number_of_levels, 1, -1):
        if len(weights) == 0:
            break
        min = weights[-1]
        max = weights[0]
        split = min + (max - min) * (left_count - 1) / float(left_count)
        cluster = []
        while len(weights) > 0 and weights[0] > split:
            cluster.append(weights[0])
            del weights[0]
        clusters.append(cluster)
    clusters.append(weights)
    while [] in clusters:
        clusters.remove([])

    # Determine level weights
    level_weights = [float(i) / len(clusters) for i in range(len(clusters), 0, -1)]

    # Map tag weights to level weights
    tag_weight_to_level_weight = dict()
    for index, (level_weight, cluster) in enumerate(zip(level_weights, clusters)):
        for tag_weight in cluster:
            tag_weight_to_level_weight[tag_weight] = (level_weight, index)

    # Compute tags
    tags = []
    for tag_weight, list in weighted_tags:
        if tag_weight in tag_weight_to_level_weight:
            level_weight, level_index = tag_weight_to_level_weight[tag_weight]
            for name, url, index in list:
                tags.append((index, name, level_weight, level_index, url))
    tags.sort()
    return tags, level_weights


def _get_hex_color(color):
    return '#' + ''.join('{:02x}'.format(int(round(c * 255))) for c in color)


def create_tag_cloud_css(tag_cloud_name, level_weights, colors=((0.4, 0.4, 0.4), (1.0, 1.0, 1.0)), background_colors=((0.133, 0.133, 0.133), ), border_colors=((0.2, 0.2, 0.2), ), font_sizes=(6, 20), round_factor=0.6):
    """Create CSS for the tag cloud.

    ``tag_cloud_name`` is integrated in the CSS selectors and should
    be the same string as provided to ``create_tag_cloud_html``. It
    should be short and be a valid CSS class name.

    ``level_weights`` are the resulting level weights returned by
    ``create_tag_cloud_data``.

    ``colors`` is a list of one or more colors that define the gradient
    from which colors for the tags are taken (depending on the level).

    ``background_colors`` is a list of one or more background colors
    that define the gradient from which background colors for the tags
    are taken.

    ``border_colors`` is a list of one or more border colors that
    define the gradient from which border colors for the tags are
    taken.

    ``font_sizes`` is a pair of numbers between which the font sizes
    for the tags are placed. The first number is used for less frequent
    tags.

    ``round_factor`` determines the border radius and the vertical
    margin by multiplying this factor with the font size.
    """
    def get_color(f, colors):
        idx = f * (len(colors) - 1)
        idx1 = int(math.floor(idx))
        if idx1 >= len(colors) - 1:
            return colors[-1]
        if idx1 < 0:
            return colors[0]
        c1 = colors[idx1]
        c2 = colors[idx1 + 1]
        f = idx - idx1
        return tuple(a + (b - a) * f for (a, b) in zip(c1, c2))

    result = '#' + tag_cloud_name + '{font-size:8px;text-align:center;vertical-align:middle;}'
    result += '#' + tag_cloud_name + ' a{white-space:nowrap;padding:1px;'
    if len(border_colors) == 1:
        result += 'border:solid 1px {0};'.format(_get_hex_color(border_colors[0]))
    if len(background_colors) == 1:
        result += 'background-color:{0};'.format(_get_hex_color(background_colors[0]))
    result += '}'
    for index, level_weight in enumerate(level_weights):
        font_size = int(round(level_weight * (font_sizes[1] - font_sizes[0]) + font_sizes[0]))
        result += '#' + tag_cloud_name + ' a.' + tag_cloud_name + str(index) + '{'
        result += 'font-size:{0}px;'.format(font_size)
        result += 'color:{0} !important;'.format(_get_hex_color(get_color(level_weight, colors)))
        if len(border_colors) > 1:
            result += 'border:solid 1px {0};'.format(_get_hex_color(get_color(level_weight, border_colors)))
        if round_factor > 0:
            result += 'border-radius:{0}px;margin:{0}px 0px;'.format(int(font_size * round_factor))
        if len(background_colors) > 1:
            result += 'background-color:{0};'.format(_get_hex_color(get_color(level_weight, background_colors)))
        result += '}'
    return result


def create_tag_cloud_html(tag_cloud_name, tags, level_weights):
    """Create HTML code for the tag cloud.

    ``tag_cloud_name`` is the CSS style name used for the generated
    tag cloud. It should be the same value as passed to
    ``create_tag_cloud_css``.

    ``tags`` and ``level_weights`` are the return values of
    ``create_tag_cloud_data``.
    """
    result = '<div id="' + tag_cloud_name + '">'
    result += ' '.join(['<a href="{1}" class="{2}">{0}</a>'.format(name, url, tag_cloud_name + str(level_index)) for _, name, level_weight, level_index, url in tags])
    result += '</div>'
    return result
