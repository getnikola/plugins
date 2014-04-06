This plugin implements support for "series of posts".

Imagine you want to write a 5-part tutorial on Nikola. You would have to choose a series name
like "Nikola Tutorial".

Then, create ``series/nikola-tutorial.txt`` and put there something that looks much like a post,
but the content describes the tutorial, like so:

```
.. title: Nikola Tutorial

A series of posts describing how to do FOO and BAR using Nikola.
```

Then, start writing the series. Suppose there are three posts, called nikola-1 nikola-2 and nikola-3.

In each post, add a series metadata field with the series name (in this case nikola-tutorial) and
make it use the series-post template:

```
.. series: nikola-tutorial
.. template: series-post
```

What will happen after you do all this?

1. There will be a ``output/series/index.html`` listing all your series.
2. There will be a ``output/series/nikola-tutorial.html`` describing this series and linking all the posts.
3. Each post will contain a section describing the series and linking all the related posts.

**This is still a WIP.**
