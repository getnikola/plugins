A plugin that renders math using a local KaTeX install.

## Requirements

* Node.js installed, in $PATH, accessible as the `node` command
* KaTeX accessible by Node (run `npm install` in this plugin’s folder)
* `USE_KATEX = True` in config

You may also edit `math_helper.tmpl` to remove the KaTeX JavaScript includes
(which are now unused). You should make sure that the KaTeX CSS version in
`math_helper.tmpl` matches the version of KaTeX you installed with npm.

## Examples:

<!-- don't include the raw tag in your blog posts, it's only for the plugin site not to render the math -->

Inline:

    Euler’s formula: {{% raw %}}{{% lmath %}}e^{ix} = \cos x + i\sin x{{% /lmath %}}{{% /raw %}}

Display:

    {{% raw %}}{{% lmath display=true %}}\int \frac{dx}{1+ax}=\frac{1}{a}\ln(1+ax)+C{{% /lmath %}}{{% /raw %}}
    {{% raw %}}{{% lmathd %}}\int \frac{dx}{1+ax}=\frac{1}{a}\ln(1+ax)+C{{% /lmathd %}}{{% /raw %}}

Alternate name:

    {{% raw %}}{{% localkatex %}}e^{ix} = \cos x + i\sin x{{% /localkatex %}}{{% /raw %}}

The following options are supported: `displayMode`, `display` (alias), `throwOnError`, `errorColor`, `colorIsTextColor` — see [KaTeX docs](https://github.com/Khan/KaTeX#rendering-options) for details.

