Extra Plugins for Nikola
========================

The source repository of <http://plugins.getnikola.com/> — Plugins for the Nikola static site generator.

## Developer Documentation

Anyone can develop plugins for Nikola.  There are some specific files you need.

### `requirements.txt` and `requirements-nonpy.txt`

If your plugin depends on something else, you need to add it to one of those two files.

If your dependency is a Python package, put it in the `requirements.txt` file, which is then passed over to `pip` while installing your plugin.  Inserting Nikola’s dependencies you also depend on is not mandatory, but suggested just in case those are not our dependencies anymore.

If you depend on a third-party piece of software that is not a Python package installable via `pip`, you need to provide a `requirements-nonpy.txt` file.  The format is `Human-friendly name::http://download/link`.  It will be shown in the Plugins index, and shown to the user while installing.

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

[Documentation]
Author = authors-name
Version = version-number
Website = http://plugins.getnikola.com/#plugin-name
Description = A short, one-line description
```

#### `[Core]`

In `[Core]`, you need to provide the `Name` of your plugin and the `Module` your plugin resides in.  We recommend to have them identical (just like the directory name and the name of this very config file).

**Additional fields:** If you have tests, put it in the `/tests/` directory of this repository (*not your plugin!*) and put the test module name in a `Tests` field.  Tests in `/tests/` are run by Travis CI.  **Note that the Travis CI test runner does not interpret `requirements-nonpy.txt` fies!**

#### `[Nikola]` (optional)

If you require a specific version of Nikola, set `MinVersion` and `MaxVersion` accordingly.  Neither field is mandatory, and you can even skip this section altogether if you do not need it.

#### `[Documentation]`

In which you need to put in the `Author`, `Version`, `Website` (of the plugin; you can just use the link to the Index as shown in the example; replacing `plugin-name` with the obvious thing) and a short `Description`.


### `[plugin name].py`

This is where your plugin resides.  [Follow the *Extending Nikola* tutorial for instructions on how to write a plugin.](http://getnikola.com/extending.html)
