A quick & dirty reimplementation of the [plot directive](http://matplotlib.org/api/pyplot_api.html#module-matplotlib.pyplot) useful for doing nice plots, and for sphinx compatibility.

**IMPORTANT:** this directive executes arbitrary python code passed as the argument, so it's wildly
insecure. Do not enable this plugin if you are ever building a site with untrusted content.

Differences with the original:

* Context is always reset between plots, the context option *will* produce an error.
* No configuration options whatsoever. 
* It always uses SVG because it's 2015
* the ``include-source`` option is supported but completely ignored

**NOTE:** if you use code inside the directive instead of files, every time you edit it it will
produce different random-named images in ``output/pyplots``. That's probably worth cleaning every once 
in a while.