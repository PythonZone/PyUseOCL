# coding=utf-8

import logging

from nose.plugins.attrib import attr

from modelscripts.interfaces.environment import Environment
from test.modelscripts.drivers import (
    TEST_CASES_DIRECTORY,
)

import os
import modelscripts.scripts.classes.parser
from modelscripts.scripts.classes.plantuml import (
    ClassPlantUMLPrinter
)

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('test.'+__name__)

@attr('slow')
def testGenerator_cls_plantuml():
    test_dir=os.path.join(
        TEST_CASES_DIRECTORY,'cls')

    #--- test all files ----------------------
    files = [
        os.path.join(test_dir, f)
            for f in os.listdir(test_dir)
            if f.endswith('.cls')]

    for filename in files:
        yield doBuildDiagram, filename


def doBuildDiagram(filename):

    #--- parser: .obs -> system -------------------
    source = modelscripts.scripts.classes.parser.ClassModelSource(
        fileName=filename,
    )
    if not source.isValid:
        print('#'*10+' ignore invalid file  %s' % filename )
    else:
        obm = source.classModel

        puml_file_path=Environment.getWorkerFileName(
            filename,
            extension='.cls.puml')

        print('TST: '+'='*80)
        print('TST: result in %s' % puml_file_path)
        print('TST: '+'='*80)
        gen = ClassPlantUMLPrinter(obm)
        gen.generate(puml_file_path, format='png' )
        print('TST: .png generated')
        print('TST: '+'='*80)

