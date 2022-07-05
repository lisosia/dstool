from setuptools import setup

setup(
    name="dstool",
    version="0.1",
    install_requires=[],
    extras_require={
        "develop": []
    },
    entry_points={
        "console_scripts": [
            "dstool = dstool.main:main",
            "foo_dev = package_name.module_name:func_name [develop]"
        ],
    }
)
