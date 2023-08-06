#!/usr/bin/env python
# pylint: disable=W0142,W0403,W0404,W0613,W0622,W0622,W0704,R0904,C0103,E0611
#
# You should have received a copy of the GNU Lesser General Public License
# along with CubicWeb.  If not, see <http://www.gnu.org/licenses/>.
"""glamconv setup module"""

import os.path as osp

from setuptools import find_packages, setup


description = """set of tools to import, transform and manipulate standard GLAM formats (EAD,
Unimarc, etc.)"""  # noqa

requires = {
    "lxml": None,
}

install_requires = [
    "{0} {1}".format(d, v and v or "").strip() for d, v in requires.items()
]

with open(osp.join(osp.dirname(__file__), "README.rst")) as f:
    long_description = f.read()


setup(
    name="glamconv",
    version="0.2.0",
    license="LGPL",
    description=description,
    long_description=description,
    author="Logilab S.A. (Paris, FRANCE)",
    author_email="contact@logilab.fr",
    url="http://www.logilab.org/project/glamconv",
    classifiers=[
        "Programming Language :: Python",
    ],
    packages=find_packages(exclude=["test"]),
    install_requires=install_requires,
    include_package_data=True,
    # entry_points={},  # XXX TODO
    zip_safe=False,
)
