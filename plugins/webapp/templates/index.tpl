<%inherit file="base.tpl" />
<%block name="head">
<script src="/static/js/jPages.min.js"></script>
<style type="text/css">
        html {
            overflow-y: scroll;
        }

        .post_holder, .page_holder {
            margin: 15px 0;
            padding: 10px;
            border: 1px solid #dddddd;
            border-radius: 5px;
            text-align: center;
        }

        .post_holder a, .page_holder a {
        /*      font-size: 12px; */
                cursor: pointer;
                margin: 0 5px;
                color: #333;
        }

        .post_holder a:hover, .page_holder a:hover {
                background-color: #222;
                color: #fff;
        }

        a.jp-previous { margin-right: 15px; }
        a.jp-next { margin-left: 15px; }

        a.jp-current, a.jp-current:hover {
                color: #FF4242;
                font-weight: bold;
        }

        a.jp-disabled, a.jp-disabled:hover {
                color: #bbb;
        }

        a.jp-current, a.jp-current:hover,
        a.jp-disabled, a.jp-disabled:hover {
                cursor: default;
                background: none;
        }

        .post_holder span, .page_holder span {
            margin: 0 5px;
        }

        code {
            color: #333;
            background-color: #F9F2F4;
        }
    </style>
</%block>

<%block name="content">
<form method="POST">

<div class="row">
    <div class="col-md-6">
        <h2 style="text-align: center;">Posts</h2>
        <div class="post_holder"></div>
        <div class="list-group" id="post_container">
        % for p in site.posts:
            <div class="list-group-item">
                <h3>${p.title()}</h3>
                <small>Date: ${p.date}</small>
                <div class="pull-right">
                    <a type="button" class="btn" href="/edit/${p.source_path}"><span class="glyphicon glyphicon-edit"></span> Edit</a>
                    <a type="button" class="btn" href="/delete/${p.source_path}"><span class="glyphicon glyphicon-remove"></span> Delete</a>
                </div>
            </div>
        % endfor
        </div>
        <div class="post_holder"></div>
    </div>

    <div class="col-md-6">
        <h2 style="text-align: center;">Pages</h2>
        <div class="page_holder"></div>
        <div class="list-group" id="page_container">
        % for p in site.pages:
            <div class="list-group-item">
                <h3>${p.title()}</h3>
                <small>Date: ${p.date}</small>
                <div class="pull-right">
                    <a type="button" class="btn" href="/edit/${p.source_path}"><span class="glyphicon glyphicon-edit"></span> Edit</a>
                    <a type="button" class="btn" href="/delete/${p.source_path}"><span class="glyphicon glyphicon-remove"></span> Delete</a>
                </div>
            </div>
        % endfor
        </div>
        <div class="page_holder"></div>
    </div>
</div>

</form>
<script type="text/javascript">
$(function(){
  $("div.post_holder").jPages({
    containerID : "post_container",
    perPage: 5
  });
  $("div.page_holder").jPages({
    containerID : "page_container",
    perPage: 5
  });
});
</script>
</%block>
