from setuptools import setup, find_packages
from cndversion.__version__ import __version__

setup(name='cndversion',
    version=__version__,
    description="The definitive tools to manage VERSION and change file",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    keywords='',
    author='Denis FABIEN',
    author_email='denis.fabien@changendevops.com',
    url='https://gitlab.com/changendevops/cndversion',
    license='MIT/X11',
    packages=find_packages(exclude=['ez_setup', 'examples', 'spec', 'spec.*']),
    include_package_data=True,
    package_data={'cndversion': ['VERSION']},
    zip_safe=False,
    install_requires=['clint', 'coverage'],
    test_require=['expect', 'doublex', 'doublex-expects'],
    entry_points={
        'console_scripts': [
            'cndversion = cndversion.cli:main'
        ]
    },
    project_urls={
        "Documentation": "https://changendevops.com",
        "Source": "https://gitlab.com/changendevops/cndversion",
    },
)