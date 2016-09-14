This plugin will do a quick and dirty import of your Blogger site.

To use it if you already have a Nikola site:

```
$ nikola plugin -i import_blogger
$ nikola import_blogger your_blogger_dump_file
```

To use it if you don't already have a Nikola site:

```
$ nikola plugin -i import_blogger --user
$ nikola import_blogger your_blogger_dump_file -o output_folder
```

