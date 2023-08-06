# TikTok API on RapidAPI

## Available on [PyPi](https://pypi.org/project/tiktok_rapidapi/)

## Install
### using pip
```
pip install tiktok_rapidapi
```
### using poetry
```
poetry add tiktok_rapidapi
```

## Build
### Windows
```
git clone https://github.com/dankaprogg/tiktok_rapidapi.git

cd tiktok_rapidapi
py -m venv venv
cd venv/Scripts/ && activate && cd ../../
pip install -r requirements.txt
py setup.py sdist bdist_wheel install
```
### Linux
```
git clone https://github.com/dankaprogg/tiktok_rapidapi.git

cd tiktok_rapidapi
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 setup.py sdist bdist_wheel install
```

## Tests
We are using pytest framework with pytest-asyncio

```shell
pip install pytest
pip install pytest-asyncio
```

```shell
pytest -v tests
```