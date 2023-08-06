# PropZen Common

Common modules for PropZen application

## Deployment

1. Make sure `build` is installed
2. Make sure `twine` is installed
3. Run `python -m build .`, this should create a `dist/` folder
4. Run `python -m twine upload dist/*`
5. For `username`, enter `__token__`
6. For `password`, enter `<your_pypi_token>`
