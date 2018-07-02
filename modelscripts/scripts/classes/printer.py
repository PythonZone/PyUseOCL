# coding=utf-8
from __future__ import unicode_literals, print_function, absolute_import, \
    division

from typing import Optional

from modelscripts.base.modelprinters import (
    ModelPrinterConfig,
    ModelSourcePrinter
)
from modelscripts.metamodels.classes import (
    METAMODEL,
    ClassModel
)

import logging

from typing import Optional

from modelscripts.base.modelprinters import (
    ModelPrinter,
    ModelPrinterConfig,
)
from modelscripts.base.printers import (
    indent
)
from modelscripts.metamodels.classes import (
    ClassModel
)


# logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('test.' + __name__)


__all__ = [
    'ClassModelPrinter',
]

class ClassModelPrinter(ModelPrinter):
    def __init__(self,
                 theModel,
                 config=None):
        #type: (ClassModel, Optional[ModelPrinterConfig]) -> None
        assert theModel is not None
        assert isinstance(theModel, ClassModel)
        super(ClassModelPrinter, self).__init__(
            theModel=theModel,
            config=config
        )

    def doModelContent(self):
        super(ClassModelPrinter, self).doModelContent()
        self.doUseModel(self.theModel)
        return self.output

    def doUseModel(self, model):
        self.doModelTextBlock(model.description)

        for d in model.dataTypes:
            self.doDataType(d)


        for e in model.enumerations:
            self.doEnumeration(e)

        for c in model.classes:
            self.doClass(c)

        for a in model.associations:
            self.doAssociation(a)

        for ac in model.associationClasses:
            self.doAssociationClass(ac)

        # TODO: invariants, operationConditions, dataTypes
        return self.output

    def doDataType(self, datatype):
        self.outLine('%s %s' % (
            self.kwd('datatype'),
            datatype.name))
        self.doModelTextBlock(datatype.description, indent=1)

    def doEnumeration(self, enumeration):
        self.outLine('%s %s' % (
            self.kwd('enumeration'),
            enumeration.name))
        self.doModelTextBlock(enumeration.description, indent=1)
        for (i,el) in enumerate(enumeration.literals):
            self.doEnumerationLiteral(el)
        self.outLine('')
        return self.output

    def doEnumerationLiteral(self, enumerationLiteral):
        self.outLine(enumerationLiteral.name, indent=1)
        self.doModelTextBlock(
            enumerationLiteral.description, indent=2)
        return self.output

    def doClass(self, class_):
        self.doModelTextBlock(class_.description)
        if class_.superclasses:
            sc = (self.kwd('extends ')
                  +self.kwd(',').join(map(
                        lambda s:s.name, class_.superclasses)))
        else:
            sc = ''
        if class_.isAbstract:
            abstract='abstract '
        abstract='abstract' if class_.isAbstract else None
        self.outLine(' '.join(filter(None,[
            (self.kwd('abstract') if class_.isAbstract else ''),
            self.kwd('class'),
            class_.name,
            sc])))

        # self.doModelTextBlock(class_.description)
        if class_.attributes:
            self.outLine(self.kwd('attributes'), indent=1)
            for attribute in class_.attributes:
                self.doAttribute(attribute)

        if class_.operations:
            self.outLine(self.kwd('operations'), indent=1)
            for operation in class_.operations:
                self.doOperation(operation)

        # if class_.invariants:
        #     for invariant in class_.invariants:
        #         self.doInvariant(invariant)

        return self.output

    def doAssociation(self, association):
        self.outLine('%s %s' % (
            self.kwd(association.kind),
            association.name,
        ))
        self.doModelTextBlock(association.description, indent=1)
        self.outLine(self.kwd('roles'), indent=1)
        for role in association.roles:
            self.doRole(role)
        return self.output

    def doAssociationClass(self, associationClass):
        self.doModelTextBlock(associationClass.description)
        if associationClass.superclasses:
            superclass_names = [c.name for c in associationClass.superclasses]
            sc = self.kwd(' < ') + self.kwd(',').join(superclass_names)
        else:
            sc = ''
        self.out('%s %s%s %s' % (
            self.kwd('associationclass'),
            associationClass.name,
            sc,
            self.kwd('between')))
        self.doModelTextBlock(associationClass.description)


        for role in associationClass.roles:
            self.doRole(role)

        if associationClass.attributes:
            self.outLine(self.kwd('attributes'), indent=1)
            for attribute in associationClass.attributes:
                self.doAttribute(attribute)

        if associationClass.operations:
            self.outLine(self.kwd('operations'))
            for operation in associationClass.operations:
                self.doOperation(operation)

        self.outLine(self.kwd('end'), linesAfter=1)
        return self.output

    def doAttribute(self, attribute):
        visibility={
            'public':None,
            'private':'-',
            'protected':'%',
            'package':'~'
        }[attribute.visibility]
        _=' '.join(filter(None,[
                self.kwd('/') if attribute.isDerived else None,
                visibility,
                attribute.name,
                self.kwd(':'),
                attribute.type.name]))
        self.outLine(_, indent=2)
        self.doModelTextBlock(attribute.description, indent=3)
        # if attribute.isDerived:
        #     self.outLine('%s %s' % (
        #             self.kwd('derive ='),
        #             attribute.expression),
        #         indent=2
        #     )
        return self.output

    def doOperation(self, operation):
        self.doModelTextBlock(operation.description)
        self.outLine('%s%s' % (
                operation.signature,
                ' =' if operation.hasImplementation
                    else ''),
            indent=1
        )
        if operation.hasImplementation:
            self.outLine(indent('        ',operation.expression)+'\n')
        self.doModelTextBlock(operation.description)

        # for condition in operation.conditions:
        #     self.doOperationCondition(condition)
        return self.output

    def doInvariant(self, invariant):
        if invariant.class_ is None:
            prefix_comment = ''
            prefix_first = self.kwd('context ')
            prefix_rest = '    '
        else:
            prefix_comment = '    '
            prefix_first = '    '
            prefix_rest  = '        '
        self.doModelTextBlock(invariant.description)
        self.outLine('%s%s%s %s:' % (
            prefix_first,
            self.kwd('existential ') if invariant.isExistential else '',
            self.kwd('inv'),
            invariant.name,
        ))
        self.doModelTextBlock(invariant.description)
        self.out(indent(prefix_rest, invariant.expression)+'\n')
        return self.output

    def doRole(self, role):
        self.doModelTextBlock(role.description)
        _=('%s %s %s%s%s%s%s%s' % (
            role.name,
            self.kwd(':'),
            role.type,
            self.kwd('['),
            role.cardinalityMin,
            self.kwd('..'),
            '*' if role.cardinalityMax is None else role.cardinalityMax,
            self.kwd(']')))
        self.outLine(_, indent=2)
        self.doModelTextBlock(role.description)
        return self.output

    # def doOperationCondition(self, condition):
    #     prefix_first = '        '
    #     prefix_rest  = '            '
    #     keyword='pre' if isinstance(condition,PreCondition) else 'post'
    #     self.doModelTextBlock(condition.description)
    #     self.outLine('%s%s %s:' % (
    #         prefix_first,
    #         self.kwd(keyword),
    #         condition.name,
    #     ))
    #     self.doModelTextBlock(condition.description)
    #     self.out(indent(prefix_rest,condition.expression)+'\n')
    #     return self.output




METAMODEL.registerModelPrinter(ClassModelPrinter)
METAMODEL.registerSourcePrinter(ModelSourcePrinter)

