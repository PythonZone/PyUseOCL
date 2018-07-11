# coding=utf-8

"""
Class metamodel.

The structure of this package is::

    ClassModel
    <>--* Package
        <>--* Enumeration
        <>--* Class
              <>--* Attribute
              <>--* Operation
                    <>--* OperationCondition
              <>--* Invariant
        <>--* Association
              <>--2 Role
        <>--* AssociationClass
              <>--2 Role
              <>--* Attribute
              <>--* Operation
                    <>--* OperationCondition
        <>--* DataType

    Association, Class
    <|--  AssociationClass

    PackagableElement
    <|-- Enumeration

    SimpleType
    <|--  DataType
    <|--  Enumeration

"""
from __future__ import print_function

import abc
import collections
import logging

from typing import Text, Optional, Union, List, Dict

# TODO: metastuff to be continued
from modelscripts.megamodels.py import (
    MComposition,
    MReference,
    MAttribute
)
from modelscripts.megamodels.elements import SourceModelElement
from modelscripts.base.metrics import Metrics
from modelscripts.megamodels.metamodels import Metamodel
from modelscripts.megamodels.dependencies.metamodels import (
    MetamodelDependency
)
from modelscripts.megamodels.models import Model
from modelscripts.metamodels.permissions.sar import Resource

META_CLASSES=( # could be in __all__ (not used by PyParse)
    'ClassModel',
    'PackagableElement',
    'Entity',
    'Member',
    'SimpleType',
    'DataType',
    'Enumeration',
    'EnumerationLiteral',
    'Class',
    'Attribute',
    'Operation',
    'Association',
    'Role',
    'RolePosition',
    'opposite',
    'AssociationClass',
)

__all__= META_CLASSES



#TODO: make associationclass class and assoc + property
# currently the implem is based on separated list for assocclass
# not sure if this should be changed. We start to introduce
# the method 'regularClasses and plainAssociations' but
# we have to check if the storage should be changed or not


#TODO: check if cardinality handling is ok
# It seems that there is a bug with * ou 1..*

# logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('test.' + __name__)

class ClassModel(Model):
    """
    Class model.
    """
    # metaMembers = [
    #       MComposition('enumerations : Enumeration[*] inv model'),
    #       MComposition('plainClasses : Class [*] inv model'),
    #       MComposition(
    #           'associationsClasses : Association[*] inv model'),
    #       MComposition('dataTypes : DataType[*] inv model'),
    # ]


    #TODO: convert this to MComposition when ready
    META_COMPOSITIONS=[
        'enumerations',
        'plainClasses',
        'plainAssociations',
        'associationClasses',
        'dataTypes',
        'packages',
    ]
    def __init__(self):
        #type: () -> None
        super(ClassModel, self).__init__()

        self._isResolved=False

        self._enumerationNamed=collections.OrderedDict()
        #type: Dict[Text, Enumeration]
        #: Map of enumerations, indexed by name.

        #: Map of data types. Indexed by type names/
        #: populated during the resolution phase
        self._dataTypeNamed=collections.OrderedDict()
        #type: Dict[Text, DataType]

        self._plainClassNamed = collections.OrderedDict()
        #type: Dict[Text, PlainClass]
        #: Only plain classes. Use method classes to get
        #: all the class (plain class + association class)

        self._plainAssociationNamed = collections.OrderedDict()
        #type: Dict[Text, PlainAssociation]
        #: Only plain associations. Use method associations to get
        #: all associations (association class + plain associations)

        self._associationClassNamed = collections.OrderedDict()
        #type: Dict[Text, AssociationClass]
        #: Map of association classes, indexed by name.

        self.operationWithFullSignature = collections.OrderedDict()
        #type: Dict[Text, Operation]
        #: Map of operations, indexed by operation full signatures.
        #: e.g. 'Person::raiseSalary(rate : Real) : Real

        self._packageNamed=collections.OrderedDict()
        #type: Dict[Text, Package]
        # ALL packages, not only the top level ones

        self._conditions = [] #type: List['Condition']
        #: List of all conditions (inv/pre/post).
        #  Both those that are declared within a class
        #  or those declared with a context at top level.
        #  Used for resolution.

        from modelscripts.metamodels.classes.core import \
            registerDataTypes
        registerDataTypes(self)
        # Register core datatypes

    @property
    def metamodel(self):
        return METAMODEL

    @property
    def packages(self):
        return self._packageNamed.values()

    @property
    def packageNames(self):
        return self._packageNamed.keys()

    def package(self, name):
        if name in self._packageNamed:
            return self._packageNamed[name]
        else:
            return None

    @property
    def simpleTypeNamed(self):
        _ = self._dataTypeNamed.copy()
        _.update(self._enumerationNamed)
        return _

    @property
    def simpleTypes(self):
        return self.simpleTypeNamed.values()

    @property
    def simpleTypeNames(self):
        return self.simpleTypeNamed.keys()

    @MComposition('DataType[*] inv model')
    def dataTypes(self):
        return self._dataTypeNamed.values()

    @property
    def dataTypeNames(self):
        return self._dataTypeNamed.keys()

    def dataType(self, name):
        if name in self._dataTypeNamed:
            return self._dataTypeNamed[name]
        else:
            return None

    @property
    def enumerations(self):
        return self._enumerationNamed.values()

    @property
    def enumerationNames(self):
        return self._enumerationNamed.keys()

    def enumeration(self, name):
        if name in self._enumerationNamed:
            return self._enumerationNamed[name]
        else:
            return None

    @property
    def plainClasses(self):
        return self._plainClassNamed.values()

    @property
    def plainClassNames(self):
        return self._plainClassNamed.keys()

    def plainClass(self, name):
        if name in self._plainClassNamed:
            return self._plainClassNamed[name]
        else:
            return None

    @property
    def plainAssociations(self):
        return self._plainAssociationNamed.values()

    @property
    def plainAssociationNames(self):
        return self._plainAssociationNamed.keys()

    def plainAssociation(self, name):
        if name in self._plainAssociationNamed:
            return self._plainAssociationNamed[name]
        else:
            return None

    @property
    def associationClasses(self):
        return self._associationClassNamed.values()

    @property
    def associationClassNames(self):
        return self._associationClassNamed.keys()

    def associationClass(self, name):
        if name in self._associationClassNamed:
            return self._associationClassNamed
        else:
            return None

    @property
    def classes(self):
        """
        All classes or association classes.
        """
        return self.plainClasses+self.associationClasses

    @property
    def classNames(self):
        return self.plainClassNames+self.associationClassNames

    def class_(self, name):
        c=self.plainClass(name)
        if c is not None:
            return c
        else:
            return self.associationClass(name)

    @property
    def associations(self):
        """
        All classes or association classes.
        """
        return self.plainAssociations+self.associationClasses

    @property
    def associationNames(self):
        return self.plainAssociationNames+self.associationClassNames

    def association(self, name):
        a=self.plainAssociation(name)
        if a is not None:
            return a
        else:
            return self.associationClass(name)

    def entity(self, name):
        e=self.class_(name)
        if e is not None:
            return e
        else:
            return self.association(name)

    @property
    def metrics(self):
        #type: () -> Metrics
        ms=super(ClassModel, self).metrics
        ms.addList((
            ('package', len(self.packages)),
            ('data type', len(self.dataTypes)),
            ('enumeration', len(self.enumerations)),
            ('enumeration literal', len(
                [el
                    for e in self.enumerations
                        for el in e.literals])),
            ('class', len(self.classes) ),
            ('plain class', len(self.plainClasses) ),
            ('association', len(self.associations)),
            ('plain association',
                 len(self.plainAssociations)),
            ('association class', len(self.associationClasses)),
            ('attribute', len(
                [a
                    for c in self.classes
                        for a in c.attributes])),
            ('role', len(
                [r
                    for a in self.associations
                        for r in a.roles])),
            ))
        return ms

    def globalNames(self):
        return (
            self.enumerationNames
            + self.classNames
            + self.associationNames
            + self.dataTypeNames)

    def __str__(self):
        # TODO: move this to printer
        def category_line(label,elems):
            print(label)
            print(elems)
            n = len(list(elems))
            return '% 3d %s: %s' % (
                n,
                label.ljust(22),
                ','.join(elems)
            )
        categories = [
            ('packages', self.packageNames),
            ('data types', self.dataTypeNames),
            ('enumerations', self.enumerationNames),
            ('plain classes', self.plainClassNames),
            ('plain associations', self.associationNames),
            ('association classes', self.associationClassNames),
            ('operations', self.operationWithFullSignature.keys()),
            # ('invariants'           ,[i.name for i in self.invariants]),  FIXME: should be replaced
        ]
        total = 0
        lines = [ 'class model '+self.name ]
        for (label, items) in categories:
            lines.append(category_line(label, items))
            total += len(list(items))
        print(lines)
        lines.append('% 3d' % total)
        return  '\n'.join(lines)

    def finalize(self):
        super(ClassModel, self).finalize()
        for a in self.associations:
            source_class=a.sourceRole.type
            target_class=a.targetRole.type
            source_class._ownedRoles.append(a.targetRole)
            source_class._playedRoles.append(a.sourceRole)
            target_class._ownedRoles.append(a.sourceRole)
            target_class._playedRoles.append(a.targetRole)

    # def _findAssociationOrAssociationClass(self, name):
    #     raise NotImplementedError('use .association(name) instead')
    #
    #     # TODO: check this implementation
    #     # should be most probably changed into
    #     # associationNamed property
    #     log.debug('_findAssociationOrAssociationClass:%s', name)
    #     if name in self.associationNamed:
    #         return self.associationNamed[name]
    #     elif name in self.associationClassNamed:
    #         return self.associationClassNamed[name]
    #     else:
    #         raise ValueError('ERROR - %s : No association or association class'
    #                         % name )

    # def _findClassOrAssociationClass(self, name):
    #     #TODO: check if the clients really need an exception
    #     # instead of just None
    #     # #type: (Text) -> Union[Class, AssociationClass]
    #     # # TODO: see _findAssociationOrAssociationClass
    #     # if name in self._classNamed:
    #     #     return self._classNamed[name]
    #     # elif name in self.associationClassNamed:
    #     #     return self.associationClassNamed[name]
    #     raise NotImplementedError('use .class_(name) instead')
    #     c=self.class_(name)
    #     if c is not None:
    #         return c
    #     else:
    #         raise ValueError('ERROR - %s : No class or association class'
    #                         % name)

    # def _findRole(self, associationOrAssociationClassName, roleName):
    #     # TODO: see _findAssociationOrAssociationClass
    #     # though there are two parmeters here
    #     log.debug('_findRole: %s::%s',
    #               associationOrAssociationClassName, roleName)
    #     # a = self._findAssociationOrAssociationClass(
    #     #             associationOrAssociationClassName)
    #     a=self.association(associationOrAssociationClassName)
    #
    #     log.debug('_findRole:  %s ',a)
    #     log.debug('_findRole:  %s ',a.roles)
    #     if roleName in a.roleNamed:
    #         return a.roleNamed[roleName]
    #     else:
    #         raise ValueError('ERROR - No "%s" role on association(class) %s' %
    #                         (roleName, associationOrAssociationClassName)  )
    #
    # def _findInvariant(self, classOrAssociationClassName, invariantName):
    #     #type: (Text, Text) -> 'Invariant'
    #     # c = self._findClassOrAssociationClass(
    #     #             classOrAssociationClassName)
    #     c=self.class_(classOrAssociationClassName)
    #     if invariantName in c.invariantNamed:
    #         return c.invariantNamed[invariantName]
    #     else:
    #         raise ValueError('ERROR - No "%s" invariant on class %s' %
    #                         (invariantName, classOrAssociationClassName))


class PackagableElement(SourceModelElement):
    """
    Top level element.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self,
                 name,
                 model,
                 astNode=None,
                 package=None,
                 lineNo=None, description=None):
        super(PackagableElement, self).__init__(
            model=model,
            name=name,
            astNode=astNode,
            lineNo=lineNo, description=description)
        self.package=package
        if self.package is not None:
            self.package.addElement(self)

    @MAttribute('String')
    def label(self):
        if self.package is not None:
            return '%s.%s' % (
                self.package.label,
                self.name)
        else:
            return self.name


class Entity(Resource):

    __metaclass__ = abc.ABCMeta


class Member(Resource):

    __metaclass__ = abc.ABCMeta


class SimpleType(PackagableElement):
    """
    Simple types.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self,
                 name,
                 model,
                 astNode=None,
                 package=None,
                 lineNo=None, description=None):
        super(SimpleType, self).__init__(
            model=model,
            name=name,
            package=package,
            astNode=astNode, lineNo=lineNo, description=description)


    @MAttribute('String')
    def label(self):
        return self.name


class DataType(SimpleType):
    """
    Data types such as integer.
    Built-in data types are not explicitly defined in the source
    file, but they are used after after symbol resolution.
    See "core" module.
    """
    # not in sources, but used created during symbol resolution
    type = 'DataType'

    def __init__(self,
                 model,
                 name,
                 superDataType=None,  # Not used yet
                 astNode=None,
                 package=None,
                 implementationClass=None,
                 isCore=False):
        super(DataType, self).__init__(
            model=model,
            name=name,
            astNode=astNode,
            package=package
        )
        self.superDataType=superDataType
        self.implementationClass=implementationClass
        self.model._dataTypeNamed[name]=self
        self.isCore=isCore

    def __repr__(self):
        return self.name


class AttributeType(object):

    def __init__(self,
                 simpleType,
                 isOptional=False,
                 isMultiple=False):
        self.simpleType=simpleType
        self.isOptional=isOptional
        self.isMultiple=isMultiple

    def accept(self, simpleValue):
        null_type=self.simpleType.model.dataType('NullType')
        valueType=simpleValue.type
        # print('KK'*10,
        #       str(simpleValue)+':'+ str(valueType),
        #       'with var',
        #       id(self.simpleType),
        #       self.simpleType.name,
        #       self.isOptional)
        return (
            (valueType==null_type and self.isOptional)
            or valueType==self.simpleType
        )

    @property
    def name(self):
        return self.simpleType.name


    def __str__(self):
        return (
              str(self.simpleType)
            + ('[0..1]' if self.isOptional else '')
        )

class UnspecifiedValue(object):
    """
    This value just represents that a slot has not specified.
    There is only one value.
    """
    def __str__(self):
        return '?'

UNSPECIFIED=UnspecifiedValue()


class SimpleValue(object):

    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def type(self):
        raise NotImplementedError('type not implemented')

    @abc.abstractmethod
    def equals(self, simpleValue):
        raise NotImplementedError('compare() not implemented')


class EnumerationValue(object):

    def __init__(self, literal):
        self.value=literal
        #type: EnumerationLiteral

    def __str__(self):
        return "%s.%s" % (
            self.value.enumeration.name,
            self.value.name)

    @property
    def type(self):
        return self.value.enumeration

    def equals(self, enumValue):
        return self.value==enumValue.value


class DataValue(SimpleValue):

    __metaclass__ = abc.ABCMeta

    def __init__(self, stringRepr, value, type):
        self.stringRepr=stringRepr
        self.value=value
        self._type=type

    @property
    def type(self):
        return self._type

    def __str__(self):
        return self.stringRepr

    def equals(self, enumValue):
        return self.value==enumValue.value

    @property
    def isCore(self):
        return False    # will be refined for core


class UserDefinedDataValue(DataValue):
    """
    Not used in practice so far.
    """

    def __init__(self, stringRepr, value, type):
        super(UserDefinedDataValue, self).__init__(
            stringRepr=stringRepr,
            value=value,
            type=type
        )





class Package(PackagableElement, Entity):
    """
    Packages.
    """
    def __init__(self,
                 name,
                 model,
                 astNode=None,
                 package=None,
                 lineNo=None, description=None):
        super(Package, self).__init__(
            name=name,
            model=model,
            astNode=astNode,
            package=package,
            lineNo=lineNo, description=description,)
        self._elememts=[]
        model._packageNamed[name]=self


    @property
    def elements(self):
        return self._elememts

    def addElement(self, element):
        assert element is not None
        if element not in self._elememts:
            self._elememts.append(element)
            element.package=self


class Enumeration(SimpleType):
    """
    Enumerations.
    """
    META_COMPOSITIONS = [
        'literals',
    ]
    type = 'Enumeration'

    # metaMembers = [
    #       Reference('model : Model inv enumerations'),
    # ]

    def __init__(self,
                 name,
                 model,
                 package=None,
                 astNode=None,
                 lineNo=None, description=None):
        super(Enumeration, self).__init__(
            name,
            model,
            package=package,
            astNode=astNode,
            lineNo=lineNo,
            description=description)
        self.model._enumerationNamed[name] = self
        self._literals=[]
        # Not sure to understand why this is not a Dict

    @MComposition('EnumerationLiteral[*] inv enumeration')
    def literals(self):
        return self._literals

    @property
    def literalNames(self):
        return [l.name for l in self.literals]

    def literal(self, name):
        # Not sure to understand why this is not a Dict
        for literal in self.literals:
            if literal.name==name:
                return literal
        else:
            return None

    def __str__(self):
        return self.name

    def __repr__(self):
        return '%s(%s)' % (self.name, repr(self.literals))


class EnumerationLiteral(SourceModelElement):

    def __init__(self, name, enumeration, astNode=None, lineNo=None,
                 description=None):
        SourceModelElement.__init__(
            self,
            model=enumeration.model,
            astNode=astNode,
            name=name,
            lineNo=lineNo, description=description)
        self.enumeration=enumeration
        self.enumeration._literals.append(self)


class Class(PackagableElement, Entity):
    """
    Classes.
    """

    __metaclass__ = abc.ABCMeta

    META_COMPOSITIONS = [
        'attributes',
        'operations',
        'invariants',
    ]

    def __init__(self, name, model, isAbstract=False, superclasses=(),
                 package=None, lineNo=None, description=None, astNode=None):
        super(Class, self).__init__(
            name=name,
            model=model,
            package=package,
            astNode=astNode,
            lineNo=lineNo,
            description=description)
        self.model._plainClassNamed[name] = self
        self.isAbstract = isAbstract
        self.superclasses = superclasses  # strings resolved as classes

        #FIXME: add support for inheritance
        self.attributeNamed = collections.OrderedDict()

        # TODO: deal with operation and operation names
        # Signature looks like op(p1:X):Z
        self.operationNamed = collections.OrderedDict()

        # Anonymous invariants are indexed with id like _inv2
        # but their name (in Invariant) is always ''
        # This id is just used internaly
        self.invariantNamed = collections.OrderedDict()   # after resolution

        self._ownedRoles = [] # after resolution
        self._playedRoles = [] # after resolution

    @property
    def attributes(self):
        return self.attributeNamed.values()

    def attribute(self, name):
        if name in self.attributeNamed:
            return self.attributeNamed[name]
        else:
            return None

    @property
    def attributeNames(self):
        return self.attributeNamed.keys()

    @property
    def operations(self):
        return self.operationNamed.values()

    @property
    def operationNames(self):
        return self.invariantNamed.keys()

    @property
    def invariants(self):
        return self.invariantNamed.values()

    @property
    def invariantNames(self):
        return self.invariantNamed.keys()

    @property
    def ownedRoles(self):
        return self._ownedRoles

    @property
    def playedRoles(self):
        return self._playedRoles

    @property
    def names(self):
        return (
            self.attributeNames
            +self.operationNames
            +self.invariantNames)

    @property
    def idPrint(self):
        #type: () -> List[Attribute]
        return [
            a for a in self.attributes
                if a.isId ]

    @abc.abstractmethod
    def isPlainClass(self):
        # This method is not really useful as isinstance can be used.
        # It is just used to prevent creating object of this class
        # (using ABCMeta is not enough to prevent this).
        raise NotImplementedError()


class PlainClass(Class):
    """
    PlainClasses, that is, classes that are not association class.
    """

    def isPlainClass(self):
        return True


class Attribute(SourceModelElement, Member):
    """
    Attributes.
    """

    def __init__(self, name, class_, type=None,
                 description=None,
                 visibility='public',
                 isDerived=False,
                 isOptional=False,
                 tags=(),
                 stereotypes=(),
                 isInit=False, expression=None,
                 lineNo=None, astNode=None):
        SourceModelElement.__init__(
            self,
            model=class_.model,
            name=name,
            astNode=astNode,
            lineNo=lineNo, description=description)
        self.class_ = class_
        self.class_.attributeNamed[name] = self
        self.type = type # string later resolved as SimpleType
        self._isDerived = isDerived
        self.visibility=visibility
        self.isOptional = isOptional
        self.isInit = isInit  # ?
        self.expression = expression
        self.tags=tags
        self.stereotypes=stereotypes

    @MAttribute('Boolean')
    def isDerived(self):
        return self._isDerived

    @isDerived.setter
    def isDerived(self,isDerived):
        self._isDerived=isDerived

    @property
    def label(self):
        return '%s.%s' % (self.class_.label, self.name)

    @property
    def isId(self):
        return 'id' in self.tags

    @property
    def isReadOnly(self):
        return 'readOnly' in self.tags

    @property
    def isClass(self):
        return 'isClass' in self.tags

# class Parameter

class Operation(SourceModelElement, Member):
    """
    Operations.
    """
    META_COMPOSITIONS = [
        'conditions',
    ]

    def __init__(self, name,  class_, signature, code=None,
                 expression=None, astNode=None,
                 lineNo=None, description=None):
        SourceModelElement.__init__(
            self,
            model=class_.model,
            name=name,
            astNode=astNode,
            lineNo=lineNo, description=description)
        self.class_ = class_
        self.signature = signature
        self.class_.operationWithSignature[signature] = self
        self.full_signature = '%s::%s' % (class_.name, self.signature)
        self.class_.model.operationWithFullSignature[self.full_signature] = self
        # self.parameters = parameters
        # self.return_type = return_type
        self.expression = expression
        # Anonymous pre/post are indexed with id like _pre2/_post6
        # but their name (in PreCondition/PostCondition) is always ''
        # This id is just used internaly
        self.conditionNamed = collections.OrderedDict() #type: Dict[Text, 'Condition']

    @property
    def label(self):
        return '%s.%s' % (self.class_.label, self.name)

    @MComposition('Condition[*]')
    def conditions(self):
        return self.conditionNamed.values()

    def conditionNames(self):
        return self.conditionNamed.keys()


    @MAttribute('Boolean')
    def hasImplementation(self):
        return self.expression is not None


RolePosition=Union['source','target']

def opposite(rolePosition):
    if rolePosition=='source':
        return 'target'
    elif rolePosition=='target':
        return 'source'
    else:
        raise NotImplementedError(
            "Position %s doesn't exists." % rolePosition)


class Association(PackagableElement, Entity):
    """
    Associations.
    """

    __metaclass__ = abc.ABCMeta

    META_COMPOSITIONS = [
        'roles',
    ]

    def __init__(self,
                 name, model, kind=None, package=None,
                 lineNo=None, description=None, astNode=None):
        # type: (Text,ClassModel,Optional[Text], Optional[Package] ,Optional[int],Optional[Text],Optional[Text]) -> None
        super(Association, self).__init__(
            name=name,
            model=model,
            package=package,
            astNode=astNode,
            lineNo=lineNo, description=description)
        self.model._plainAssociationNamed[name] = self
        self.kind = kind   # association|composition|aggregation|associationclass  # TODO:should associationclass be
        # there?
        self.roleNamed = collections.OrderedDict() # indexed by name

    @property
    def roles(self):
        return self.roleNamed.values()

    @property
    def roleNames(self):
        return self.roleNamed.keys()

    @MAttribute('Integer')
    def arity(self):
        return len(self.roles)

    @MAttribute('Boolean')
    def isBinary(self):
        return self.arity == 2

    @MAttribute('Boolean')
    def isNAry(self):
        return self.arity >= 3

    @MReference('Role')
    def sourceRole(self):
        if not self.isBinary:
            raise ValueError(
                '"sourceRole" is not defined on "%s" n-ary association' % (
                    self.name
                ))
        return self.roles[0]

    @MReference('Role')
    def targetRole(self):
        if not self.isBinary:
            raise ValueError(
                '"targetRole" is not defined on "%s" n-ary association' % (
                    self.name
                ))
        return self.roles[1]

    def role(self, position):
        #type: (RolePosition) -> Role
        if position=='source':
            return self.roles[0]
        elif position=='target':
            return self.roles[1]
        else:
            raise NotImplementedError(
                'role position "%s" is not implemented' % position)

    @MAttribute('Boolean')
    def isManyToMany(self):
        return (
            self.isBinary
            and self.roles[0].isMany
            and self.roles[1].isMany
        )

    @MAttribute('Boolean')
    def isOneToOne(self):
        return (
            self.isBinary
            and self.roles[0].isOne
            and self.roles[1].isOne
        )

    @MAttribute('Boolean')
    def isForwardOneToMany(self):
        return (
            self.isBinary
            and self.roles[0].isOne
            and self.roles[1].isMany
        )

    @MAttribute('Boolean')
    def isBackwardOneToMany(self):
        return (
            self.isBinary
            and self.roles[0].isMany
            and self.roles[1].isOne
        )

    @MAttribute('Boolean')
    def isOneToMany(self):
        return self.isForwardOneToMany or self.isBackwardOneToMany

    @property
    def navigability(self):
        return {
            (True, True) : 'both',
            (True, False) : 'backward',
            (False, True) : 'forward',
            (False, False) : 'none'
        }[(self.roles[0].isNavigable, self.roles[1].isNavigable)]

    @property
    def isComposition(self):
        return self.kind=='composition'

    @property
    def isAggregation(self):
        return self.kind=='aggregation'

    @abc.abstractmethod
    def isPlainAssociation(self):
        # This method is not really useful as isinstance can be used.
        # It is just used to prevent creating object of this class
        # (using ABCMeta is not enough to prevent this).
        raise NotImplementedError()


class PlainAssociation(Association):

    def isPlainAssociation(self):
        return True


class Role(SourceModelElement, Member):
    """
    Roles.
    """

    def __init__(self, name, association, astNode=None,
                 cardMin=None, cardMax=None, type=None,
                 navigability=None,
                 qualifiers=None, subsets=None, isUnion=False,
                 expression=None,
                 tags=(),
                 stereotypes=(),
                 lineNo=None, description=None):

        # unamed role get the name of the class with lowercase for the first letter
        if name == '' or name is None:
            if type is not None:
                name = type[:1].lower() + type[1:]
        SourceModelElement.__init__(
            self,
            model=association.model,
            name=name,
            astNode=astNode,
            lineNo=lineNo, description=description)
        self.association = association
        self.association.roleNamed[name] = self
        self.cardinalityMin = cardMin
        self.cardinalityMax = cardMax
        self.type = type  # string to be resolved in Class

        # (str,str) to be resolved in (str,SimpleType)
        self.qualifiers = qualifiers
        self.subsets = subsets
        self.isUnion = isUnion
        self.expression = expression
        self.tags=tags
        self.navigability=navigability
        self.stereotypes=stereotypes

    @property
    def isOrdered(self):
        return 'ordered' in self.tags

    @property
    def isNavigable(self):
        return self.navigability != 'x'

    @property
    def isNavigabilitySpecified(self):
        return self.navigability is not None

    @property
    def label(self):
        return '%s.%s' % (self.association.label, self.name)

    @property
    def cardinalityLabel(self):
        if self.cardinalityMin is None and self.cardinalityMax is None:
            return None
        if self.cardinalityMin == self.cardinalityMax:
            return str(self.cardinalityMin)
        if self.cardinalityMin == 0 and self.cardinalityMax is None:
            return '*'
        return ('%s..%s' % (
            str(self.cardinalityMin),
            '*' if self.cardinalityMax is None else str(
                self.cardinalityMax)

        ))

    @property
    def opposite(self):
        if self.association.isNAry:
            raise ValueError(
                '%s "opposite" is not available for %s n-ary association. Try "opposites"' % (
                    self.name,
                    self.association.name
                ))
        rs = self.association.roles
        return rs[1] if self is rs[0] else rs[0]

    @property
    def opposites(self):
        rs = list(self.association.roles)
        rs.remove(self)
        return rs

    @property
    def isOne(self):
        return self.cardinalityMax == 1

    @property
    def isMany(self):
        return self.cardinalityMax is None or self.cardinalityMax >= 2

    @property
    def isTarget(self):
        return (
            self.association.isBinary
            and self.association.roles[1] == self
        )

    @property
    def isSource(self):
        return (
            self.association.isBinary
            and self.association.roles[0] == self
        )

    @property
    def position(self):
        # type: () -> RolePosition
        if self.association.isBinary:
            if self.association.roles[0] == self:
                return 'source'
            else:
                return 'target'
        else:
            raise NotImplementedError(
                'role.position() not implemented'
                ' for n-ary association')

    def __str__(self):
        return '%s::%s' % (self.association.name, self.name)

    def acceptCardinality(self, actualCardinality):
        if actualCardinality < self.cardinalityMin:
            return False
        elif (self.cardinalityMax is not None
              and actualCardinality > self.cardinalityMax):
            return False
        else:
            return True


class AssociationClass(Class, Association):
    """
    Association classes.
    """
    def __init__(self,
                 name, model, isAbstract=False, superclasses=(),
                 package=None,
                 lineNo=None, description=None, astNode=None):
        # Use multi-inheritance to initialize the association class
        Class.__init__(self,
            name=name,
            model=model,
            isAbstract=isAbstract,
            superclasses=superclasses,
            package=package,
            lineNo=lineNo,
            description=description,
            astNode=astNode)
        Association.__init__(self,
            name=name,
            model=model,
            kind='associationclass',
            package=package,
            lineNo=lineNo,
            description=description, astNode=astNode)
        # But register the association class apart and only once, to avoid
        # confusion and the duplicate in the associations and classes lists
        del self.model._plainClassNamed[name]
        del self.model._plainAssociationNamed[name]
        self.model._associationClassNamed[name] = self

    def isPlainAssociation(self):
        return False

    def isPlainClass(self):
        return False


METAMODEL = Metamodel(
    id='cl',
    label='class',
    extension='.cls',
    modelClass=ClassModel
)

MetamodelDependency(
    sourceId='cl',
    targetId='gl',
    optional=True,
    multiple=True,
)

