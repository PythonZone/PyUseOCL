# coding=utf-8
"""issue box registry.
This module provides a unique mixin _MetaCheckerPackageRegistry to be
included in the Megamodel class.
"""

from collections import OrderedDict

from typing import Dict,  List, Optional

__all__=(
    '_MetaCheckerPackageRegistry'
)

class _MetaCheckerPackageRegistry(object):
    """
    Part of the megamodel dealing with metapackages
    """

    _metaCheckerPackageNamed=OrderedDict()

    @classmethod
    def registerMetaCheckerPackage(cls, metaPackage):
        cls._metaCheckerPackageNamed[metaPackage.qname] = metaPackage

    @classmethod
    def metaCheckerPackages(cls):
        # TODO:4 2to3 was cls._metaCheckerPackageNamed.values()
        return list(cls._metaCheckerPackageNamed.values())