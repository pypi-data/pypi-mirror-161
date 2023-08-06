from setuptools import setup, find_packages

version = '0.6.1'

setup(name='Pypeline',
      version=version,
      description="Easy rendering of markup languages",
      long_description="""Provides an easy, pluggable way to support rendering an arbitrary markup syntax (ReST, Markdown, etc.) to HTML.
""",
      classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries',
        'Topic :: Software Development :: Documentation',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Filters',
        'Topic :: Text Processing :: Markup :: HTML',
        ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='markup, markdown, textile, creole, text',
      author='Kyle Adams',
      author_email='kyle@geek.net',
      url='http://pypeline.sourceforge.net',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      python_requires='>=3.7',
      install_requires=[
        'bleach[css]>=5',
        'html5lib',
      ],
      extras_require={
        'creole': ["Creoleparser >= 0.7.2"],
        'markdown': ["Markdown >= 2.0.3"],
        'textile': ["textile >= 2.1.4"],
        'rst': ["docutils >= 0.7"],
      },
      tests_require=[
        'pytest',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
