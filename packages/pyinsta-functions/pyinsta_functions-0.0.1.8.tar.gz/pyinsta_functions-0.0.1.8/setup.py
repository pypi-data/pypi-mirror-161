import setuptools


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='pyinsta',
    version='0.0.1',
    author='Instaviagem',
    author_email='david@instaviagem.com',
    description='Funções mais importantes para o time de dados do Instaviagem',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://bitbucket.org/instaviagem/pyinsta',
    project_urls = {
        "Bug Tracker": "https://bitbucket.org/instaviagem/pyinsta/pull-requests/"
    },
    license='MIT',
    packages=['pyinsta'],
    install_requires=['requests'],
)