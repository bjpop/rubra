# Retrieve the version number of rubra from the setup.py file.
# This solution was suggested on Stack Overflow:
# http://stackoverflow.com/questions/2058802/how-can-i-get-the-version-defined-in-setup-py-setuptools-in-my-package

import pkg_resources  # part of setuptools

rubra_version = pkg_resources.require("Rubra")[0].version
