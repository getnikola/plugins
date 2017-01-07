Extra Plugins for Nikola
========================

The source repository of <https://plugins.getnikola.com/> — Plugins for the Nikola static site generator.

## How to get your Plugin to the Index

1. Follow the Developer Documentation closely.
2. Fork this repository and put your plugin there.
3. Send a Pull Request.
   
   **Note:** even if you have commit rights (shared with Nikola or from another plugin you posted), please send a Pull Request.  The admins have to do some tasks (add an Issue label; add you to the Plugin Creators group) they might forget about if you do not do this.  (oh, and code review, too)

4. Success!  Your plugin is in the Index.
   Please note that it will appear on the website at midnight UTC, when the site is automatically rebuilt.


## Developer Documentation

Anyone can develop plugins for Nikola.  There are some specific files you need if you want them on the Index, though.

There is also a sample `helloworld` plugin available.

### `README.md`

A [Markdown](http://daringfireball.net/projects/markdown/)-formatted file, describing your plugin, what it does, and how it works.

(those files are rendered locally, and this is why we aren’t using reST, which is a de-facto standard in the Python and Nikola community.)

### `requirements.txt` and `requirements-nonpy.txt` (optional)

If your plugin depends on something else, you need to add it to one of those two files.

If your dependency is a Python package, put it in the `requirements.txt` file, which is then passed over to `pip` while installing your plugin.  Inserting Nikola’s dependencies you also depend on is not mandatory, but suggested just in case those are not our dependencies anymore.

If you depend on a third-party piece of software that is not a Python package installable via `pip`, you need to provide a `requirements-nonpy.txt` file.  The format is `Human-friendly name::http://download/link`.  It will be shown in the Plugins index, and shown to the user while installing.

### `conf.py.sample` (optional)

If there are any config options you need for your plugin, put them here.

### `[plugin name].plugin`

This is a standard ConfigParser-style ini file.  It is parsed by yapsy and the Plugin Index.

```ini
[Core]
Name = plugin-name
Module = plugin-name
Tests = test-suite

[Nikola]
MinVersion = version-number
MaxVersion = version-number
Compiler = compiler-that-uses-extensions
plugincategory = plugin-category

[Documentation]
Author = authors-name
Version = version-number
Website = https://plugins.getnikola.com/#plugin-name
Description = A short, one-line description
```

#### `[Core]`

In `[Core]`, you need to provide the `Name` of your plugin and the `Module` your plugin resides in.  We recommend to have them identical (just like the directory name and the name of this very config file).

**Additional fields:** If you have tests, put it in the `/tests/` directory of this repository (*not your plugin!*) and put the test module name in a `Tests` field.  Tests in `/tests/` are run by Travis CI.  **Note that the Travis CI test runner does not interpret `requirements-nonpy.txt` files!**

#### `[Nikola]`

If you require a specific version of Nikola, set `MinVersion` and `MaxVersion` accordingly.  Those fields are not mandatory.

If the plugin is a compiler extension, you need to set the `Compiler` here.  Otherwise, skip this field.

The `plugincategory` field is mandatory, and it must contain the plugin category.
Use 'Compiler' for compilers and the base class name for anything else.

#### `[Documentation]`

In which you need to put in the `Author`, `Version`, `Website` (of the plugin; you can just use the link to the Index as shown in the example; replacing `plugin-name` with the obvious thing) and a short `Description`.


### `[plugin name].py`

This is where your plugin resides.  [Follow the *Extending Nikola* tutorial for instructions on how to write a plugin.](https://getnikola.com/extending.html)
