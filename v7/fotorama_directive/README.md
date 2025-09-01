Fotorama directive to display a gallery using http://fotorama.io jQuery plugin

# Usage

```
.. fotorama::
   :keyboard: true
   :allowfullscreen: native

   image0.jpg
   image1.jpg
   image2.jpg
   image3.jpg
```

# Gallery centered

If you want to get your fotorama images centered on the web page you
can add this code to your `custom.css`:

```
.fotorama__wrap {
    margin: 0 auto;
}
```
