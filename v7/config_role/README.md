Add the `config` role, it reads a value from the `conf.py` file.

Usage:

```rst
Send us an email to :config:`BLOG_EMAIL`
```

Here `BLOG_EMAIL` is the variable name from the `conf.py` file.
Note that the text is rendered as an email link, not just as plain text.
This is because the value is interpreted as reStructuredText.
