This plugin converts [PlantUML](https://plantuml.com/) files.

The default configuration will output all `*.puml` files found under the `pages` dir as SVG files.

Developed against PlantUML version 1.2020.24.  Probably works with some earlier versions.

# Unicode

The plugin expects PlantUML files to be encoded with UTF-8.

# Known Issues

- It's slow!  Every PlantUML rendering launches a new Java process, on my laptop it takes 4-8 seconds per file.
  I have some ideas to speed this up, and they may be available in future plugin versions.

- Changes to files included via `!include ...` or via a pattern (e.g. `-Ipath/to/*.iuml`) will NOT trigger a rebuild.
  Instead, if you include them explicitly in `PLANTUML_ARGS` (e.g. `-Ipath/to/foo.iuml`) then they will trigger a
  rebuild.

- `nikola auto` does not watch dirs in `PLANTUML_FILES` or files included via `PLANTUML_ARGS` / `!include`.
  As a workaround you could put PlantUML files under any dir listed in `POSTS` or `PAGES` because those dirs
  are watched.
  (Use `.iuml` suffix for include files to prevent them matching the `*.puml` wildcard in `PLANTUML_FILES`)

- If your file does not begin with `@start` then PlantUML prepends a line containing `@startuml` which causes 
  the line number in error messages to be one higher than the actual error location.

- The file name in PlantUML error messages is always `string` rather than the actual problem file.
  PlantUML does this when input is piped via stdin, which as a compromise for simplicity we always do.
  