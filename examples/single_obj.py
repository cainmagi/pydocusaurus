# -*- coding: UTF-8 -*-
"""
Example: Single Object
======================
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
Print the rendered documentation of a single object.

In the project folder, run the following command:
```
python -m examples.single_obj
```
"""

import pydocusaurus

__all__ = ("render",)


def render() -> None:
    """Render the documentation of an example member in the package pydocusaurus."""
    doc = pydocusaurus.render_obj(pydocusaurus.components.comprotocol.ProtocolComponent)
    if doc is None:
        print("Fail to produce the documentation page.")
        return
    print("Producing the documentation page: {0}".format(doc.slug))
    print("")
    print(doc.render())


if __name__ == "__main__":
    render()
