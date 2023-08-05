import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="raspy_qmc5883l",
    version="0.2.7",
    author="Yanfu Zhou",
    author_email="yanfu.zhou@outlook.com",
    description="Python driver for the QMC5883L 3-axis magnetic sensor",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/RigacciOrg/py-qmc5883l",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Operating System :: OS Independent",
    ],
)
