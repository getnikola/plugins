from nikola.plugin_categories import ConfigPlugin
from nikola import utils
import locale
import datetime
from babel import Locale, dates
import platform

class BabelDates(ConfigPlugin):
    """
    Use Babel to format dates
    """
    def __init__(self):
        self.name = 'babelDates'

    def set_site(self, site):
        self.site = site
        if self.site.config['DATE_FANCINESS'] == 0 and not self.site.config.get('BABEL_DATE_FORMAT') is None:
            babel_date_format = utils.TranslatableSetting('BABEL_DATE_FORMAT', self.site.config['BABEL_DATE_FORMAT'], self.site.config['TRANSLATIONS'])
            for lang in self.site.config['TRANSLATIONS']:
                try:
                    self.site.config['DATE_FORMAT'][lang] = babel_date_format(lang)
                except KeyError:
                    self.site.config['DATE_FORMAT'][lang] = 'medium'
            utils.LocaleBorg().add_handler(formatted_date_handler = self.babel_date_formatter)
        super(BabelDates, self).set_site(site)

    def babel_date_formatter(self, date_format, date, lang):
        if platform.system() == 'Windows':
            norm_locale = locale.normalize(lang).split('.')[0]
        else:
            norm_locale = self.site.config['LOCALES'][lang]
        return dates.format_datetime(date, format = date_format, locale = norm_locale)
