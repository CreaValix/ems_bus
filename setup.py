from distutils.core import setup, Extension

import os

EMS_SERIO_DIR = 'ems_serio'

ems_serio = Extension(
    "ems_bus.ems_serio",
    [
        os.path.join(EMS_SERIO_DIR, "crc.c"),
        os.path.join(EMS_SERIO_DIR, "ems_serio.c"),
        os.path.join(EMS_SERIO_DIR, "python_module.c"),
        os.path.join(EMS_SERIO_DIR, "queue.c"),
        os.path.join(EMS_SERIO_DIR, "rx.c"),
        os.path.join(EMS_SERIO_DIR, "serial.c"),
        os.path.join(EMS_SERIO_DIR, "tx.c")
    ],
    libraries=['rt'],
    define_macros=[('PYTHON_MODULE', '1')]
)

setup(
    name='ems_bus',
    version='1.0.0',
    description='A driver for the Buderus EMS protocol',
    url='',
    author='Alexander Simon',
    author_email='Alexander Simon <an.alexsimon@googlemail.com>',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator',
        'Topic :: Terminals :: Serial',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',

    ],
    keywords='ems buderus',
    packages=['ems_bus'],
    ext_modules=[ems_serio],
    python_requires='>=3.6',
#    project_urls={  # Optional
#        'Bug Reports': 'https://github.com/pypa/sampleproject/issues',
#        'Funding': 'https://donate.pypi.org',
#        'Say Thanks!': 'http://saythanks.io/to/example',
#        'Source': 'https://github.com/pypa/sampleproject/',
#    },
    install_requires=['posix_ipc'],  # Optional
)
