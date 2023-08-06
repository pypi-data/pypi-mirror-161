from setuptools import setup, find_packages

setup(
    name='zmcli',
    version='0.2.2',
    # keywords=['Safari', 'Bookmarks', 'JSON', 'Monsoir'],
    description='A Simple Command Line Tool',
    license='MIT License',

    url='https://git.zoom.us/zackary.huang/zmcli',
    author='Zackary',
    author_email='zackaryhuang96@gmail.com',

    packages=find_packages(),
    include_package_data=True,
    platforms=["any"],
    install_requires=['PrettyTable', 'requests', 'tqdm', 'docopt'],
    python_requires='>3.6',
    entry_points={
        'console_scripts': [
            'zmcli = source.cli:main',
        ]
    }
)