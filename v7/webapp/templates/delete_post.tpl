<%inherit file="base.tpl" />
<%block name="head">
</%block>
<%block name="content">
<h1 class="title">Really delete "${post.title()}"?</h1>
<a type="button" href="/really_delete/${path}">Yes, really.</a>
</%block>
