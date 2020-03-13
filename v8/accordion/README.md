Accordion for reStructuredText, combining [Bootstrap's Collapse and Card components](https://getbootstrap.com/docs/4.0/components/collapse/#accordion-example).

Separate each box from the next with two blank lines. The first line in each group will become the title. All of the remaining lines in the group will become the contents.

You can put arbitrary reStructuredText directives inside the accordion, including videos and images.

This plugin supports both boostrap3 and boostrap4, but if you are using bootstrap3 you must add an extra "bootstrap3" argument to the directive. See the second example below.

```

    .. accordion::

      Box 1
      Lorem ipsum dolor sit amet, consectetur adipiscing elit. Morbi accumsan, nulla sit amet aliquam molestie, nisi purus dignissim ante, non scelerisque diam ligula eu ex. Integer tristique felis id mattis imperdiet. Maecenas elementum purus quis vestibulum elementum. Etiam nec eleifend metus, vel convallis nisl. Fusce tempor ante felis, vitae tincidunt nulla pulvinar sed. Vivamus eget ipsum nulla. Vestibulum lectus enim, facilisis vel ipsum in, vulputate sodales ligula. Curabitur lorem erat, ullamcorper sit amet imperdiet vitae, lobortis non neque. Fusce porta tempor nulla. Vivamus pulvinar purus nibh. Vestibulum semper rutrum sapien, eget suscipit lectus semper sit amet. Interdum et malesuada fames ac ante ipsum primis in faucibus. Aenean vel fringilla urna, ut vestibulum arcu. Sed bibendum augue risus, quis gravida libero bibendum ac.


      Box 2
      Lorem ipsum dolor sit amet, consectetur adipiscing elit. Morbi accumsan, nulla sit amet aliquam molestie, nisi purus dignissim ante, non scelerisque diam ligula eu ex. Integer tristique felis id mattis imperdiet. Maecenas elementum purus quis vestibulum elementum. Etiam nec eleifend metus, vel convallis nisl. Fusce tempor ante felis, vitae tincidunt nulla pulvinar sed. Vivamus eget ipsum nulla. Vestibulum lectus enim, facilisis vel ipsum in, vulputate sodales ligula. Curabitur lorem erat, ullamcorper sit amet imperdiet vitae, lobortis non neque. Fusce porta tempor nulla. Vivamus pulvinar purus nibh. Vestibulum semper rutrum sapien, eget suscipit lectus semper sit amet. Interdum et malesuada fames ac ante ipsum primis in faucibus. Aenean vel fringilla urna, ut vestibulum arcu. Sed bibendum augue risus, quis gravida libero bibendum ac.


      Box 3
      Lorem ipsum dolor sit amet, consectetur adipiscing elit. Morbi accumsan, nulla sit amet aliquam molestie, nisi purus dignissim ante, non scelerisque diam ligula eu ex. Integer tristique felis id mattis imperdiet. Maecenas elementum purus quis vestibulum elementum. Etiam nec eleifend metus, vel convallis nisl. Fusce tempor ante felis, vitae tincidunt nulla pulvinar sed. Vivamus eget ipsum nulla. Vestibulum lectus enim, facilisis vel ipsum in, vulputate sodales ligula. Curabitur lorem erat, ullamcorper sit amet imperdiet vitae, lobortis non neque. Fusce porta tempor nulla. Vivamus pulvinar purus nibh. Vestibulum semper rutrum sapien, eget suscipit lectus semper sit amet. Interdum et malesuada fames ac ante ipsum primis in faucibus. Aenean vel fringilla urna, ut vestibulum arcu. Sed bibendum augue risus, quis gravida libero bibendum ac.

```

Here is another example for use in a bootstrap3-themed site. Notice the start of the YouTube directives are indented.

```

    .. accordion:: bootstrap3

      Box 1
      The Last Starfigher (1984)

      .. youtube:: H7NaxBxFWSo
        :width: 400
        :align: center


      Box 2
      Terminator Trailer (1984)

      .. youtube:: k64P4l2Wmeg
        :width: 400
        :align: center


      Box 3
      Bladerunner (1982)

      .. youtube:: eogpIG53Cis
        :width: 400
        :align: center

```
