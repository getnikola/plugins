<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Nikola Webapp</title>
    <link href="//netdna.bootstrapcdn.com/bootstrap/3.1.1/css/bootstrap.min.css" rel="stylesheet">
    <script src="//cdnjs.cloudflare.com/ajax/libs/jquery/2.1.0/jquery.js"></script>
    <script src="//netdna.bootstrapcdn.com/bootstrap/3.1.1/js/bootstrap.min.js"></script>
<%block name="head">
</%block>
</head>
<body>
    <div class="navbar navbar-inverse" role="navigation">
      <div class="container">
        <div class="navbar-header">
          <button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-collapse">
            <span class="sr-only">Toggle navigation</span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </button>
          <a class="navbar-brand" href="/">Nikola Webapp</a>
        </div>
        <div class="collapse navbar-collapse">
          <ul class="nav navbar-nav">
            <li>
               <a href="#" data-toggle="modal" data-target="#newPost">New Post</a>
            </li>
            <li>
               <a href="#" data-toggle="modal" data-target="#newPage">New Page</a>
            </li>
          </ul>
        </div><!--/.nav-collapse -->
      </div>
    </div>
    <div class="container">
        <%block name="content">
        </%block>
    </div>


<!-- New Page Modal -->
<div class="modal fade" id="newPage" tabindex="-1" role="dialog" aria-labelledby="newPageLabel" aria-hidden="true">
  <form method="POST" action="/new/page">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
        <h4 class="modal-title" id="newPageLabel">Create New Page?</h4>
      </div>
      <div class="modal-body">
        <input class="form-control" name="title" id="title" placeholder="Title">
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
        <button type="submit" class="btn btn-primary">Create Page</button>
      </div>
    </div>
  </div>
  </form>
</div>

<!-- New Post Modal -->
<div class="modal fade" id="newPost" tabindex="-1" role="dialog" aria-labelledby="newPostLabel" aria-hidden="true">
  <form method="POST" action="/new/post">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
        <h4 class="modal-title" id="newPostLabel">Create New Post?</h4>
      </div>
      <div class="modal-body">
        <input class="form-control" name="title" id="title" placeholder="Title">
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
        <button type="submit" class="btn btn-primary">Create Post</button>
      </div>
    </div>
  </div>
  </form>
</div>


</body>

