Compile [SASS](http://sass-lang.com/) source files into CSS.

To use this plugin:

Create a `sass` folder in your theme, put your `.scss` files there, add a `sass/targets` file listing the files you
want compiled.

Also don't forget to set the right SASS compiler, usually the most used was `sass` installed with `ruby-sass` but is now deprecated basically everywhere. Instead `sassc` it is the new one (and it is compatible) so you can use both, set the chosen one with the conf.py parameter `SASS_COMPILER`.

Note: in some cases, you might have to run `nikola build` twice.
