# Introduction #

This page intents to describe the programming style to follow on PPC-project.

# Details #

We will try to adhere to [official Python style guide](https://www.python.org/dev/peps/pep-0008/) ([spanish translation](http://mundogeek.net/traducciones/guia-estilo-python.htm)).

Better explained and more interesting ideas in [Code Like a Pythonista](http://python.net/~goodger/projects/pycon/2007/idiomatic/handout.html).

Remember some main ideas:
  * Use the standard syntax for pydoc in comments.
  * Use 4 spaces for indenting (never use tabs).
  * Use spaces in assignments (make them clear)
  * Comment code blocks as necessary
  * Use lowercase and underscore to separate compound function or method names.
  * Use uppercase and uppercased separation for classes or modules (ex. "RedCar").

Example:
```
class ClassName:

    def function_name(x, y):
        """
        Comment on what is done... (Get volume for 1m height)

        x, comment about x, if useful.

        Return: comment on returned object, if useful.
        """
        z = 1

        # Get volume
        a = x * y
        v = a * z

        return z   
```
