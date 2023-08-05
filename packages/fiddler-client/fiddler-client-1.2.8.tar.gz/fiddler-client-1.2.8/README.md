# Fiddler Python client

## Distribution

The Fiddler Python client is published as
[`fiddler-client`](https://pypi.org/project/fiddler-client/) in the Python
Package Index.

1. Set the new semantic version number in `fiddler/_version.py`, e.g. `1.4.3`;
2. Update `PUBLIC.md` with release notes for the new version;
3. Raise a PR;
4. Once the PR is merged, create a new annotated tag on the `main` branch. For
   example:

   ```bash
   git checkout main
   git pull
   git tag -a 1.4.3 -m 'The one that fixes event publishing'
   git push --tag
   ```

This triggers a pipeline that will automatically build and publish the new
version of the client to PyPI.

Note: dev versions may be published from any branch at any time by using a
`.devN` affix, as described in [PEP-440](https://peps.python.org/pep-0440/). For
example: `1.4.3.dev5`.
