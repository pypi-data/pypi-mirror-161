from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import setuptools

_VERSION = '1.7.1-3'


DEPENDENCY_LINKS = [
]

REQUIRED_PACKAGES = [
"boto3",
"torch==1.8.0",
"ray==1.4.1",
"ray[default]==1.4.1",
"ray[tune]==1.4.1",
"tensorflow==2.4.1",
"azure-storage-blob==12.8.1",
"protobuf==3.20.*",
"lazy_import"
]

setuptools.setup(
    name='innocuous-magic',
    version=_VERSION,
    description='innocuous library',
    install_requires=REQUIRED_PACKAGES,
    dependency_links=DEPENDENCY_LINKS,
    packages = ['innocuous'],
    zip_safe = False
)
