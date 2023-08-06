# Wikipedia shortcode

A Nikola shortcode plugin to generate HTML elements containing the first paragraph of the summary of a given Wikipedia article. By adding appropriate CSS styles, the resulting HTML can be made to behave as tooltips.

The shortcode takes a mandatory argument `article` and an optional one, `text`, which, if set, is used as the text of the link *in lieu* of `article`. Here are two examples:

```
{{% wikipedia article="DNA" %}}

{{% wikipedia article="DNA" text="DNA molecule" %}}
```

This is the HTML structure that is returned by `{{% wikipedia article="DNA" %}}`:

```html
<span class="wikipedia_tooltip"><a href="https://en.wikipedia.org/wiki/DNA" target="_blank">DNA</a>
    <span class="wikipedia_summary">
    <a href="https://en.wikipedia.org/wiki/DNA" target="_blank" class="wikipedia_wordmark">
        <img src="https://upload.wikimedia.org/wikipedia/commons/b/bb/Wikipedia_wordmark.svg"><span class="wikipedia_icon"></span>
    </a>
    Deoxyribonucleic acid (DNA) is a polymer composed of two polynucleotide chains that coil around each other to form a double helix. The polymer carries genetic instructions for the development, functioning, growth and reproduction of all known organisms and many viruses. DNA and ribonucleic acid (RNA) are nucleic acids. Alongside proteins, lipids and complex carbohydrates (polysaccharides), nucleic acids are one of the four major types of macromolecules that are essential for all known forms of life.
    </span>
</span>
```

**Nota Bene:** the plugin uses [Wikipedia-API](https://pypi.org/project/Wikipedia-API/) to obtain the summaries from Wikipedia. This procedure is carried out every time `nikola` builds the pages where the shortcode is invoked. Don't forget to connect to the internet before building the website!

## CSS style examples

The following CSS code (adapted from [here](https://codepen.io/Xopoc/pen/eYmvpPW)) can be used to style the tooltip:

```css
.wikipedia_tooltip {
  cursor: help;
  position: relative;
}

.wikipedia_tooltip .wikipedia_summary {
  background: #fff;
  top: 99%;
  font-size: 80%;
  line-height: normal;
  display: block;
  left: -125px; /* found with trial and error */
  margin-top: 15px;
  opacity: 0;
  padding: .5em 1em;
  pointer-events: none;
  position: absolute;
  width: 300px;
  transform: translateY(10px);
  transition: all 0.25s ease-out;
  box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  z-index: 999 !important;
}

#post-main a.wikipedia_wordmark {
    display: block;
    border-bottom: 1px solid black;
    padding-bottom: 2px;
    margin-bottom: 5px;
}

#post-main a.wikipedia_wordmark:hover {
    background-color: white; /* overwrites the main hover style */
}

#post-main a.wikipedia_wordmark img {
    height: 25px;
}

#post-main a.wikipedia_wordmark .wikipedia_icon:after { 
   content: '\f08e';
   color: #304860;
   font-family: 'fontawesome';
   font-weight: normal;
   font-style: normal;
   font-size: 110%;
   margin-top: 5px;
   float: right;
   text-decoration:none;
} 

/* This bridges the gap so you can mouse into the tooltip without it disappearing */
.wikipedia_tooltip .wikipedia_summary:before {
  top: -20px;
  content: " ";
  display: block;
  height: 20px;
  left: 0;
  position: absolute;
  width: 100%;
}

/* a CSS upper triangle */
.wikipedia_tooltip .wikipedia_summary:after {
  border-left: solid transparent 10px;
  border-right: solid transparent 10px;
  border-bottom: solid #fff 10px;
  top: -10px;
  content: " ";
  height: 0;
  left: 50%;
  margin-left: -13px;
  position: absolute;
  width: 0;
}

.wikipedia_tooltip:hover .wikipedia_summary {
  opacity: 1;
  pointer-events: auto;
  transform: translateY(0px);
}
```

And here is a screenshot:

![](https://raw.githubusercontent.com/getnikola/plugins/master/v8/wikipedia/tooltip-example.png)
