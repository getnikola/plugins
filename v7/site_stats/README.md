This plugin computes some summary statistics and inserts them into the global context.

## Installation

From within a nikola site directory:

```
$ nikola plugin -i site_stats
```

## Usage

After installation, the following keys/values are accessible in `site.GLOBAL_CONTEXT`:

* `post_count`: the number of posts in the site
* `cat_count`: the number of categories in the site
* `tag_count`: the number of tags in the site.

Nothing visible will happen, though, unless you access this data within a template.  
For instance, with `mako` templates you can insert a block

```html
<%def name="html_site_statistics()">
    <div class="stats">
        <div class="line">
            <span class="counter">${post_count}</span>
            <span class="caption">Posts</span>
        </div>
        <div class="line">
            <span class="counter">${category_count}</span>
            <span class="caption">Categories</span>
        </div>
        <div class="line">
            <span class="counter">${tag_count}</span>
            <span class="caption">Tags</span>
        </div>
    </div>
</%def>
```

Then put `${html_site_statistics()}` wherever you want it to go.

## Related

The [`sidebar`](https://github.com/getnikola/plugins/tree/master/v7/sidebar) plugin
has this same functionality and more.  It provides templates and generates an HTML 
fragment that can be included into any page.  Either way will require some template
hacking to see the content on your pages.
