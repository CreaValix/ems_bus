from distutils.core import setup, Extension

ems_serio = Extension(
    "ems_serio",
    [
        "crc.c",
        "ems_serio.c",
        "python_module.c",
        "queue.c",
        "rx.c",
        "serial.c",
        "tx.c"
    ]
)

setup(
    name = "ems_serio",
    version = "1.0.0",
    ext_modules=[ems_serio],
)
