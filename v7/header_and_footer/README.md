
This is a plug-in for generating separate header and footer files for your
Nikola site. These can be used to dynamically generate pages when that's something
you need to do.

This plugin was originally created to support the Nginx FancyIndex extension but
is general enough for any case where you might want to compose a Nikola styled
page from 2 halves.

At build time, this plugin looks for files you've told it about and splits them
in two. In the configuration you select the input file, the separator string and
the header and footer output file names.

Multiple files can be split.

Input and output file configuration may include $LANG which is replaced with the
language code. The plugin runs across the list of files for each language your site
is configured for.

Example Usage

In conf.py:

	HEADER_AND_FOOTER = [{
	    'source'      : 'header-and-footer/index.html',
	    'separator'   : 'piggy',
	    'header'      : 'header-and-footer/header',
	    'footer'      : 'header-and-footer/footer',
    }]

	PAGES = [
	    ("stories/*.md", "stories", "story.tmpl"),
	    ("root/*.md", "", "story.tmpl"),
	    ("root/*.html", "", "story.tmpl"),
    ]

In root/header-and-footer.html:

	<!-- 
	.. title: FILES!
	.. slug: header-and-footer
	.. date: 2014-06-30 03:50:59 UTC+12:00
	.. tags: 
	.. link: 
	.. description: Reed's Web Site
	.. type: text
	.. hidetitle: True
	-->

	<hr/>
	<p>Department of Files</p>
	<hr/>
	<h1>Index of:
	piggy
	<hr/>

After a build, output/header-and-footer/header and output/header-and-footer/footer will be created from the contents of output/header-and-footer/index.html

The related nginx config which uses these header and footer files looks like:

	root /home/reed/www/site;
	location / {
		try_files $uri $uri/ =404;
	}
	location /files {
		alias /home/reed/www/files;
		try_files $uri $uri/ =404;
        fancyindex on;
        fancyindex_exact_size off;
        fancyindex_localtime on;
        fancyindex_header /header-and-footer/header;
        fancyindex_footer /header-and-footer/footer;
        default_type text/plain;
	}
