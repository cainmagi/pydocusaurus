# -*- coding: UTF-8 -*-
"""
Entrypoint
============
@ pyDocusaurus

Author
------
Yuchen Jin (cainmagi)
cainmagi@gmail.com

License
-------
MIT License

Description
-----------
The entrypoint of command lines of this package. Currently, we offer:

```sh
python -m pydocusaurus render-doc {package_name} -o {out_dir}
```
"""

import logging

import typer
from rich.logging import RichHandler

from pydocusaurus.clis.package import app as app_package

app = typer.Typer()
app.add_typer(app_package)

__all__ = ("app",)


if __name__ == "__main__":
    log = logging.getLogger("pydocusaurus")
    logging.basicConfig(
        format="%(name)s - %(message)s",
        datefmt="[%X]",
        level=logging.INFO,
        handlers=[RichHandler(rich_tracebacks=True)],
    )
    log.setLevel(logging.INFO)
    app()
