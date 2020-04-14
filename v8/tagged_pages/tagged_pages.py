# -*- coding: utf-8 -*-

# Copyright © 2012-2020 Roberto Alsina and others.

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

"""Classify pages by tags."""


from nikola import utils
from nikola.plugins.task.tags import ClassifyTags


class ClassifyPagesByTags(ClassifyTags):
    """Classify the posts by tags."""

    name = "tagged_pages"

    classification_name = "tagged_pages"
    overview_page_variable_name = "tagged_pages"
    overview_page_items_variable_name = "items"
    more_than_one_classifications_per_post = True
    has_hierarchy = False
    show_list_as_subcategories_list = False
    template_for_classification_overview = "tags.tmpl"
    always_disable_rss = True
    always_disable_atom = True
    apply_to_posts = False
    apply_to_pages = True
    omit_empty_classifications = True
    add_other_languages_variable = True
    show_list_as_index = False
    template_for_single_list = "tagged_pages.tmpl"
    path_handler_docstrings = {
        "tagged_pages_index": "",
        "tagged_pages": "",
        "tagged_pages_atom": "",
        "tagged_pages_rss": "",
    }

    def set_site(self, site):
        """Set site, which is a Nikola instance."""
        super().set_site(site)
        self.minimum_post_count_per_classification_in_overview = self.site.config[
            "TAGLIST_MINIMUM_POSTS"
        ]
        self.translation_manager = utils.ClassificationTranslationManager()
        self.pages_index_path = utils.TranslatableSetting(
            "TAGGED_PAGES_INDEX_PATH",
            self.site.config["TAGGED_PAGES_INDEX_PATH"],
            self.site.config["TRANSLATIONS"],
        )
        self.pages_path = utils.TranslatableSetting(
            "TAGGED_PAGES_PATH",
            self.site.config["TAGGED_PAGES_PATH"],
            self.site.config["TRANSLATIONS"],
        )

    def get_overview_path(self, lang, dest_type="page"):
        """Return a path for the list of all classifications."""
        if self.pages_index_path(lang):
            path = self.pages_index_path(lang)
            return [_f for _f in [path] if _f], "never"
        else:
            return [_f for _f in [self.pages_path(lang)] if _f], "always"

    def get_path(self, classification, lang, dest_type="page"):
        """Return a path for the given classification."""
        return (
            [
                _f
                for _f in [
                    self.pages_path(lang),
                    self.slugify_tag_name(classification, lang),
                ]
                if _f
            ],
            "auto",
        )

    def provide_overview_context_and_uptodate(self, lang):
        """Provide data for the context and the uptodate list for the list of all classifiations."""
        kw = {
            "tag_path": self.site.config["TAG_PATH"],
            "taglist_minimum_post_count": self.site.config["TAGLIST_MINIMUM_POSTS"],
            "tzinfo": self.site.tzinfo,
            "tag_descriptions": self.site.config["TAG_DESCRIPTIONS"],
            "tag_titles": self.site.config.get(
                "TAGGED_PAGES_TITLES", self.site.config["TAG_TITLES"]
            ),
        }
        context = {
            "title": self.site.MESSAGES[lang]["Tags"],
            "description": self.site.MESSAGES[lang]["Tags"],
            "pagekind": ["list", "tags_page"],
        }
        kw.update(context)
        return context, kw

    def provide_context_and_uptodate(self, classification, lang, node=None):
        """Provide data for the context and the uptodate list for the list of the given classifiation."""
        kw = {
            "tag_path": self.site.config["TAG_PATH"],
            "taglist_minimum_post_count": self.site.config["TAGLIST_MINIMUM_POSTS"],
            "tzinfo": self.site.tzinfo,
            "tag_descriptions": self.site.config["TAG_DESCRIPTIONS"],
            "tag_titles": self.site.config.get(
                "TAGGED_PAGES_TITLES", self.site.config["TAG_TITLES"]
            ),
        }
        context = {
            "title": kw["tag_titles"]
            .get(lang, {})
            .get(classification, "Pages tagged %s" % classification),
            "description": self.site.config["TAG_DESCRIPTIONS"]
            .get(lang, {})
            .get(classification),
            "pagekind": ["tag_page", "index" if self.show_list_as_index else "list"],
            "tag": classification,
        }
        kw.update(context)
        return context, kw
