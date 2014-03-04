<%inherit file="base.tpl" />
<%block name="content">
<form method="POST">
% for p in site.posts:
    <div>
        <h3>Title: ${p.title()}<small>&nbsp;--&nbsp;Date: ${p.date}</small></h3>
    <button formaction="/edit/${p.source_path}"><span class="glyphicon glyphicon-edit"></span> Edit</button>
    <button formaction="/delete/${p.source_path}"><span class="glyphicon glyphicon-remove"></span> Delete</button>
    </div>
% endfor
</form>
</%block>
