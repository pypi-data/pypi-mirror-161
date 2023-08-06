from setuptools import setup, find_packages

Version = "1.0.6"

Description = "A basic Roblox Package"

Long_Description = "A Python package that allows you to manage your Roblox account with Roblox API."

setup(
    name="RobloxPyApi3",
    version=Version,
    author="pyProjects3 (github.com/pyProjects3)",
    description=Description,
    long_description_content_type="text/markdown",
    long_description=Long_Description,
    packages=find_packages(),
    install_requires=['colorama','socket.py','requests',"RobloxPyApi3Update"],
    keywords=['python3','python','Roblox',"API","POST GET","json"],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
    ]
)