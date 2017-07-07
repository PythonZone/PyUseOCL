# coding=utf-8

from nose.plugins.attrib import attr

import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('test.'+__name__)

from test.pyuseocl import getUseFile

import os
import pyuseocl.use.use.parser
import pyuseocl.use.use.printer

from test.pyuseocl import TEST_CASES_DIRECTORY

# TODO: add this again
# def test_UseOclModel_Simple():
#     check_isValid('Demo.use')


@attr('slow')
def testGenerator_UseOclModel_full():
    test_file_names1 = [
        'civstatAnonymous.use',
        'CyberResidencesOCL.use',
        'AssociationClass.use',
        'Demo.use',
        'Employee.use',
        'NestedOperationCalls.use',
        'Graph.use',
        'civstat.use',
        'tollcoll.use',
        'actionsemantics.use',
        'OCL2MM.use',
        'UML13All.use',
        'UML13Core.use',
        'CarRental2.use',
        'Empty.use',
        'Grammar.use',
        'derived.use',
        'Job.use',
        'Lists.use',
        'Math.use',
        'MultipleInheritance.use',
        'MultipleInheritance_unrelated.use',
        'Person.use',
        'Polygon.use',
        'Project.use',
        'RecursiveOperations.use',
        'ReflexiveAssociation.use',
        'Student.use',
        'simpleSubset.use',
        'simpleSubsetUnion.use',
        'twoSubsets.use',
        'Sudoku.use',
        'Test1.use',
        'Tree.use',
        'CarRental.use',
        'RoyalAndLoyal.use',
        'OCLmetamodel.use',
        'EmployeeExtended.use',
        'bart.use',
    ]
    test_files1=[os.path.join('use',f) for f in test_file_names1]

    use4subdir = os.path.join('use', 'use4', 'test')
    test_dir_2 = os.path.join(TEST_CASES_DIRECTORY,use4subdir)
    # print test_dir_2
    test_files2 = [use4subdir + os.sep + f
                   for f in os.listdir(test_dir_2) if f.endswith('.use')]
    # test_files2=[]
    # #print test_files2
    all_test_files = test_files1 + test_files2
    print all_test_files


    for test_file in all_test_files:
        yield check_isValid, test_file


def check_isValid(testFile):
    use_file = pyuseocl.use.use.parser.UseFile(
        os.path.join(TEST_CASES_DIRECTORY,testFile))
    if not use_file.isValid:
        use_file.printStatus()
    assert use_file.isValid

    out = pyuseocl.use.use.printer.UseOCLPrinter(use_file.model)
    print out.do()
    # if useModel.isValid:
    #     print useModel.model
    # assert useModel.isValid
        #else:
    #    print >> sys.stderr, 'Failed to create canonical form'
    #    for error in use.errors:
    #        print >> sys.stderr, error
    #        # UseOCLConverter.convertCanOCLInvariants(use.canonicalLines)
