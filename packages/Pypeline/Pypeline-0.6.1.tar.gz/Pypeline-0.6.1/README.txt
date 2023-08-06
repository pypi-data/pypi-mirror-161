=========================
Getting to Know Pypeline
=========================

A Brief History
----------------

There are a wide variety of plain text-based syntaxes for generating
documentation, including HTML. GitHub's Markup
[http://github.com/github/markup/] library provides a way to handle all of
these formats in an easily-extensible manner. Pypeline provides the same
functionality in a native Python library.

Installing Pypeline
--------------------

In order to install Pypeline, pip install it.  (We recommend using a virtualenv
[http://pypi.python.org/pypi/virtualenv] for development.)

    $ virtualenv pypeline_env
    $ source pypeline_env/bin/activate
    (pypeline_env)$ pip install pypeline

Getting Started
----------------

Out of the box Pypeline supports the following markups:

* Markdown
* Textile
* ReST
* Creole
* Plain text

To get started with these:

    >>> from pypeline.markup import markup
    >>> markup.render('foo.txt')
