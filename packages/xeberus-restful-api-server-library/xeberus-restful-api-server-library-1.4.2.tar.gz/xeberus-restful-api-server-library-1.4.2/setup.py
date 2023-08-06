# Copyright (C) 2019 Majormode.  All rights reserved.
#
# This software is the confidential and proprietary information of
# Majormode or one of its subsidiaries.  You shall not disclose this
# confidential information and shall use it only in accordance with the
# terms of the license agreement or other applicable agreement you
# entered into with Majormode.
#
# MAJORMODE MAKES NO REPRESENTATIONS OR WARRANTIES ABOUT THE SUITABILITY
# OF THE SOFTWARE, EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
# TO THE IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE, OR NON-INFRINGEMENT.  MAJORMODE SHALL NOT BE LIABLE FOR ANY
# LOSSES OR DAMAGES SUFFERED BY LICENSEE AS A RESULT OF USING, MODIFYING
# OR DISTRIBUTING THIS SOFTWARE OR ITS DERIVATIVES.

import os

import setuptools

from majormode.perseus.utils import setup_util


# Base directory where this file is located.
BASE_DIR = os.path.dirname(__file__)


__author__ = "Daniel CAUNE"
__copyright__ = "Copyright (C) 2019, Majormode"
__credits__ = ["Daniel CAUNE"]
__email__ = "daniel.caune@gmail.com"
__license__ = "SEE LICENSE IN <LICENSE.md>"
__maintainer__ = "Daniel CAUNE"
__status__ = "Production"
__version__ = setup_util.read_version_file(BASE_DIR)


setuptools.setup(
    author=__author__,
    author_email=__email__,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    description="Xeberus RESTful API Server Python Library",
    install_requires=setup_util.get_requirements(),
    license=__license__,
    long_description=setup_util.read_readme_file(BASE_DIR),
    long_description_content_type='text/markdown',
    name='xeberus-restful-api-server-library',
    packages=setuptools.find_packages(),
    platforms=['any'],
    python_requires='>=3',
    version=str(__version__),
)
