Add the [Asyntai](https://asyntai.com) AI chatbot to every page of your Nikola site. It answers visitor questions from your own posts and pages, in more than 80 languages, day and night.

## Setup

1. Install the plugin:

   ```
   nikola plugin -i ai_chatbot
   ```

2. Add your widget ID to `conf.py`:

   ```python
   ASYNTAI_WIDGET_ID = "asyntai_1a2b3c4d5e6f"
   ```

   The widget ID is on the Install page of your [Asyntai dashboard](https://asyntai.com/dashboard). It is the value of `data-asyntai-id` in the snippet shown there, and it starts with `asyntai_`. Creating an account is free, and the Free plan is enough to try the widget.

3. Run `nikola build`. The chat bubble is on every page.

## Options

| Option | Default | What it does |
| --- | --- | --- |
| `ASYNTAI_WIDGET_ID` | required | Your Asyntai widget ID |
| `ASYNTAI_SCRIPT_URL` | the Asyntai CDN | Advanced. Load the widget from another URL |

If the widget ID is missing or malformed, the build prints a message that says how to fix it, and the site builds without the widget.

## What the plugin does

- It adds one `async` script tag to `BODY_END`, so it is in front of the closing body tag of every page: posts, pages, indexes, archives, tag and category pages, and galleries.
- It works with every theme that ships with Nikola, Mako and Jinja alike, and on every language of a multilingual site.
- Your own `BODY_END` code stays as it is. If it already has the Asyntai snippet, the plugin does not add a second one.
- When you change the widget ID, the next build updates every page.

## Answering from your content

Asyntai reads your published pages. Add your site URL in the dashboard, and the assistant answers from the same posts and pages the widget sits on. You can also add documents, and question and answer pairs.

## Support

Email [hello@asyntai.com](mailto:hello@asyntai.com), or read the [Nikola guide](https://asyntai.com/documentation/integrations/nikola/).
