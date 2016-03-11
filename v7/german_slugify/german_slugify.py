# -*- coding: utf-8 -*-

from nikola.plugin_categories import SignalHandler
from nikola import utils


def _needs_german_slugifying_rules(lang, locale):
    """Checks whether the given language name with corresponding locale needs German slugifying rules."""
    if locale.split('_')[0] in {'de', 'gsw'}:  # German and Allemanic German
        return True
    if lang in {'de', 'deutsch', 'german',
                'de_at', 'de_ch', 'de_de',
                'de-at', 'de-ch', 'de-de',
                'atde', 'chde', 'dede'}:
        return True
    return False


class GermanSlugify(SignalHandler):  # Could also be any other plugin type which is initialized early enough.
    def set_site(self, site):
        super(GermanSlugify, self).set_site(site)

        # First determine languages which belong to German locales
        self.german_languages = set()
        for lang, loc in utils.LocaleBorg.locales.items():
            if _needs_german_slugifying_rules(lang, loc):
                self.german_languages.add(lang)
        if len(self.german_languages) > 0:
            utils.LOGGER.info("Using German slugifying rules for the following languages: {0}".format(', '.join(sorted(self.german_languages))))
        else:
            utils.LOGGER.info("Not using German slugifying rules.")

        # Store old slugify method
        self.old_slugify = utils.slugify

        # Define new slugify method
        def new_slugify(value, lang=None, force=False):
            if lang is not None and lang in self.german_languages:
                if not isinstance(value, utils.unicode_str):
                    raise ValueError("Not a unicode object: {0}".format(value))
                value = value.replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue').replace('ß', 'ss')
                value = value.replace('Ä', 'ae').replace('Ö', 'oe').replace('Ü', 'ue')
            return self.old_slugify(value, lang=lang, force=force)

        # Setting it as utils.slugify
        utils.slugify = new_slugify

        # Note that we do not replace utils.unslugify as ae,oe,ue,ss cannot
        # be substitued by ä,ö,ü,ß in all cases.
