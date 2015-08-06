This plug-in enables your site to take full advantage of the Start
screen on Windows 8.1 and Windows Phone 8.1 with Internet Explorer 11,
and Windows 10 and Windows 10 Mobile with Microsoft Edge.

### Browser configuration file

Generates a configuration file `/browserconfig.xml` for tile images and
Live Tiles with notifications for the Windows 8.1 and Windows Phone 8.1
Start screens, and the Start menu in Windows 10 . Windows 8 is not
supported because Microsoft.

Internet Explorer 11 will automatically request this file from your
server root when a user tries to pin you site to their Start screen. If
you cannot store the file directly under root, you can reference the
file by adding the following to your template’s `<head>`:

    <meta name="msapplication-config" content="example-path/browserconfig.xml" />

All other resources are relative to the `BASE_URL` option.

### Tile images

Specify any of these tile templates to use them. Note that the actual
image assets are at a 1.8 scale-factor from the tile template sizes!

    WINDOWS_LIVE_TILES = { "tileimages": {
        "square70x70logo": "assets/msapplication/tile128x128.png",
        "square150x150logo": "assets/msapplication/tile270x270.png",
        "wide310x150logo": "assets/msapplication/tile558x270.png",
        "square310x310logo": "assets/msapplication/tile558x558.png",
    } }

The smallest size is *required*. All the smaller sizes are *required*
to use the larger sizes. Only include the largest sizes if your site
updates with new content at least a couple of times per week.

The image should be PNG with a transparent background. Reserve some
space in the image canvas for padding. More details in the
[Windows guidelines](http://msdn.microsoft.com/en-us/library/windows/apps/hh781198.aspx "Tile and toast visual assets").

Notification templates (small XML files) for Live Tiles will be stored
in assets/msapplication/ so it will be a good idea to keep tile images
in the same location.

The `WINDOWS_LIVE_TILES[tilecolor]` option is used to specify your
tile’s background color. The value should be in HEX (#ffffff). Note
that Windows and Windows Phone will apply a gradient to the background
so verify the end result.

### Notifications

Notifications will rotate the headlines and header images, if set,
for the five latest posts on the site. At least the two smallest tile
images are *required* to use notifications. The largest tile size only
rotates between the tile image and a tile showing the three latest
headlines from your site

The notifications works like RSS were the newest posts are rotated on
the Start screen. The notification tiles are generated and stored in
`assets/msapplication/`. The `/browserconfig.xml` file will reference
these file for Windows to periodically download.

The `WINDOWS_LIVE_TILES[frequency]` option is used to specify how
often Windows should look for new notification data. The value is in
minutes and can be one of these values: 30, 60, 360, 720, or 1440.
12 hours is the default. Only lower the value if your site actually
updates frequently with new content.

Header images can be included in post notifications by setting
`previewimage: post-header-image.png` in each post’s metadata section.
Any resolution and dimension can be used for this image. This is not
used for the very largest tile size.

Localization is not fully supported in Windows for web site tiles. Only
the default site language is used.

### How-to pin a site to the Start screen

Instruct your visitors to click the Favorites button and then click on
the Pin site button in Internet Explorer 11 to add your site to their
Start screen. Older Windows versions will also pin your site using the
same method, but will not use the enhanced tile images nor notifications.

