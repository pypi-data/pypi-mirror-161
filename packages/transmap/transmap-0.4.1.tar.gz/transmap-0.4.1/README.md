## Transmap Hub - Python API

This pulls in the various python modules for accessing either the MongoDB Transmap Hub database or for querying API services/datasets through an approachable interface.

### Documentation
[pdoc Docs via Git Pages](https://cast.git-pages.uark.edu/transmap-hub/transmap-python-api/transmap/)

### Usage
```python
import transmap
transmap.lpms.locks() -> pandas.DataFrame
transmap.cwbi.locks.metadata() -> pandas.DataFrame
```
For more information about the sub-packages within the transmap namesapce, see their relevant package descriptions.

### Included Submodules
This uses git submodules to embed the related packages and uses setuptools for package discovery. The following packages are currently included:
- [ais](https://git.uark.edu/cast/transmap-hub/ais-archive "ais-archive")
- [lpms](https://git.uark.edu/cast/transmap-hub/lpms "lpms")
- [cwbi](https://git.uark.edu/cast/transmap-hub/cwbi "cwbi")

If initializing a new repo or submodule, run:
```bash
$ git submodule update --init --recursive
```

Use to get latest if you've cloned previously:
```bash
$ git submodule update --recursive --remote
```

### Install and Build
Increment the version value in `setup.py` manually (for now)
```bash
$ pipenv install
$ pipenv run python setup.py bdist_wheel
```
That will create the appropriate wheel

### Creating a release
- Use curl to post the artifact with your gitlab personal access token:
```bash
$ curl --request POST --header "PRIVATE-TOKEN: #Personal Access Token#" --form file=@dist\transmap-0.1.0-py3-none-any.whl
https://git.uark.edu/api/v4/projects/1857/uploads
```
- This will return a JSON response with a markdown attribute. Copy the markdown value
- First create a tag with the correct version listed as `transmap-x.x.x`
- Paste the markdown value into the release notes when creating the tag

### Install in a python env
This will install the built wheel into your python env
```bash
$ pip[env] install transmap-0.1.0-py3-none-any.whl
```




