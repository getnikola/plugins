The idea of MetaTemplate plugin is, as a final user, be able to create
simple HTML templates to be included in your posts/stories without
having to program anything in Python.

You only have to add a simple `.tmpl` file in the
`meta_template/templates/mako` folder with the content you want and
using variables to be replaced with the information you will pass in
the reStructuredText directive. Let's see an example of it.

This is the reStructuredText you will need to put in your post to get
a Bootstrap3 simple button:

```
.. template:: bootstrap3/button
   :href: http://elblogdehumitos.com.ar/

   Go to my blog
```

You will also need to put the file `button.tmpl` in the folder
`meta_template/templates/mako` with this content:

```
## -*- coding: utf-8 -*-

<div style="${style or 'text-align: center; margin-top: 25px; margin-bottom: 25px;'}">
  <a class="btn btn-lg btn-primary" target="${target or '_blank'}" href="${href}">
    ${'\n'.join(content)}
  </a>
</div>
```

Finally, you will get the button as you expect. Easy. Doesn't it?

Feel free to send your pull request to collaborate with more templates
or supported options :)
