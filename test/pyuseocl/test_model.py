# coding=utf-8

from test.pyuseocl import TEST_CASES_DIRECTORY

import os
import pyuseocl.analyzer

def test_UseOclModel_Simple():
    testFile = 'Demo.use'
    use_model_file = pyuseocl.analyzer.UseOCLModelFile(
        TEST_CASES_DIRECTORY + os.sep + testFile)
    assert use_model_file.isValid
    model = use_model_file.model
    print model
    class_names = [c.name for c in model.classes]
    for n in ['Employee', 'Department', 'Project' ]:
        assert n in class_names
    assoc_names = [c.name for c in model.associations]
    for n in ['WorksIn','WorksOn','Controls' ]:
        assert n in assoc_names
    ac = model.associationNamed['Controls']
    assert ac.name == 'Controls'
    assert ac.roles[0].name == 'department'
    assert ac.roles[1].name == 'project'
    assert ac.isBinary
    assert ac.roles[0].opposite == ac.roles[1]
    assert ac.roles[1].opposite == ac.roles[0]
    assert ac.roles[0].type.name == 'Department'
    assert ac.roles[1].type.name == 'Project'
    assert ac.roles[0].cardinalityMin == 1
    assert ac.roles[0].cardinalityMax == 1
    assert ac.roles[1].cardinalityMin == 0
    assert ac.roles[1].cardinalityMax == None

    department=model.classNamed['Department']
    assert set(r.name for r in department.outgoingRoles) == set(['employee', 'project'])
    assert set(r.name for r in department.incomingRoles) == set(['department'])