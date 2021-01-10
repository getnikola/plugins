import re
from typing import List, Optional

from markdown.extensions import Extension
from markdown.extensions.attr_list import get_attrs
from markdown.extensions.fenced_code import FencedBlockPreprocessor

from nikola import Nikola
from nikola.plugin_categories import MarkdownExtension
from nikola.utils import LocaleBorg, req_missing, slugify

DEFAULT_PLANTUML_MARKDOWN_ARGS = []


class PlantUmlMarkdownProcessor(FencedBlockPreprocessor):
    def __init__(self, md, config, site, logger):
        super().__init__(md, config)
        self._logger = logger
        self._plantuml_manager = None  # Lazily retrieved because it might not exist right now
        self._plantuml_markdown_args = list(site.config.get('PLANTUML_MARKDOWN_ARGS', DEFAULT_PLANTUML_MARKDOWN_ARGS))
        self._prefix: List[str] = []
        self._site: Nikola = site

    @property
    def plantuml_manager(self):
        """PlantUmlManager instance from the "plantuml" plugin"""
        if not self._plantuml_manager:
            plugin_info = self._site.plugin_manager.getPluginByName('plantuml', category='Task')
            if not plugin_info:
                req_missing("plantuml plugin", "use the plantuml_markdown plugin", python=False)
            self._plantuml_manager = plugin_info.plugin_object.plantuml_manager
        return self._plantuml_manager

    def reset(self):
        self._prefix = []

    def run(self, lines):
        def replace(match):
            lang, _id, classes, config = None, '', [], {}
            if match.group('attrs'):
                _id, classes, config = self.handle_attrs(get_attrs(match.group('attrs')))
                _id = slugify_id(_id)
                if len(classes):
                    lang = classes[0]
            elif match.group('lang'):
                lang = match.group('lang')
                classes.append(lang)

            if lang == 'plantuml-prefix':
                self._prefix = [f"-c{line}" for line in match.group('code').split('\n')]
                return ''

            if lang != 'plantuml':
                return match.group()  # the normal FencedBlockPreprocessor extension will process it later

            def div_start():
                return [f'<div class="{" ".join(classes)}" style="display: inline-block; vertical-align: top;">']

            def listing():
                listing_lines = match.group().split('\n')
                listing_lines[0] = first_line_for_listing_block(match)
                rendered = FencedBlockPreprocessor.run(self, listing_lines)
                return div_start() + rendered + ['</div>']

            def svg():
                rendered_bytes, error = self.plantuml_manager.render(
                    match.group('code').encode('utf8'),
                    self._plantuml_markdown_args + self._prefix + ['-tsvg']
                )
                if error:
                    # Note we never "continue" when rendered_bytes is empty because that likely means PlantUML failed to start
                    if len(rendered_bytes) and self.plantuml_manager.continue_after_failure:
                        self._logger.warning(error)
                    else:
                        raise Exception(error)
                rendered_str = rendered_bytes.decode('utf8')
                rendered_str = re.sub(r'^<\?xml [^>]+\?>', '', rendered_str)  # remove "<?xml ... ?>" header
                return div_start() + [rendered_str, '</div>']

            html = [f'<div id="{_id}">' if _id else '<div>']
            if 'listing+svg' in config:
                html.extend(listing())
                html.extend(svg())
            elif 'svg+listing' in config:
                html.extend(svg())
                html.extend(listing())
            elif 'listing' in config:
                html.extend(listing())
            else:
                html.extend(svg())

            html.append('</div>')

            return self.md.htmlStash.store(''.join(html))

        return self.FENCED_BLOCK_RE.sub(replace, '\n'.join(lines)).split('\n')


def first_line_for_listing_block(match):
    line = [match.group('fence')]
    if match.group('attrs'):
        attrs = match.group('attrs')
        attrs = attrs.replace('.plantuml', '.text', 1)
        attrs = re.sub(r' #([^ =]*)', lambda id_match: f' anchor_ref={slugify_id(id_match.group(0))}', attrs)
        line.extend(('{', attrs, '}'))
    if match.group('lang'):
        line.append('text')
    if match.group('hl_lines'):
        line.append(f" hl_lines={match.group('quot')}{match.group('hl_lines')}{match.group('quot')}")
    return ''.join(line)


def slugify_id(_id: str) -> str:
    # This matches processing of anchor_ref in NikolaPygmentsHTML
    return slugify(_id, lang=LocaleBorg().current_lang, force=True)


class PlantUmlMarkdownExtension(MarkdownExtension, Extension):
    name = "plantuml_markdown"
    _processor: Optional[PlantUmlMarkdownProcessor]

    def extendMarkdown(self, md):
        try:
            self._processor = PlantUmlMarkdownProcessor(md, self.getConfigs(), self.site, self.logger)
            md.preprocessors.register(self._processor, 'fenced_code_block_plantuml', 26)
            md.registerExtension(self)
        except TypeError as e:  # Kludge to avoid Extension._extendMarkdown() hiding of TypeErrors
            raise Exception(e)

    def reset(self):
        self._processor.reset()
