# coding=utf-8
from __future__ import print_function
from test.modelscripts.framework.assertions import (
    simpleTestDeneratorAssertions)
from modelscripts.scripts.megamodels.printer.megamodels import \
    MegamodelPrinter

from modelscripts.metamodels.tasks import METAMODEL

def testGenerator_Assertions():
    for (v,f,m,eim, emm) in \
            simpleTestDeneratorAssertions(METAMODEL):
        yield (v,f,m,eim, emm)

def testFinalMegamodel():
    MegamodelPrinter().display()
