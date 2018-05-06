Project Pages plugin for Nikola
===============================

This is a generator of project pages.  It is based on meta fields in story
files.

**LIVE DEMO:** <https://chriswarrick.com/projects/>

**SOURCE FILES FOR THE ABOVE:** <https://github.com/Kwpolska/chriswarrick.com/tree/master/projects>

Why use a plugin?
-----------------

1. So someone can do the thinking for you.
2. So you can just create standardized files and have pretty subpages and
   indexes generated for you.
3. So many things are automated for you.

Usage
-----

1. `projects` directory is the default directory for projects.  You can change
   this by setting `PROJECT_PATH` to a different value:

       PROJECT_PATH = 'projects'

2. Create an entry in `PAGES` for your project directory, eg.

       ("projects/*.rst", "projects", "project.tmpl")

3. Create project pages in reStructuredText (or any other supported markup language).
4. Optionally create your own templates (some are provided with the plugin).
   The default templates include `project.tmpl`, `project_helper.tmpl` and
   `projects.tmpl`.

The default templates assume you use Bootstrap 3 and [**Font
Awesome**](http://fortawesome.github.io/Font-Awesome) (which is **not**
included in the default Nikola themes).  You can alter the templates to use
glyphicons if you want.

The plugin generates two files in each language:

* projects/index.html (or whatever `PROJECT_PATH` and `INDEX_FILE` are) — a HTML
  page with a slider and list of projects, from template `projects.tmpl`
* projects/projects.json — a JSON file, dict of `{slug: all meta data}`

Project subpage generation is handled by Nikola’s built-in stories framework.

Meta fields
-----------

* **title** — the project name in a human friendly form
* **description** — tagline or short project description
* **previewimage** — promotional graphics (used in slider and social networks)
* **logo** — project logo (used on the right side of the project page)
* **devstatus** (str/int) — Development Status.  Use your own phrasing, or the
  following numbers to get nice formatting:

    1. Planning
    2. Pre-Alpha
    3. Alpha
    4. Beta
    5. Production/Stable
    6. Mature
    7. Inactive
* **sort** — sorting key, used for determining order.  Defaults to 1, larger numbers
  first.  Falls back to alphabetical sorting by title descending.  *Negative
  numbers not allowed.*
* **link** — link to the project website
* **download** — main download link (eg. PyPI page)
* **github** — GitHub link
* **bitbucket** — BitBucket link
* **bugtracker** — bug tracker link
* **gallery** — screenshot gallery link
* **language** — programming language
* **license** — name of the license under which the project
* **role** — your role in the project.  Free-form, sample values include
  *Contributor* and *Maintainer*
* **status** — ``featured`` to show in the slider, ``private`` to hide from the
  page
* Also: the **post text** is a full description of the project.  You can put a
  README here.  (Bonus points for using a .meta file for the metadata and a
  symlink to the actual README as the post, assuming you have good READMEs)

**title**, **description**, **devstatus** are required.  **previewimage** is needed if
**status: featured** is set.  **date** and **tags** are ignored and not included in the
JSON file.

Any other fields are not used by default — however, you can modify templates
and include them.  (Or, if you believe they will really useful to the general
public, request addition in the plugins repo.  The author of this plugin wasn’t
very creative when coming up with the list.)
