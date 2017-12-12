# coding=utf-8

import logging
from distutils.dir_util import mkpath


from test.modelscripts import (
    TEST_CASES_DIRECTORY,
    BUILD_DIRECTORY,
)

import os
import modelscribes.use.engine.merger

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('test.'+__name__)


SEX_DIR=os.path.join(BUILD_DIRECTORY, 'sex')
mkpath(SEX_DIR)


# TODO:add this again
# def test_UseOclModel_Simple():
#     check_isValid('Demo.use')



def testGenerator_UseOclModel_full():
    test_dir=os.path.join(
        TEST_CASES_DIRECTORY,'sex')

    for test in ['Demo6','Demo666.5']:

        soilfile=os.path.join(test_dir,'%s.soil'%test)
        tracefile=os.path.join(test_dir,'%s.stc'%test)
        sexfile=os.path.join(
            SEX_DIR,
            '%s.sex'%test
        )
        yield check_isValid, soilfile, tracefile, sexfile



def check_isValid(soilfile, tracefile, sexfile):
    modelscribes.use.engine.merger.merge(soilfile, tracefile, sexfile)

