# The Quotebacks Markdown Extension Plugin

## Description

[Quotebacks](https://quotebacks.net) is a recently-developed JavaScript library for applying a standard styling to blockquotes on web pages. As released, it also includes a browser plugin for Chrome, that helps with capturing the quotes and applying the correct HTML. 

However, if you don't use Chrome, and/or you prefer to write in Markdown, it's not ideal. 

Luckily [Matt Webb](http://interconnected.org/home/2020/06/16/quotebacks) has written an [extension for Python-Markdown](https://github.com/genmon/quotebacks-mdx) which allows the writer to activate the Quotebacks styling using simple Markdown.

This change incorporates that extension into Nikola.

To use it you'll have to have the `quotebacks.js` file installed, and have suitable code in your template to ensure that it's referenced in posts. Or just suitable code to import it from the CDN.

## Usage

To use it you'll need to make the `quoteback.js` library accessible to your site. You can either download it and keep a local copy, and then include something like the following in your `EXTRA_HEAD_DATA` constant in `conf.py`:

```
    EXTRA_HEAD_DATA = """
        <script src="/js/quoteback.js"></script>
    """
```

Or you can access it using a CDN, in which case you'll want the following:

```
    EXTRA_HEAD_DATA = """
        <script src="https://cdn.jsdelivr.net/gh/Blogger-Peer-Review/quotebacks@1/quoteback.js">
    """
```

To quote something using Quotebacks, include Markdown like this:

```

What is Nikola? The answer is here:

> Nikola is a static website and blog generator. The very short explanation is that it takes some texts you wrote, and uses them to create a folder full of HTML files. If you upload that folder to a server, you will have a rather full-featured website, done with little effort.
>
> -- Roberto Alsina and the Nikola contributors, [The Nikola Handbook](https://getnikola.com/handbook.html)



```
