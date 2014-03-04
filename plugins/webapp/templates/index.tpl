<%inherit file="base.tpl" />
<%block name="content">
<form>
<button>New Post</button>
<button>New Page</button>
<ul>
% for p in site.posts:
    <li><div>
    <ul>
        <li>Title: ${p.title()}
        <li>Date: ${p.date}
        <li><button formaction="/edit/${p.source_path}">Edit</button> <button>Delete</button>
    </ul>
    </div></li>
% endfor
</ul>
</form>
</%block>
