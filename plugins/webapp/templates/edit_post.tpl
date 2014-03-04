<%inherit file="base.tpl" />
<%block name="head">
</%block>
<%block name="content">
<h1>Editing ${post.title()}</h1>
<form method='POST'>
<ul>
% for k,v in post.meta['en'].items():
<li>${k}: <input name="${k}" value="${v}">
% endfor
</ul>
<div id="epiceditor" style="height: 500px;"></div>
<textarea name="content" id="content" style="display:none;"></textarea>
<button formaction="/save/${post.source_path}">Save</button>
</form>

<script src="//cdnjs.cloudflare.com/ajax/libs/jquery/2.1.0/jquery.js"></script>
<script src="/static/js/epiceditor.min.js"></script>
<script type="text/javascript">
var opts = {
  container: 'epiceditor',
  textarea: 'content',
  basePath: '/static',
  clientSideStorage: false,
  localStorageName: 'epiceditor',
  useNativeFullscreen: true,
  parser: marked,
  file: {
    name: 'epiceditor',
    defaultContent: ${json.dumps(open(path).read().split('\n\n', 1)[1])},
    autoSave: 100
  },
  theme: {
    base: '/themes/base/epiceditor.css',
    preview: '/themes/preview/preview-dark.css',
    editor: '/themes/editor/epic-dark.css'
  },
  button: {
    preview: true,
    fullscreen: true,
    bar: "auto"
  },
  focusOnLoad: false,
  shortcut: {
    modifier: 18,
    fullscreen: 70,
    preview: 80
  },
  string: {
    togglePreview: 'Toggle Preview Mode',
    toggleEdit: 'Toggle Edit Mode',
    toggleFullscreen: 'Enter Fullscreen'
  },
  autogrow: false
};
var editor = new EpicEditor(opts).load();
</script>
</%block>
