from setuptools import setup, find_packages

Version = "1.0.0"

Description = "A package allows you to update RobloxPyApi3 Package"

Long_Description = "A package related to RobloxPyApi3 that allows you to uninstall, upgrade, install RobloxPyApi3 package."

setup(
    name="RobloxPyApi3Update",
    version=Version,
    author="pyProjects3 (github.com/pyProjects3)",
    description=Description,
    long_description_content_type="text/markdown",
    long_description=Long_Description,
    packages=find_packages(),
    install_requires=['requests'],
    keywords=["RobloxPyApi3","UnInstall",'CheckforVersion',"Upgrade","Pip","Install"],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
    ]
)