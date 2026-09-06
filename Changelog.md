# pyDocusaurus: Convert your Python docstrings to Docusaurus Documentation

{:toc}

## CHANGELOG

### 1.0.0 @ 09/06/2026

#### :wrench: Fix

1. Fix: Correct the missing icon import when solving the rendered pages.

#### :floppy_disk: Change

1. Set the exposed port `3000` for the docker project.
2. Split the `renderer.package.Saver*` into a separated module `renderer.saver`.

### 1.0.0 @ 09/03/2026

#### :mega: New

1. Create this project.
2. Finish the `core` package with package analysis functionalities.
3. Finish the `components` package with component-rendering functionalities.
4. Finish the `renderer` package for rendering documentation pages.
5. Finish the CLIs.
6. Finish GitHub configurations and actions.

#### :floppy_disk: Change

1. Drop the support for `Python 3.13` because it does not support `annotationlib`.
2. Improve the code structure for maintaing the implementation complexity.
