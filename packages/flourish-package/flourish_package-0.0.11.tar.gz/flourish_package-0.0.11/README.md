# flourish_package
This is a SaaS solution to create data pipelines and manage metadata for businesses (small and big).

## Authors
- [@srinivaskrishnamurthy](https://github.com/srinivaskrishnamurthy)
## Installation
Install flourish with pip
```bash
  pip install flourish_package
```
## Requirements
* aiohttp
* aioitertools
* async-timeout
* attrs
* boto3
* botocore
* chardet
* et-xmlfile
* fsspec
* greenlet
* idna
* importlib-metadata
* Jinja2
* jmespath
* MarkupSafe
* multidict
* numpy
* openpyxl
* pandas
* psycopg2-binary
* pyodbc
* pymssql
* python-dateutil
* pytz
* s3fs
* s3transfer
* six
* smart_open
* SQLAlchemy
* typing-extensions
* urllib3
* wrapt
* xlrd
* yarl
* zipp

## Instructions to build package
- pip3 install build
- python -m build
- py -m pip install --upgrade twine
- py -m twine upload --repository testpypi dist/* --verbose
- py -m twine upload --repository pypi dist/* --verbose
- python -m pip install -i https://test.pypi.org/simple/ flourish-package==0.0.7
- python -m pip install flourish-package==0.0.8