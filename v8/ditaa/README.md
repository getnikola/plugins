# Ditaa plugin

Create diagrams (using ASCII art and render them to PNG or SVG using ditaa with
this ReST directive.

[ditaa](https://github.com/stathissideris/ditaa/) is a neat tool that takes
diagrams like this:

```
    +-----------+        +---------+
    |    PLC    |        |         |
    |  Network  +<------>+   PLC   +<---=---------+
    |    cRED   |        |  c707   |              |
    +-----------+        +----+----+              |
                              ^                   |
                              |                   |
                              |  +----------------|-----------------+
                              |  |                |                 |
                              v  v                v                 v
      +----------+       +----+--+--+      +-------+---+      +-----+-----+       Windows clients
      |          |       |          |      |           |      |           |      +----+      +----+
      | Database +<----->+  Shared  +<---->+ Executive +<-=-->+ Operator  +<---->|cYEL| . . .|cYEL|
      |   c707   |       |  Memory  |      |   c707    |      | Server    |      |    |      |    |
      +--+----+--+       |{d} cGRE  |      +------+----+      |   c707    |      +----+      +----+
         ^    ^          +----------+             ^           +-------+---+
         |    |                                   |
         |    +--------=--------------------------+
         v
+--------+--------+
|                 |
| Millwide System |            -------- Data ---------
| cBLU            |            --=----- Signals ---=--
+-----------------+

```

And produces this:

![example](https://raw.githubusercontent.com/getnikola/plugins/master/v8/ditaa/ditaa-example.svg)

(Thanks to https://github.com/changcs/ditaa-examples for this example)

This plugin provides a directive for reStructuredText that allows you to embed
the ASCII art diagram directly in your post, calling ditaa for you and inserting
the `<img>` tag.

## Dependencies

You need ditaa installed on your PATH.

## Configuration

* `DITAA_OUTPUT_FOLDER`: the folder where ditaa should put the images it
  generates. e.g. `'files/images/ditaa'`

* `DITAA_OUTPUT_URL_PATH`: the final URL path that corresponds to the above
  folder, which will be used in the generated HTML. e.g. `'/images/ditaa'`

In general you have two choices for `DITAA_OUTPUT_FOLDER`. You can make it a
folder that is part of your normal source files (usually these are under version
control), as above, or you could put under your `OUTPUT_PATH` (which usually is
not under version control). The former is recommended as being safer — you’ll
still have your images even if you stop having a functioning ditaa installation.

## Syntax

Example usage looks like this:

```
.. ditaa::
   :cmdline: --scale 1 --no-separation --svg
   :filename: my_diagram.svg
   :class: my-css-class
   :alt: A cool diagram

   /-----------------+
   | My cool diagram |
   +-----------------/

```

* `cmdline`: a space separated list of options to pass to the ditaa executable.
  See the [ditaa
  docs](https://github.com/stathissideris/ditaa/#usage-and-syntax) for details
  on what can be passed.

* `filename`: the filename of the image that will be generated. You are
  responsible for ensuring that it doesn’t clash with other diagrams you may
  have — existing files will be overwritten without warning.

  If desired, you can use the text `{checksum}` as part of the filename and it
  will be replaced with a hash of the ASCII contents of the diagram, which will
  help to ensure uniqueness and avoid name clashes. However, this will then
  generate a differently named file each time you change the contents, and
  you’ll need to do any cleanup on old copies of the diagram that you don’t
  want.

* `class`: a space separated list of class names that will be added to the
  `class` attribute of the generated `<img>`.

* `alt`: alternate text for the image, like with the `image` directive.


## Tips

* If you are an Emacs user, check out the `picture-mode` for drawing
  ASCII art diagrams.

