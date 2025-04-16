import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='lcarsmonitor',
    version='1.0',
    py_modules=["lcarsmonitor"],
    entry_points={
        "console_scripts": [
            "lcarsmonitor = lcarsmonitor.main:main"
        ]
    },
    author="Fernando Omar Aluani",
    author_email="rewasvat@gmail.com",
    description="Python/IMGUI App to monitor hardware status with a customizable LCARS-themed interface.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Rewasvat/lcars-monitor",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Exclusive Copyright",
        "Operating System :: OS Independent",
    ],
    install_requires=["libasvat", "pythonnet", "pyinstaller"]
)
