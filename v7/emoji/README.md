Plugin to embed emojis in restructuredText.

Usage:

```
    I give this plugin a :emoji:`+1`
```

And yes, I know the syntax is annoying but :+1: is invalid restructuredText syntax.

An alternative is to just use emojify.js in your templates.

The emojis are **not** shipped with this plugin, they are provided by emojify
provided for free by CloudFlare.

For a full list of emojis, check http://www.emoji-cheat-sheet.com/

You probably want to add something like this to your ``custom.css``:

```css
.emoji {
    height: 1.4em;
    vertical-align: text-bottom;
}
```
