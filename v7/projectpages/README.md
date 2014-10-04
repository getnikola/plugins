This is a generator of project pages.  It is based on meta fields in story
files.

Why use a plugin?
-----------------

1. So someone can do the thinking for you.
2. So you can just create standardized files and have pretty subpages and
   indexes generated for you.
3. So many things are automated for you.

Usage
-----

1. Create an entry in `PAGES` for a special path, eg.

       ("projects/*.rst", "projects", "project.tmpl")

2. Create a setting named `PROJECT_PATH` pointing at the directory:

       PROJECT_PATH = 'projects'

3. Create project pages in reStructuredText.
4. Optionally create better templates than the ones provided with the plugin.
   The default templates include `project.tmpl`, `project_helper.tmpl` and
   `projects.tmpl`.

The default templates assume you use Bootstrap 3 and [**Font
Awesome**](http://fortawesome.github.io/Font-Awesome) (which is **not**
included in the default Nikola themes).  You can alter the templates to use
glyphicons if you want.

Meta fields
-----------

* **title** — the project name in a human friendly form
* **description** — tagline or short project description
* **link** — main download link (eg. PyPI page)
* **previewimage** — promotional graphics (used in slider and social networks)
* **logo** — project logo (used on the right side of the project page)
* **language** — programming language
* **status** (str/int) — Development Status.  Use your own phrasing, or the
  following numbers to get nice formatting:

    1. Planning
    2. Pre-Alpha
    3. Alpha
    4. Beta
    5. Production/Stable
    6. Mature
    7. Inactive

* **github** — GitHub link
* **bitbucket** — BitBucket link
* **license** — name of the license under which the project
* **role** — your role in the project.  Free-form, sample values include
  *contributor* and *maintainer*.
* **featured** (bool) — show the project above others.
* **hidden** (bool) — hide the project from the listing.
* Also: the **post text** is a full description of the project.  You can put a
  README here.  (Bonus points for using a .meta file for the metadata and a
  symlink to the actual README as the post, assuming you have good READMEs)

**title**, **description**, **status** and one of **link**, **github**,
**bitbucket** are strictly necessary.

Any other fields are not used by default — however, you can modify templates
and include them.  (Or, if you believe they will really useful to the general
public, request addition in the plugins repo.  The author of this plugin wasn’t
very creative when coming up with the list.)
