from setuptools import setup, find_packages

with open("README.md") as readme_file:
    README = readme_file.read()

with open("HISTORY.md") as history_file:
    HISTORY = history_file.read()

setup_args = dict(
    name="rlocker_expiryaddon",
    version="0.1.0",
    description="A Plugin for Resource Locker Project to implement expiry logic",
    long_description_content_type="text/markdown",
    long_description=README + "\n\n" + HISTORY,
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    author="Jim Erginbash",
    author_email="jimshapedcoding@gmail.com",
    keywords=["Rlocker", "rlocker", "ResourceLocker", "Python 3", "Resource Locker"],
    url="https://github.com/jimdevops19/rlocker_expiry_addon.git",
    download_url="https://pypi.org/project/rlocker_expiry_addon/",
)

install_requires = []

entry_points = {}

if __name__ == "__main__":
    setup(**setup_args, install_requires=install_requires, entry_points=entry_points)
