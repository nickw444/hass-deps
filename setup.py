import os

from setuptools import setup

readme_path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)),
    'README.md',
)
long_description = open(readme_path).read()

setup(
    name='hass-deps',
    packages=['hass_deps'],
    author="Nick Whyte",
    author_email='nick@nickwhyte.com',
    description="3rd party dependency manager for Home Assistant",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/nickw444/hass-deps',
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python',
    ],
    install_requires=[
        'requests',
        'click',
        'ruamel-yaml',
    ],
    entry_points={
        'console_scripts': ['hass-deps=hass_deps.__main__:cli'],
    },
)
