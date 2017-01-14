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

"""Provide the Nikola plugin LaTeXFormulaRendererPlugin, an infrastructure to render LaTeX formulae as images."""

from nikola.plugin_categories import Task
from nikola import utils

import gzip
import hashlib
import os
import tempfile
import shutil
import subprocess
import base64
import json
import threading
import xml.etree.ElementTree

from PIL import Image

_LOGGER = utils.get_logger('compile_latex.formula', utils.STDERR_HANDLER)


class LaTeXError(Exception):
    """Represent an error which occured when LaTeX was run."""

    def __init__(self, message, ret_code=None):
        """Initialize LaTeX exception."""
        super(LaTeXError, self).__init__(message)
        self.ret_code = ret_code

    def get_ret_code(self):
        """Retrieve return code."""
        return self.ret_code


def _convert_color_component(float):
    """Convert color component between 0 and 1 to integer value in [0, 255]."""
    return max(0, min(255, int(float * 255)))


def _ensure_dir_existence(dir):
    """Try to ensure that given directory exists; returns True if it does."""
    try:
        utils.makedirs(dir)
        return True
    except os.error:
        return os.path.isdir(dir)


class FormulaCache(object):
    """Does bookkeeping for formula file names and allows to store/retrieve cached formula files."""

    # The prefix put before formula file names
    __output_prefix = "/"

    # The directory where to put the final formula images
    __output_directory = "."

    # Whether the output directory is known to exist
    __output_directory_exists = False

    # The cache directory where to put the cached formula images and the formula filename database
    __cache_directory = None

    # Whether the cache directory is known to exist
    __cache_directory_exists = False

    def __init__(self):
        """Create formula cache."""
        self.__internal_lock = threading.Lock()
        self.__database = None

    def set_cache_directory(self, cacheDirectory):
        """Set cache directory to given directory."""
        self.__cache_directory = cacheDirectory
        self.__cache_directory_exists = False

    def set_output_directory(self, output_directory):
        """Set output directory to given directory."""
        self.__output_directory = output_directory
        self.__output_directory_exists = False

    def set_output_prefix(self, output_prefix):
        """Set output prefix to given prefix."""
        if len(output_prefix) > 0:
            # Make sure that output_prefix begins and ends with '/'
            if output_prefix[-1] != '/':
                output_prefix += '/'
            if output_prefix[0] != '/':
                output_prefix = '/' + output_prefix
        else:
            output_prefix = '/'
        self.__output_prefix = output_prefix

    def get_output_directory(self):
        """Retrieve output directory."""
        if not self.__output_directory_exists:
            self.__output_directory_exists = _ensure_dir_existence(self.__output_directory)
        return self.__output_directory

    def get_output_prefix(self):
        """Retrieve output prefix."""
        return self.__output_prefix

    def __get_search_text(self, formula_type, formula, color, scale):
        """Get internal search text for combination of formula type, formula, color and scale."""
        typeStr = str(formula_type)
        if isinstance(formula_type, (tuple, list)):
            typeStr = str(formula_type[0])
        text = "{0},{1},{2},{3},{4}:{5}".format(typeStr, _convert_color_component(color[0]), _convert_color_component(color[1]), _convert_color_component(color[2]), int(100 * scale), formula.strip())
        return text

    def __get_database_file(self):
        """Get filename of formula filename database."""
        return os.path.join(self.__cache_directory, "formulae.db.json")

    def __create_empty_database(Self):
        """Get empty formula filename database."""
        return dict(), set()

    def __read_database(self):
        """Read formula filename database. Always returns something valid."""
        if self.__cache_directory is None:
            return self.__create_empty_database()
        if not self.__cache_directory_exists:
            self.__cache_directory_exists = _ensure_dir_existence(self.__cache_directory)
        try:
            with open(self.__get_database_file(), "rb") as file:
                result = json.loads(file.read().decode('utf-8'))
            if type(result) != list or len(result) != 2 or type(result[0]) != dict or type(result[1]) != list:
                raise Exception("Read database invalid!")
            result[1] = set(result[1])
            return result
        except Exception as e:
            _LOGGER.warn("Error on reading formulae database: {}".format(e))
            return self.__create_empty_database()

    def __write_database(self, db):
        """Write formula filename database to cache."""
        if self.__cache_directory is None:
            return
        if not self.__cache_directory_exists:
            self.__cache_directory_exists = _ensure_dir_existence(self.__cache_directory)
        try:
            new_db = [db[0], sorted(list(db[1]))]
            with open(self.__get_database_file(), "wb") as file:
                file.write(json.dumps(new_db, sort_keys=True).encode('utf-8'))
        except Exception as e:
            _LOGGER.warn("Error on writing formulae database: {}".format(e))

    def get_base_name(self, formula_type, formula, color, scale):
        """Get base name for formula with given formula type, color and scale."""
        searchText = self.__get_search_text(formula_type, formula, color, scale)
        with self.__internal_lock:
            if self.__database is None:
                self.__database = self.__read_database()
            if searchText in self.__database[0]:
                return self.__database[0][searchText]
            else:
                base_name = hashlib.sha224(searchText.encode(encoding="UTF-8", errors="replace")).digest()
                base_name = str(base64.b64encode(base_name, altchars=b"_."), "UTF-8")[:-2]  # substring gets rid of final '=='
                suffix = ""
                counter = -1
                while base_name + suffix in self.__database[1]:
                    counter += 1
                    suffix = "-{0}".format(counter)
                base_name += suffix
                self.__database[1].add(base_name)
                self.__database[0][searchText] = base_name
                self.__write_database(self.__database)
                return base_name

    def get_base_names(self, formula_color_scale_formula_type_list):
        """Get base name for formula with given formula type, color and scale."""
        result = []
        changed = False
        with self.__internal_lock:
            if self.__database is None:
                self.__database = self.__read_database()
            for (formula, color, scale, formula_type) in formula_color_scale_formula_type_list:
                searchText = self.__get_search_text(formula_type, formula, color, scale)
                if searchText in self.__database[0]:
                    result.append(self.__database[0][searchText])
                else:
                    base_name = hashlib.sha224(searchText.encode(encoding="UTF-8", errors="replace")).digest()
                    base_name = str(base64.b64encode(base_name, altchars=b"_."), "UTF-8")[:-2]  # substring gets rid of final '=='
                    suffix = ""
                    counter = -1
                    while base_name + suffix in self.__database[1]:
                        counter += 1
                        suffix = "-{0}".format(counter)
                    base_name += suffix
                    self.__database[1].add(base_name)
                    self.__database[0][searchText] = base_name
                    changed = True
                    result.append(base_name)
            if changed:
                self.__write_database(self.__database)
        return result

    # Content cache

    def get_content_from_cache(self, base_name):
        """Retrieve content from cache. Returns None if base_name wasn't cached."""
        if self.__cache_directory is None:
            return None
        fn = os.path.join(self.__cache_directory, base_name)
        try:
            with open(fn, "rb") as file:
                return file.read()
        except Exception:
            return None

    def put_content_into_cache(self, base_name, content):
        """Put the content in the cache under base_name.

        Returns True if storing was successful and data can be retrieved
        with get_content_from_cache().
        """
        if self.__cache_directory is None:
            return False
        if not self.__cache_directory_exists:
            self.__cache_directory_exists = _ensure_dir_existence(self.__cache_directory)
        fn = os.path.join(self.__cache_directory, base_name)
        try:
            with open(fn, "wb") as file:
                file.write(content)
                return True
        except Exception as e:
            _LOGGER.warn("Cannot store content into cache file {0}: {1}".format(fn, e))
            try:
                os.remove(fn)
            except Exception:
                pass
            return False


class LaTeXFormulaRenderer(object):
    """Abstracts the process of converting a formula to an image file."""

    def __init__(self, additional_preamble={}):
        """Create an LaTeXFormulaRenderer object. Additional preambles can be specified."""
        super(LaTeXFormulaRenderer, self).__init__()
        self.__additional_preamble = additional_preamble

    # -----------------------------------------------------------------------
    # Creating .tex files

    def _get_LaTeX_header(self, color, withXY, withTikz, withPStricks, latex_mode):
        """Compose header contents for the .tex file."""
        LaTeX_header = ''

        def _clamp_color_frac(float):
            return _convert_color_component(float) / 255.0

        if withTikz:
            LaTeX_header += r'\usepackage{tikz,pgffor}' + "\n"

        if withPStricks:
            LaTeX_header += r'\usepackage{pstricks}' + "\n"

        if withXY:
            LaTeX_header += r'\usepackage{xypic}' + "\n"

        LaTeX_header += r'''
\pagestyle{empty}
\definecolor{mycolor}{rgb}{''' + '{0} {1} {2}'.format(_clamp_color_frac(color[0]), _clamp_color_frac(color[1]), _clamp_color_frac(color[2])) + r'''}
'''
        indices = ['', latex_mode]
        if withTikz:
            indices.append('tikz')
        if withPStricks:
            indices.append('pstricks')
        if withXY:
            indices.append('xy')
        for idx in indices:
            if idx in self.__additional_preamble and len(self.__additional_preamble[idx]) > 0:
                LaTeX_header += r'''
% Additional preamble ('{0}')
{1}
'''.format(idx, self.__additional_preamble[idx])
        return LaTeX_header

    def _get_form_head_tail(self, formula_type):
        """Generate prefix and suffix to wrap formula in when putting it into the LaTeX document."""
        if formula_type == 'inline':
            form_head = r'\('
            form_tail = r'\)'
        elif formula_type == 'display':
            form_head = r'\['
            form_tail = r'\]'
        elif formula_type == 'align':
            form_head = r'\begin{align*}'
            form_tail = r'\end{align*}'
        elif isinstance(formula_type, (tuple, list)) and formula_type[0] == 'tikzpicture':
            form_head = r'\begin{tikzpicture}'
            if formula_type[1] is not None:
                form_head += '[' + formula_type[1] + ']'
            form_head += '\n'
            form_tail = '\n' + r'\end{tikzpicture}'
        elif isinstance(formula_type, (tuple, list)) and formula_type[0] == 'pstricks':
            atts = formula_type[1]
            width = float(atts['right']) - float(atts['left'])
            height = float(atts['top']) - float(atts['bottom'])
            form_head = r"\setlength{\unitlength}{" + atts['unit'] + r"}\psset{unit=" + atts['unit'] + "}\n"
            form_head += r"\begin{picture}(" + str(width) + "," + str(height) + ")(0,0)\n"
            form_head += r"\put(0,0){\white\line(1,0){" + str(width / 1000.0) + "}}\n"
            form_head += r"\put(" + str(width) + "," + str(height) + r"){\white\line(-1,0){" + str(width / 1000.0) + "}}\n"
            form_head += r"\put(0,0){\begin{pspicture}(" + atts['left'] + "," + atts['bottom'] + ")(" + atts['right'] + "," + atts['top'] + ")\n"
            form_tail = "\n" + r"\end{pspicture}}\end{picture}"
        else:
            raise ""
        return form_head, form_tail

    def _needs_XY(self, formula):
        """Check whether the formula requires XY-Pic."""
        return formula.find(r'\xymatrix') >= 0

    def _create_TeX_file_PDF_standalone(self, formula, color, formula_type):
        """Create .tex file for processing with pdflatex (to create .pdf file)."""
        head = r'''\documentclass{standalone}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{xcolor}
    ''' + self._get_LaTeX_header(color, self._needs_XY(formula), isinstance(formula_type, (tuple, list)) and formula_type[0] == 'tikzpicture', False, 'pdflatex') + r'''
\begin{document}
  \color{mycolor}
    '''
        tail = r'\end{document}' + '\n'
        form_head, form_tail = self._get_form_head_tail(formula_type)
        return head + form_head + formula + form_tail + tail

    def _create_TeX_file_DVI(self, formula, color, formula_type):
        """Create .tex file for processing with latex (to create .dvi file)."""
        head = r'''\documentclass{article}
    \usepackage[left=0cm,right=0cm,top=0cm,bottom=0cm,landscape,a0paper]{geometry}
    \usepackage[utf8]{inputenc}
    \usepackage[T1]{fontenc}
    \usepackage{xcolor}
    ''' + self._get_LaTeX_header(color, self._needs_XY(formula), False, isinstance(formula_type, (tuple, list)) and formula_type[0] == 'pstricks', 'latex') + r'''
    \begin{document}
      \color{mycolor}
    '''
        tail = r'\end{document}' + '\n'
        form_head, form_tail = self._get_form_head_tail(formula_type)
        return head + form_head + formula + form_tail + tail

    # -----------------------------------------------------------------------
    # Running LaTeX on .tex files

    def _run_latex(self, tempfn, tempdir, base_name, content, program):
        """Execute LaTeX CLI on the file's content by writing it into the given temporary directory."""
        with open(tempfn, "w") as file:
            file.write(content)
        p = subprocess.Popen([program, '--halt-on-error', '-interaction', 'nonstopmode', '-no-shell-escape', '-output-directory', tempdir, "-jobname", base_name, tempfn], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = p.communicate('')
        ret_code = p.returncode
        if ret_code != 0:
            raise LaTeXError("Error {0} on running formula through LaTeX ({1})! LaTeX file:\n{3}\n{2}\n{3}\nLaTeX output (stdout):\n{3}\n{4}\n{3}\nLaTeX error output (stderr):\n{3}\n{5}\n{3}".format(ret_code, program, content, '-' * 79, str(output, 'utf-8'), str(error, 'utf-8')), ret_code)

    def _render_formula_PDF_standalone(self, formula, formula_type, color, scale, base_name, tempdir, tempfn):
        """Render the formula as a PDF file."""
        pdffn = os.path.join(tempdir, base_name + ".pdf")
        self._run_latex(tempfn, tempdir, base_name, self._create_TeX_file_PDF_standalone(formula, color, formula_type), 'pdflatex')
        return 'pdf', pdffn

    def _render_formula_DVI(self, formula, formula_type, color, scale, base_name, tempdir, tempfn):
        """Render the formula as a DVI file."""
        dvifn = os.path.join(tempdir, base_name + ".dvi")
        self._run_latex(tempfn, tempdir, base_name, self._create_TeX_file_DVI(formula, color, formula_type), 'latex')
        return 'dvi', dvifn

    def _render_formula_DVIPS(self, formula, formula_type, color, scale, base_name, tempdir, tempfn):
        """Render the formula as an EPS file."""
        dvifn = os.path.join(tempdir, base_name + ".dvi")
        epsfn = os.path.join(tempdir, base_name + ".eps")
        self._run_latex(tempfn, tempdir, base_name, self._create_TeX_file_DVI(formula, color, formula_type), 'latex')
        ret_code = subprocess.call(['dvips', dvifn, '-E', '-o', epsfn], shell=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if ret_code != 0:
            raise LaTeXError("Cannot convert DVI file to PS file!", ret_code)
        return 'eps', epsfn

    # -----------------------------------------------------------------------
    # Conversion to output format

    def _convert_to_png(self, tempdir, base_name, intermediate_format, intermediate_file, scale):
        """Convert intermediate format to PNG."""
        pngfn = os.path.join(tempdir, base_name + ".png")
        # Convert to PNG
        if intermediate_format == 'pdf':
            ret_code = subprocess.call(['convert', '-density', str(int(100 * scale)), intermediate_file, pngfn], shell=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if ret_code != 0:
                raise LaTeXError("Cannot convert PDF file to PNG file!", ret_code)
        elif intermediate_format == 'eps' or intermediate_format == 'ps':
            ret_code = subprocess.call(['convert', intermediate_file, '-density', str(int(100 * scale)), pngfn], shell=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if ret_code != 0:
                raise LaTeXError("Cannot convert PS file to PNG file!", ret_code)
        elif intermediate_format == 'dvi':
            ret_code = subprocess.call(['dvipng', intermediate_file, '-bg', 'Transparent', '-T', 'tight', '-D', str(int(100 * scale)), '-z', '9', '-o', pngfn], shell=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if ret_code != 0:
                raise LaTeXError("Cannot convert DVI file to PNG file!", ret_code)
        # Optimize PNG
        subprocess.call(['optipng', '-o7', '-zm1-9', pngfn], shell=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # Read result
        with open(pngfn, "rb") as file:
            data = file.read()
        return data

    def _convert_to_svg(self, tempdir, base_name, intermediate_format, intermediate_file, scale, compress=False):
        """Convert intermediate format to (compressed or uncompressed) SVG."""
        svgfn = os.path.join(tempdir, base_name + ".svg")
        svgzfn = os.path.join(tempdir, base_name + ".svgz")
        # Convert to SVG
        if intermediate_format == 'pdf':
            pdftmpfn = os.path.join(tempdir, base_name + ".tmp.pdf")
            ret_code = subprocess.call(['gs', '-o', pdftmpfn, '-dNoOutputFonts', '-sDEVICE=pdfwrite', intermediate_file], shell=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if ret_code != 0:
                raise LaTeXError("Cannot convert text in PDF file to outlines!", ret_code)
            ret_code = subprocess.call(['pdf2svg', pdftmpfn, svgfn], shell=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if ret_code != 0:
                raise LaTeXError("Cannot convert PDF file to SVG file!", ret_code)
            if compress:
                ret_code = subprocess.call(['gzip', '-S', 'z', svgfn], shell=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if ret_code != 0:
                    raise LaTeXError("Cannot compress SVG file!", ret_code)
        elif intermediate_format == 'eps' or intermediate_format == 'ps':
            compress_option = ['-z'] if compress else []
            ret_code = subprocess.call(['dvisvgm', '-n', '-E', intermediate_file, '-o', svgzfn if compress else svgfn] + compress_option, shell=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if ret_code != 0:
                raise LaTeXError("Cannot convert PS file to SVG file!", ret_code)
        elif intermediate_format == 'dvi':
            compress_option = ['-z'] if compress else []
            ret_code = subprocess.call(['dvisvgm', '-n', intermediate_file, '-o', svgzfn if compress else svgfn] + compress_option, shell=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if ret_code != 0:
                raise LaTeXError("Cannot convert DVI file to SVG file!", ret_code)
        # Read result
        with open(svgzfn if compress else svgfn, "rb") as file:
            data = file.read()
        return data

    # -----------------------------------------------------------------------
    # Main rendering function

    def render_formula(self, formula, formula_type, color, scale, base_name, output_format):
        """Render formula as image.

        formula, formula_type, color and scale must be as described in the docstring
        of LaTeXFormulaRendererPlugin (see below).

        base_name must be a file-system friendly string, and output_format must be one
        of "png", "svg" and "svgz".

        Returns the formula as a byte array.
        """
        if isinstance(formula_type, (tuple, list)):
            formula_type_name = formula_type[0]
        else:
            formula_type_name = formula_type
        _LOGGER.info("Converting formula {0}({1}): '{2}'".format(base_name, formula_type_name, formula))
        tempdir = tempfile.mkdtemp()
        try:
            tempfn = os.path.join(tempdir, base_name + ".tex")
            # First step: convert to PDF, DVI or PS
            if formula_type_name in {'align', 'display'}:
                intermediate_format, intermediate_file = self._render_formula_DVI(formula, formula_type, color, scale, base_name, tempdir, tempfn)
            elif formula_type_name == 'pstricks':
                intermediate_format, intermediate_file = self._render_formula_DVIPS(formula, formula_type, color, scale, base_name, tempdir, tempfn)
            elif formula_type_name in {'inline', 'tikzpicture'}:
                intermediate_format, intermediate_file = self._render_formula_PDF_standalone(formula, formula_type, color, scale, base_name, tempdir, tempfn)
            else:
                raise LaTeXError("Unknown formula type '{}'!".format(formula_type_name))
            # Second step: convert to format
            if output_format == 'png':
                return self._convert_to_png(tempdir, base_name, intermediate_format, intermediate_file, scale)
            elif output_format == 'svg':
                return self._convert_to_svg(tempdir, base_name, intermediate_format, intermediate_file, scale, compress=False)
            elif output_format == 'svgz':
                return self._convert_to_svg(tempdir, base_name, intermediate_format, intermediate_file, scale, compress=True)
            else:
                raise Exception("Unknown output format '{}'!".format(output_format))
        finally:
            shutil.rmtree(tempdir, True)


class MemoryFile:
    """Turns a bytes array into a read-only file."""

    def __init__(self, data):
        """Create memory file."""
        self.__data = data
        self.__pos = 0

    def tell(self):
        """Get position in file."""
        return self.__pos

    def seek(self, offset, whence=os.SEEK_SET):
        """Set position in file."""
        if whence == os.SEEK_SET:
            self.__pos = offset
        elif whence == os.SEEK_CUR:
            self.__pos += offset
        elif whence == os.SEEK_END:
            self.__pos = len(self.__data) + offset
        else:
            raise IOError("Invalid 'whence' for seek()")
        if self.__pos < 0:
            self.__pos = 0
        if self.__pos > len(self.__data):
            self.__pos = len(self.__data)

    def read(self, size=-1):
        """Read bytes from file."""
        if size < 0 or self.__pos + size > len(self.__data):
            size = len(self.__data) - self.__pos
        result = self.__data[self.__pos:self.__pos + size]
        self.__pos += size
        return result


def _parse_svg_unit_as_pixels(unit):
    """Parse a unit from a SVG file."""
    if unit.endswith('pt'):
        value = float(unit[:-2])
        # Magic value which seems to works fine for what pdf2svg and dvisvgm outputs
        return round(value * 1.777778)
    else:
        # Looks like we need no other unit for output of pdf2svg and dvisvgm
        raise Exception('Cannot interpret SVG unit "{0}"!'.format(unit))


def _get_image_size_from_memory(data, output_format):
    """Return a tuple (width, height) for the image of format output_format stored in the byte array data."""
    if output_format == 'png':
        # We use PIL
        with Image.open(MemoryFile(data)) as img:
            result = img.size
        return result
    elif output_format == 'svg':
        # We use ElementTree to parse the SVG as XML
        e = xml.etree.ElementTree.fromstring(data)
        return _parse_svg_unit_as_pixels(e.get('width')), _parse_svg_unit_as_pixels(e.get('height'))
    elif output_format == 'svgz':
        # We use ElementTree to parse the decompressed SVG as XML
        f = gzip.GzipFile(fileobj=MemoryFile(data))
        e = xml.etree.ElementTree.parse(f).getroot()
        return _parse_svg_unit_as_pixels(e.get('width')), _parse_svg_unit_as_pixels(e.get('height'))
    else:
        raise Exception('Unknown image format "{0}"!'.format(output_format))


def _make_data_URI(data, output_format):
    """Convert the image with format output_format given as a byte array to a data URI."""
    media_type = None
    if output_format == 'png':
        media_type = 'image/png'
    elif output_format == 'svg' or format == 'svgz':
        media_type = 'image/svg+xml'
    else:
        raise Exception('Unknown image format "{0}"!'.format(output_format))
    return 'data:{0};base64,{1}'.format(media_type, str(base64.standard_b64encode(data), "UTF-8"))


def _sanitizeName(name):
    """Convert formula base_name to something safer."""
    result = ''
    for c in name:
        if c >= 'a' and c <= 'z':
            result += c
        elif c >= 'A' and c <= 'Z':
            result += c
        elif c >= '0' and c <= '9':
            result += c
        else:
            result += '_'
    return result


class LaTeXFormulaRendererPlugin(Task):
    r"""Provide a LaTeX formula rendering infrastructure.

    Users of this plugin can ask it to render a formula as a graphics,
    either as a relative URL or as a HTML fragment displaying the
    result, and ensure by registering formula collectors that the
    graphics will be generated by doit tasks and thus do not show up
    when running ``nikola orphans`` or ``nikola check -f``.

    To register a formula collector, a plugin should add a function
    ``formula_collector`` to ``site.latex_formula_collectors``. Care
    must be taken to ensure that ``site.latex_formula_collectors`` is
    set to an empty list before trying to add it if it doesn't exist
    yet, as it can be that the LaTeX formula rendering plugin will be
    initialized after the plugin trying to use it. This can be
    achieved as follows::

        if not hasattr(site, 'latex_formula_collectors'):
            site.latex_formula_collectors = []
        site.latex_formula_collectors.append(self.formula_collector)

    The LaTeX formula renderer will call the function ``formula_collector``
    somewhen after ``scan_posts`` has been run. It has to return a list
    of tuples ``(formula, color, scale, formula_type)``.

    Here, ``formula`` is a LaTeX-style formula, i.e. everything between
    two ``$``, two ``$$``, between ``\(`` and ``\)``, between ``\[`` and
    ``\]``, etc., depending on what ``formula_type`` is.

    ``formula_type`` can be one of:

      * ``"inline"`` (standard inline formula);
      * ``"display"`` (standard display-style formula);
      * ``"align"`` (formula in an ``align*`` environment);
      * ``("pstricks", xx)`` (for content in a ``tikzpicture`` environment),
        with ``xx`` either being ``None`` or the content of the argument to
        the ``tikzpicture`` environment;
      * ``("tikzpicure", { "left": xx, "right": xx, "top": xx, "bottom": xx, "unit": yy })``
        where ``xx`` are numbers and yy is a string (content in an
        ``pstricks`` environment).

    ``color`` is a tuple of three numbers between 0 and 1, specifying
    the red, green and blue components of the color, with ``(0, 0, 0)``
    being black and ``(1, 1, 1)`` being white.

    ``scale`` is a positive number which determines the size of the
    output.

    Finally, to directly render a formula, you can access this plugin
    via ``site.latex_formula_renderer`` as soon as all ``Task`` plugins
    are initialized by calling their ``set_site`` functions (check out
    ``nikola.py`` to find out when that is precisely). The plugin provides
    two public APIs:
     * ``compile(self, formula, color, scale, formula_type='inline')``:
       compiles the formula and returns a URL for it;
     * ``render(self, formula, color, scale, formula_type='inline')``:
       compiles the formula and returns an HTML fragment which displays
       the formula.
    """

    name = 'latex_formula_renderer'

    def set_site(self, site):
        """Set site, which is a Nikola instance."""
        super(LaTeXFormulaRendererPlugin, self).set_site(site)

        self.__formula_cache = FormulaCache()
        self.__formula_cache.set_cache_directory(os.path.join(site.config['CACHE_FOLDER'], 'formulae'))
        formula_folder = site.config.get('LATEX_FORMULA_FOLDER', 'formulae')
        self.__formula_cache.set_output_prefix(formula_folder)
        self.__formula_cache.set_output_directory(os.path.join(site.config['OUTPUT_FOLDER'], formula_folder.strip('/')))
        self.__formula_as_data_URIs = site.config.get('LATEX_FORMULA_AS_DATAURI', False)
        self.__output_format = site.config.get('LATEX_FORMULA_OUTPUT_FORMAT', 'png')
        self.__formula_additional_preamble = site.config.get('LATEX_FORMULA_ADDITIONAL_PREAMBLE', {})
        if not isinstance(self.__formula_additional_preamble, dict):
            self.__formula_additional_preamble = {'': self.__formula_additional_preamble}

        if not hasattr(site, 'latex_formula_collectors'):
            site.latex_formula_collectors = []

        site.latex_formula_renderer = self

    def _generate_formula(self, base_name, formula, formula_type, color, scale):
        """Make sure formula is generated and cached under base_name.

        If it is already cached, the cached value will be used.
        """
        extension = ".{0}".format(self.__output_format)
        data = self.__formula_cache.get_content_from_cache(base_name + extension)
        if data is None:
            renderer = LaTeXFormulaRenderer(self.__formula_additional_preamble)
            data = renderer.render_formula(formula, formula_type, color, scale, _sanitizeName(base_name), self.__output_format)
            self.__formula_cache.put_content_into_cache(base_name + extension, data)
        return data

    def _write_formula(self, data, base_name, extension, formula, formula_type, color, scale):
        """Write formula into output directory."""
        file_name = os.path.join(self.__formula_cache.get_output_directory(), base_name + extension)
        with open(file_name, "wb") as file:
            file.write(data)

    def compile(self, formula, color, scale, formula_type='inline'):
        """Compile formula and return URL for it.

        If data URIs are requested, no output files will be generated.
        Otherwise, the formula will be stored in the output directory.

        For a description of the values of ``formula``, ``color``,
        ``scale`` and ``formula_type``, please refer to the docstring
        of ``LaTeXFormulaRendererPlugin``.
        """
        extension = ".{0}".format(self.__output_format)
        base_name = self.__formula_cache.get_base_name(formula_type, formula, color, scale)
        data = self._generate_formula(base_name, formula, formula_type, color, scale)
        width, height = _get_image_size_from_memory(data, self.__output_format)
        if self.__formula_as_data_URIs:
            return self._make_data_URI(data, self.__output_format), width, height
        else:
            self._write_formula(data, base_name, extension, formula, formula_type, color, scale)
            return '{0}{1}{2}'.format(self.__formula_cache.get_output_prefix(), base_name, extension), width, height

    def _copy_formula(self, base_name, extension, formula, color, scale, formula_type):
        """Make sure that formula is stored in output directory."""
        data = self._generate_formula(base_name, formula, formula_type, color, scale)
        self._write_formula(data, base_name, extension, formula, formula_type, color, scale)

    def render(self, formula, color, scale, formula_type='inline'):
        """Compile formula and return HTML fragment displaying it.

        Prepare for a large return value in case data URIs are requested.

        For a description of the values of ``formula``, ``color``,
        ``scale`` and ``formula_type``, please refer to the docstring
        of ``LaTeXFormulaRendererPlugin``.
        """
        src, width, height = self.compile(formula, formula_type, color, scale)
        if isinstance(formula_type, (tuple, list)):
            css_type = formula_type[0]
        else:
            css_type = formula_type
        return "<img class='img-{0}-formula img-formula' width='{1}' height='{2}' src='{3}' />".format(css_type, width, height, src)

    def gen_tasks(self):
        """Generate doit tasks."""
        yield self.group_task()
        # Do we have something to do?
        if not self.__formula_as_data_URIs:
            # Make sure we have all posts scanned and can safely query the formula collectors
            self.site.scan_posts()
            formulae = []
            # Process all formula collectors
            for formula_collector in self.site.latex_formula_collectors:
                # Get formulae
                formulae.extend(formula_collector())
            if len(formulae) == 0:
                return
            # Remove obvious duplicates
            last = None
            s = sorted(formulae)
            formulae = []
            for f in s:
                if f == last:
                    continue
                last = f
                formulae.append(last)
            # Get base names for list of formulae
            base_names = self.__formula_cache.get_base_names(formulae)
            # Generate tasks
            extension = ".{0}".format(self.__output_format)
            generated = set()
            for base_name, (formula, color, scale, formula_type) in zip(base_names, formulae):
                destination = os.path.normpath(os.path.join(self.__formula_cache.get_output_directory(), base_name + extension))
                if destination not in generated:
                    generated.add(destination)
                    task = {
                        'basename': self.name,
                        'name': destination,
                        'file_dep': [],
                        'targets': [destination],
                        'actions': [(self._copy_formula, [base_name, extension, formula, color, scale, formula_type])],
                        'clean': True,
                        'uptodate': [utils.config_changed({0: formula, 1: color, 2: scale, 3: formula_type})]
                    }
                    yield task
