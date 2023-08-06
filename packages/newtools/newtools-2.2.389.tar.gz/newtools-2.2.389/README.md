# New Tools

&copy; Deductive 2012-2020, all rights reserved. This code is licensed under MIT license. See [license.txt](https://bitbucket.org/deductive/newtools/src/master/licence.txt) for details.

For documentation see [read the docs](http://newtools.readthedocs.io)

# Development checklist

1. For any new functionality, update the unit tests and run them with nose
1. Add new tests to ensure you get 100% coverage or the tests won't pass
1. Update documentation in the docstrings in the code
1. Add any new classes to [index.rst](docs/index.rst) to ensure they are included in the documentation

To test the documentation locally you can run:

```bash
pip install sphinx
pip install sphinx_rtd_theme
sphinx-build -b html docs docs/build/
```

In a separate terminal, run
```
python -m http.server --directory docs/build/html/
```

You should now be able to see the documentation on [localhost](http://localhost:8000).

Note the documentation does not automatically update and you need to re-run ```sphinx-build -b html docs docs/build/``` when you make a change.
