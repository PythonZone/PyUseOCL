# coding=utf-8
from __future__ import unicode_literals, print_function, absolute_import, division

from typing import Text, List

from modelscribes.base.printers import (
    AbstractPrinter
)
from modelscribes.metamodels.permissions import (
    UCPermissionModel,
    metamodel
)
from modelscribes.metamodels.permissions.sar import Action


class PermissionModelPrinter(AbstractPrinter):  # TODO: check implementation

    def __init__(self, permissionModel, displayLineNos=True):
        #type: (UCPermissionModel, bool) -> None
        super(PermissionModelPrinter, self).__init__(
            displayLineNos=displayLineNos)
        self.permissionModel=permissionModel

    def do(self):
        super(PermissionModelPrinter, self).do()
        self._permissionModel(self.permissionModel)
        return self.output

    def _permissionModel(self, permissionModel):
        self.outLine(
            'permission model',
            lineNo=None, #usecaseModel.lineNo)  # TODO: change parser
            linesAfter=1 )
        self.outLine(str(permissionModel))
    #
    # def _rule(self, rule):
    #     self.outLine(str(rule))




# def playerString(player):
#     if isinstance(player, (Usecase, Actor)):
#         return player.name
#     else:
#         raise NotImplementedError(
#             'ERROR: playerString(%s) is not implemented' % (
#                 type(player)
#         ))
#
# def resourceString(resource):
#     if isinstance(resource, (Class, AssociationClass, Association)):
#         return resource.name
#     elif isinstance(resource, Attribute):
#         return '%s.%s' % (
#             resource.class_.name,
#             resource.name
#         )
#     elif isinstance(resource, Role):
#         return '%s.%s' % (
#             resource.association.name,
#             resource.name
#         )
#     else:
#         raise NotImplementedError(
#             'ERROR: playerString(%s) is not implemented' % (
#                 type(resource)
#         ))

def actionName(action):
    #type:  (Action)->Text
    return action.name

def actionNames(actions):
    #type: (List[Action])->Text
    _=[]
    names=[a.name for a in actions]
    # TODO: add the case with other labels
    return ''.join(
        [ name if names in names else ""
          for name in 'CRUDX']
    )

metamodel.registerModelPrinter(PermissionModelPrinter)