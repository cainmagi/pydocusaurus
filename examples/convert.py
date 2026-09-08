# -*- coding: UTF-8 -*-
"""
Example: Convert
================
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
The minimal example of converting a package into the documentation.

The example produces the files of **this** pyDocusaurus package.

In the project folder, run the following command:
```
python -m examples.convert
```
"""

import os

import pydocusaurus

__all__ = ("render",)


def render() -> None:
    """Render the documentation of pydocusaurus."""
    cur_dir = os.path.dirname(__file__)
    out_dir = os.path.join(cur_dir, "docs-{0}".format(pydocusaurus.__name__))
    print("Producing the documentation: {0}".format(out_dir))
    pydocusaurus.render_package_as_mdx(
        pydocusaurus, out_dir=out_dir, package_info="cainmagi"
    )


if __name__ == "__main__":
    render()
