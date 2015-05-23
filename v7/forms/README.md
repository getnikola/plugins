This plugin uses [Alpaca Forms](http://alpacajs.org/) to allow "easy" form creation
in reStructuredText documents.

Here's an example:

```
.. form::

   {
    "schema": {
        "title": "What do you think of Alpaca?",
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "title": "Name"
            },
            "ranking": {
                "type": "string",
                "title": "Ranking",
                "enum": ['excellent', 'not too shabby', 'alpaca built my hotrod']
            }
        }
    }
```

Instead of using the form description as content for the directive, you can put it in a separate file
and load it like this:

```
.. form::
   :file: formdescription.json
```

A description of how Alpaca works is beyond the scope of this README, and you should read
[their fine docs](http://alpacajs.org/tutorial.html) instead.

You will probably want to add something like this to your config:


```
EXTRA_HEAD_DATA += """
<link type="text/css" href="//code.cloudcms.com/alpaca/1.5.8/bootstrap/alpaca.min.css" rel="stylesheet" />
"""

BODY_END += """
<script type="text/javascript" src="//cdnjs.cloudflare.com/ajax/libs/handlebars.js/1.3.0/handlebars.js"></script>
<script type="text/javascript" src="//code.cloudcms.com/alpaca/1.5.8/bootstrap/alpaca.min.js"></script>
<script>
$(document).ready(function() {
    $('div.alpacaform').each(function(index, element) {
        data = eval(element.id+'_data');
        Alpaca(element, data);
    });});
</script>
"""
```
