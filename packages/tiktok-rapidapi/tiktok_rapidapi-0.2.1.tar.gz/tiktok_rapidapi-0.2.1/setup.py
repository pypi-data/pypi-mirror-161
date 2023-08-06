from setuptools import setup

setup(
    name='tiktok_rapidapi',
    version='0.2.1',
    description='TikTok API on RapidAPI',
    packages=['tiktok_rapidapi', 'tiktok_rapidapi.schemas'],
    author_email='dshvedov@kotspin.ru',
    zip_safe=False,
    author='Daniil Shvedov',
    keywords=['rapidapi', 'tiktok', 'parsing'],
    classifiers=[],
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url='https://github.com/dankaprogg/tiktok_rapidapi',
)
