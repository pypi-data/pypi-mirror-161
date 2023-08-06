<!-- #region -->
# `debuglater`: Store Python traceback for later debugging

`debuglater` writes the traceback of an exception that you can later load in
a Python debugger. `debuglater` works with `pdb`, `pudb`, `ipdb` and `pdbpp`.

You can use the generated file to debug on a different machine (assuming the
environment is the same), without having access to the source code.

For support, feature requests, and product updates: [join our community](https://ploomber.io/community) or follow us on [Twitter](https://twitter.com/ploomber)/[LinkedIn](https://www.linkedin.com/company/ploomber/).

![demo](https://ploomber.io/images/doc/debuglater-demo/debug.gif)

## Installation

```sh

pip install debuglater

# for better serialization support (via dill)
pip install 'debuglater[all]'
```
<!-- #endregion -->

## Example

```sh
# get the example
curl -O https://raw.githubusercontent.com/ploomber/debuglater/master/examples/crash.py
```

```sh tags=["raises-exception"]
# crash
python crash.py
```

<!-- #region -->
Debug:

```sh
dltr crash.dump
```

Upon initialization, try printing the variables `x` and `y`:

```
Starting pdb...
> /Users/ploomber/debuglater/examples/crash.py(5)<module>()
-> x / y
(Pdb) x
1
(Pdb) y
0
(Pdb) quit
```

*Note: you can also use:* `debuglater crash.py.dump`

<!-- #endregion -->

<!-- #region -->
## Integration with Jupyter/IPython

> **Note**
> For an integration with papermill, see [ploomber-engine](https://github.com/ploomber/ploomber-engine)

Add this at the top of your notebook/script:

```python
from debuglater import patch_ipython
patch_ipython()
```
<!-- #endregion -->

```sh
# get sample notebook
curl -O https://raw.githubusercontent.com/ploomber/debuglater/master/examples/crash.ipynb

# install package to run notebooks
pip install nbclient
```

```sh tags=["raises-exception"]
# run the notebook
jupyter execute crash.ipynb
```

Debug:

```
dltr jupyter.dump
```

Upon initialization, try printing the variables `x` and `y`:

```
Starting pdb...
-> x / y
(Pdb) x
1
(Pdb) y
0
(Pdb) quit
```


*Note: you can also use:* `debuglater jupyter.dump`

## Motivation

The [Ploomber team](https://github.com/ploomber/ploomber) develops tools for
data analysis. When data analysis code executes non-interactively
(example: a daily cron job that generates a report), it becomes hard to debug
since logs are often insufficient, forcing data practitioners to re-run the
code from scratch, which can take a lot of time.

`debuglater` can be used for any use case to facilitate post-mortem debugging.

## Use cases

* Debug long-running code (e.g., crashed Machine Learning job)
* Debug multiprocessing code (generate one dump file for each process)

## Credits

This project is a fork of [Eli Finer's pydump](https://github.com/elifiner/pydump).
