from setuptools import setup, find_packages


setup(
    name='macrox',
    packages=['macrox', 'macrox.commands', 'macrox.nodes', 'macrox.tokens', 'macrox.utils'],
    package_dir={'macrox':'src'},
    version = '1.0.7',
    license = 'MIT',
    description = 'A python macro tool',
    author = 'Wrench56',
    author_email = 'dmarkreg@gmail.com',
    url = 'https://github.com/Wrench56/MacroX',
    install_requires = ['colorama', 'keyboard', 'mouse', 'pywin32'],
    long_description = 'Please find more information on my Github page! (under construction)',
    entry_points={
         "console_scripts": [
            "macrox=macrox.client:main"
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Code Generators',
        'License :: Free For Home Use',
        'Natural Language :: English',
        'Operating System :: OS Independent', # Hopefully
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12'
  ],
)