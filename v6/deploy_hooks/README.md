This is a signal handling plugin that lets you run custom commands or functions
on new entries created since the last deployment.

Your command can be a template that can be rendered by the templating engine
that your theme uses or a simple Python callable.  The new entry/post is passed
in the context to the templating engine, along with the command.  If the
command is a callable, the entry is passed as an argument.
