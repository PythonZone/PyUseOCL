# coding=utf-8

"""
Parser of subset of the soil language and of the sex format.
The same parser can parse both:
* .soil files, that is USE .soil files
* .sex files, that are an internal format merging .soil files with trace results
See the 'merge' module for more information.


SOIL Syntax
http://useocl.sourceforge.net/wiki/index.php/SOIL

            s ::=                                     (statement)
(P)            v := new c [(nameExpr)] |              (object creation)
(I)            create v : c
(I)            v := new c [(nameExpr)] between (participant1,participant2,...) |
                                                      (link object creation)
(I)            destroy e  |                           (object destruction)
(I)            insert (e1; ... ; en) into a j |       (link insertion)
(I)            delete (e1; ... ; en) from a j |       (link deletion)
(I)            e1.a := e2 |                           (attribute assignment)
(I)            v := e |                               (variable assignment)
               e1.op(e2; ... ; en) |                  (operation call)
               v := e1.op(e2; ... ; en) |             (operation call with result)
               [begin] s1; ... ; sn [end] [declare v1 : t1; ... ; vn : tn] |
                                                      (block of statements)
               if e then s1 [else s2] end |           (conditional execution)
               for v in e do s end                    (iteration)

"""

# Scn: Assertion
# TODO: add @assert inv X::Y is True|False   -> check -d -v
# TODO: add @assert inv * is True|False      -> check -d -v
# TODO: add @assert query expr is result     -> ??


# TODO: add proper mamangement for Warning and Errors
# TODO: check if a USE OCL run before parsin is necessary/better

from __future__ import unicode_literals, print_function, absolute_import, division

import os
import re

from typing import Text, Optional, Union, List

# DEBUG=3
DEBUG=0

from abc import ABCMeta, abstractproperty, abstractmethod

from modelscripts.use.engine import USEEngine

from modelscripts.sources.sources import (
    ModelSourceFile,
)
# from modelscripts.sources.errors import (
#     Issue,
#     Level,
# )

from modelscripts.scripts.scenarios.printer import (
    ScenarioPrinter,
)

from modelscripts.metamodels.classes import (
    ClassModel,
)

from modelscripts.metamodels.usecases import (
    UsecaseModel,
    Actor,
    Usecase,
)
from modelscripts.metamodels.scenarios import (
    ScenarioModel,
    ActorInstance,
    ContextBlock,
)
from modelscripts.metamodels.scenarios.blocks import (
    UsecaseInstanceBlock,
    TopLevelBlock,
)
from modelscripts.metamodels.scenarios.operations import (
    ObjectCreation,
    ObjectDestruction,
    LinkCreation,
    #TODO: implement link destruction
    LinkObjectCreation,
    AttributeAssignment,
    Check,
    Query,
)

from modelscripts.metamodels.scenarios.evaluations import (
    ScenarioEvaluation,
)
from modelscripts.metamodels.scenarios.evaluations.operations import (
    _USEImplementedQueryEvaluation,
    _USEImplementedCheckEvaluation,
    InvariantValidation, \
    InvariantViolation,
    CardinalityViolation,
    CardinalityViolationObject,
)

from modelscripts.metamodels.permissions import (
    PermissionModel
)

__all__ = (
    'SoilSource',
    'SexSource',
)


def isEmptySoilFile(file):
    with open(file) as f:
        content = f.read()
    match = re.search(r'(^ *!)|(^ *open)', content, re.MULTILINE)
    return match is None


#TODO: add support for use interpreter errors !!!


class _PolymorphicSource(ModelSourceFile):
    __metaclass__ = ABCMeta

    def __init__(self,
                 evaluateScenario,
                 soilFileName,
                 sexFileName,
                 classModel,
                 usecaseModel=None,
                 permissionModel=None,
                 parsePrefix='^',
                 preErrorMessages=()):
        #type: (bool,Text, Optional[Text], ClassModel, Optional[UsecaseModel], Optional[PermissionModel], Text, List[Text]) -> None
        """
        Create a soil/sex source from the given file.
        See subclasses

        Args:
            evaluateScenario:
                If true, the scenario is executed with USE
                and it will have an scenarioEvaluation associated.
            soilFileName:
                The name of the soil file. If evaluateScenario the
                sex file generated (generated previously) will
                be parsed.
            sexFileName:
                The name of the sex file to be parsed actually instead
                of the soilFile. Set only if evaluateScenario. Otherwise
                sexFileName will be none
            classModel:
                The class model used to resolve Classes, Associations, etc.
                This model is required as it makes not sense to parse the
                soil file without the use file.
            usecaseModel:
                A use case model is necessary only if
                there are directives for actor instance
                and usecase instance.
                Can be used without evaluateScenario.
            permissionModel:
                In case of evaluateScenario used to check accesses.
            parsePrefix:
                See subclasses. Prefix is necessary for parsing sex file.
                Only used if evaluateScenario.
            preErrorMessages:
                If not [] these errors with be added to the list of
                error and nothing else will happen (no file reading)

        """
        self.evaluateScenario=evaluateScenario #type: bool
        self.soilFileName=soilFileName #type: Text
        self.sexFileName=sexFileName #type: Optional[Text]
        self.classModel=classModel #type:ClassModel
        self.usecaseModel=usecaseModel #type:Optional[UsecaseModel]
        self.permissionModel=permissionModel #type:Optional[PermissionModel]
        self._parsePrefix=parsePrefix

        super(_PolymorphicSource, self).__init__(
            fileName=soilFileName,
            realFileName=sexFileName,
            preErrorMessages=preErrorMessages)  #realFileName is ignore if None

        #--- create a scenario to contain the result -----------
        self.scenario = ScenarioModel( #type:ScenarioModel   # TODO -> model
            source=self,
            classModel=classModel,
            name=None,
            usecaseModel=usecaseModel,
            permissionModel=permissionModel,
            file=self.soilFileName)

        if self.isValid:
            self._parse(self._parsePrefix)

            if self.evaluateScenario:
                ScenarioEvaluation.evaluate(self.scenario)

    @property
    def model(self):
        return self.scenario

    @property
    def usedModelByKind(self):
        _={}
        if self.classModel is not None:
            _['cl'] = self.classModel
        if self.usecaseModel is not None:
            _['uc'] = self.usecaseModel
        if self.permissionModel is not None:
            _['pm'] = self.permissionModel
        return _

    def printStatus(self):
        """
        Print the status of the file:

        * the list of errors if the file is invalid,
        * a short summary of entities (classes, attributes, etc.) otherwise
        """
        if self.isValid:
            p=ScenarioPrinter(
                scenario=self.scenario,
                displayLineNos=True,
                displayBlockSeparators=True,
                displayEvaluation=True,
                originalOrder=True)
            print(p.do())
        else:
            print('%s error(s) in the model' % len(self.issues))
            for e in self.issues:
                print(e)

    def _parse(self, prefix):

        class _S(object):
            """
            Current state of the parser.
            Required for _getBlock
            """
            original_line=""

            # Always the line number in the soil file, the only file seen be the user
            line_no=0
            # The line number in the sex file or None if parsing a soil file
            sex_line_no=None

            main_block = None
            # type: Optional[Union[UsecaseInstanceBlock, TopLevelBlock]]
            # current main block
            # null if no toplevel block have been created yet

            context_block = None
            # type: Optional[ContextBlock]
            #: can be nested in other blocks

        def _getBlock():
            """
            Create a toplevel block if necessary (None)
            otherwise reuse the existing one.
            """
            if _S.context_block is not None:
                # inside a context block
                return _S.context_block
            else:
                if _S.main_block is None:
                    # no block, create one
                    _S.main_block = TopLevelBlock(
                        scenario=self.scenario,
                        lineNo=_S.line_no
                    )
                return _S.main_block


        begin = prefix + r' *'
        end = ' *$'



        if DEBUG>=1:
            print('\nParsing %s with %s usecase model\n' % (
                self.soilFileName,
                'no' if self.usecaseModel is None else 'a'
            ))

        last_check_evaluation=None
        current_cardinality_info=None
        current_invariant_violation=None
        current_query_evaluation=None

        for (line_index, line) in enumerate(self.sourceLines):

            _S.original_line = line
            line = line.replace('\t',' ')


            # Compute the line number
            if self.evaluateScenario:  #'sex':
                _S.sex_line_no = line_index + 1
                _m=re.match(r'^(?P<lineno>\d{5}):', line)
                if _m:
                    # in case of sex file update the line no from the line begining
                    _S.line_no=int(_m.group('lineno'))
                else:
                    # This is a result line. |||||: Do nothing.
                    # The same line number to the soil will be reused.
                    pass
            else:
                _S.line_no = line_index + 1

            if DEBUG>=2:
                if self.evaluateScenario: #'sex':
                    print ('#%05i <- %05i : %s' % (
                        _S.line_no,
                        _S.sex_line_no,
                        _S.original_line,
                    ))
                else:
                    print('#%05i : %s' % (
                        _S.line_no,
                        _S.original_line,
                    ))

            #---- blank lines ---------------------------------------------
            r = prefix+''+end
            m = re.match(r, line)
            if m:
                continue



            #---- query
            r = begin+'(?P<kind>\?\??) *(?P<expr>.*)'+end
            m = re.match(r, line)
            if m:
                query=Query(
                    block=_getBlock(),
                    expression=m.group('expr'),
                    verbose=m.group('kind')=='??',
                    lineNo=_S.line_no,
                )
                if self.evaluateScenario:
                    current_query_evaluation = _USEImplementedQueryEvaluation(
                        blockEvaluation=None,
                        op=query)
                continue


            #-------------------------------------------------
            # directives
            #-------------------------------------------------

            if re.match(begin+r'--', line):
                #---- -- @scenario XXX
                r = begin+'-- *@scenario( +model?) +(?P<name>\w+)'+end
                m = re.match(r, line)
                if m:
                    if self.scenario.name is not None:
                        raise ValueError(
                            'Error at line #%i: '
                            'scenario named again' % _S.line_no)
                    self.scenario.name=m.group('name')
                    self.scenario.lineNo=_S.line_no,

                    # TODO: raise an effor if some block has already there
                    continue

                #---- -- @actorinstance XXX : YYY
                r = prefix+'-- *@actori +(?P<name>\w+) *: *(?P<actor>\w+)'+end
                m = re.match(r, line)
                if m:
                    if self.usecaseModel is None:
                        print('Warning at line %i: no use case model provided. Directive ignored' % (
                            _S.line_no,
                        ) )
                        continue
                    #--- instance
                    iname=m.group('name')
                    if iname in self.scenario.actorInstanceNamed:
                        raise ValueError(
                            'Error at line %i: actor instance "%s" already exist' % (
                            _S.line_no,
                            iname,
                        ))
                    #--- actor
                    aname=m.group('actor')
                    if aname not in self.scenario.usecaseModel.actorNamed:
                        raise ValueError('Error at line %i: actor "%s" does not exist' % (
                            _S.line_no,
                            aname,
                        ))
                    a=self.scenario.usecaseModel.actorNamed[aname]
                    ai = ActorInstance(
                        scenario=self.scenario,
                        name=iname,
                        actor=a,
                        lineNo=_S.line_no
                    )
                    self.scenario.actorInstanceNamed[iname]=ai
                    continue

                #---- -- @context
                r = prefix+'-- *@context'+end
                m = re.match(r, line)
                if m:
                    if _S.main_block is not None:
                        # TODO: this limitation might be removed
                            raise ValueError(
                            'Error at line %i: context cannot be nested in other block' % (
                                _S.line_no,
                            ))
                    if _S.context_block is None:
                        _S.context_block=ContextBlock(
                            self.scenario,
                            lineNo=_S.line_no,
                        )
                    continue

                #---- -- @endcontext
                r = prefix+'-- *@endcontext'+end
                m = re.match(r, line)
                if m:
                    if _S.context_block is None:
                        raise ValueError(
                            'Error at line %i: context is not open' % (
                                _S.line_no,
                            ))
                    _S.context_block=None
                    continue

                #---- -- @uci
                r = (prefix
                     +r'-- *@uci'
                     +r' +(?P<name>\w+)'
                     # +r' *(: *(?P<actor>\w+))?'  # TODO: add online definition
                     +r' *(?P<usecase>\w+)'
                     +end)
                m = re.match(r, line)
                if m:
                    if self.usecaseModel is None:
                        print('Warning at line %i: no use case model provided. Directive ignored' % (
                            _S.line_no,
                        ) )
                        continue
                    if _S.context_block is not None:
                        raise ValueError(
                            'Error at line %i: context is open' % (
                                _S.line_no,
                            ))
                    ainame=m.group('name')
                    if ainame not in self.scenario.actorInstanceNamed:
                        raise ValueError(
                            'Error at line %i: actori "%s" is not defined' % (
                                _S.line_no,
                                ainame,
                            ))
                    ai=self.scenario.actorInstanceNamed[ainame] #type: ActorInstance
                    a=ai.actor #type: Actor
                    ucname=m.group('usecase')
                    if ucname not in self.scenario.usecaseModel.system.usecaseNamed:
                        raise ValueError(
                            'Error at line %i: usecase "%s" is not defined' % (
                                _S.line_no,
                                ucname,
                            ))
                    uc=self.scenario.usecaseModel.system.usecaseNamed[ucname] #type: Usecase
                    if uc not in a.usecases:
                        raise ValueError(
                            'Error at line %i: actor %s cannot perform usecase %s' % (
                                _S.line_no,
                                a.name,
                                uc.name,
                            ))
                    _S.main_block=UsecaseInstanceBlock(
                        scenario=self.scenario,
                        actorInstance=ai,
                        useCase=uc,
                        lineNo=_S.line_no,
                    )
                    continue

                #---- -- @enduci
                r = (prefix
                     +r'-- *@enduci'
                     +end)
                m = re.match(r, line)
                if m:
                    if self.usecaseModel is None:
                        print('Warning at line %i: no use case model provided. Directive ignored' % (
                            _S.line_no,
                        ) )
                        continue
                    if not isinstance(_S.main_block, UsecaseInstanceBlock):
                        raise ValueError(
                            'Error at line %i: no opened usecase instance' % (
                                _S.line_no,
                            ))
                    _S.main_block=None
                    continue



                #--- unrecognized directive ----------------------------------------
                r = (begin+'-- *@.*'+end)
                m = re.match(r, line)
                if m:
                    print('Warning at line %i: directive not recognized: %s' % (
                        _S.line_no,
                        _S.original_line
                    ))
                    continue

                #---- comments -------------------------------------------------
                r = prefix+'--.*'+end
                m = re.match(r, line)
                if m:
                    continue



            # -------------------------------------------------
            # ! operations
            # -------------------------------------------------

            if re.match(begin + r'!', line):

                #--- object creation (create x : C) ---------------------
                r = begin+r'! *create +(?P<name>\w+) *: *(?P<className>\w+)'+end
                m = re.match(r, line)
                if m:
                    variable=m.group('name')
                    classname=m.group('className')
                    id=None
                    if DEBUG:
                        print('%s := new %s' % (variable,classname))

                    ObjectCreation(
                        block=_getBlock(),
                        variableName=variable,
                        class_=self.classModel.classNamed[classname],
                        id=id,
                        lineNo=_S.line_no
                    )
                    continue

                #--- object creation(x := new C('lila') --------------------
                r = (begin
                     + r'! *(?P<name>\w+) *:= *new +(?P<className>\w+)'
                     + ' *( *\( *(\'(?P<id>\w+)\')? *\))?'
                     + end)
                m = re.match(r, line)
                if m:
                    variable=m.group('name')
                    classname=m.group('className')
                    id=m.group('id')
                    if DEBUG:
                        print('%s := new %s : %s' % (variable,id,classname))

                    ObjectCreation(
                        block=_getBlock(),
                        variableName=variable,
                        class_=self.classModel.classNamed[classname],
                        id=id,
                        lineNo=_S.line_no
                    )
                    continue

                #--- attribute assignement ----------------------------------------
                r = (begin
                        + r'! *(set )? *(?P<name>\w+) *'
                        + r'\. *(?P<attribute>\w+) *'
                        + r':= *(?P<expr>.*) *'
                        + end )
                # r2 = (begin
                #         + r'create +(?P<name>\w+) *'
                #         + r'\. *(?P<attribute>\w+) *'
                #         + r':= *(?P<value>.*)'
                #         + end )
                m = re.match(r, line)
                if m:
                    variable=m.group('name')
                    attribute=m.group('attribute')
                    expression=m.group('expr')
                    if DEBUG:
                        print ('%s.%s := %s' % (
                            variable, attribute, expression))
                    AttributeAssignment(
                        block=_getBlock(),
                        variableName=variable,
                        attributeName=attribute,
                        expression=expression,
                        lineNo=_S.line_no,
                    )
                    continue

                #--- link creation-------------------------------------------------
                r = (begin
                     + r'! *insert *\((?P<names>[\w, ]+)\) *'
                     + r'into +'
                     + r'(?P<associationName>\w+)'
                     + end )
                m = re.match(r, line)
                if m:
                    names = [
                        n.strip()
                        for n in m.group('names').split(',')]
                    assoc=self.classModel.associationNamed[m.group('associationName')]
                    if DEBUG:
                        print('new (%s) : %s' % (
                            ','.join(names),
                            assoc.name ))
                    LinkCreation(
                        block=_getBlock(),
                        names=names,
                        association=assoc,
                        id=None,
                        lineNo=_S.line_no
                    )
                    continue

                #--- link object creation (form1 ) --------------------------------
                # ex: create r1 : Rent between (a1,b2)
                r = (begin
                     + r'! *create +(?P<name>\w+) *: *(?P<assocClassName>\w+) +'
                     + r'between +\((?P<names>[\w, ]+)\) *'
                     + end )
                m = re.match(r, line)
                if m:
                    assoc_class_name = m.group('assocClassName')
                    name = m.group('name')
                    names = m.group('objectList').replace(' ','').split(',')
                    ac = self.classModel.associationClassNamed[assoc_class_name]
                    if DEBUG:
                        print(('new %s between (%s)' % (
                            assoc_class_name,
                            ','.join(names))
                        ))
                    LinkObjectCreation(
                        block=_getBlock(),
                        variableName=name,
                        names=names,
                        id=None,
                        associationClass=ac,
                        lineNo=_S.line_no
                    )
                    continue

                #--- link object creation (form2 ) --------------------------------
                # v1 := new Rent('lila') between (r1,a2,v3)
                r = (begin
                     + r'! *(?P<name>\w+) *:='
                     + r' *new +(?P<assocClassName>\w+)'
                     + r' *( *\( *(\'(?P<id>\w+)\')? *\))?'
                     + r' *between +\((?P<objectList>[\w, ]+)\) *'
                     + end )
                m = re.match(r, line)
                if m:
                    assoc_class_name = m.group('assocClassName')
                    name = m.group('name')
                    id = m.group('id')
                    names = m.group('objectList').replace(' ','').split(',')
                    ac = self.classModel.associationClassNamed[assoc_class_name]
                    if DEBUG:
                        print(("new %s('%s') between (%s)" % (
                            assoc_class_name,
                            id,
                            ','.join(names)
                        )))
                    LinkObjectCreation(
                        block=_getBlock(),
                        variableName=name,
                        names=names,
                        id=id,
                        associationClass=ac,
                        lineNo=_S.line_no
                    )
                    continue


                #--- object (or link object) destruction --------------------------
                r = (begin
                     + r'! *destroy +(?P<name>\w+)'+ end )
                m = re.match(r, line)
                if m:
                    name = m.group('name')
                    if DEBUG:
                        print( 'delete object %s' % name )
                    ObjectDestruction(
                        block=_getBlock(),
                        variableName=name,
                    )
                    continue
                    # check if this is an regular object or a link object
                    # if name in self.state.objects:
                    #     del self.state.objects[name]
                    # else:
                    #     del self.state.linkObject[name]
                    # continue

                #--- link destruction ---------------------------------------------
                r = (begin
                     + r'! *delete *\((?P<objectList>[\w, ]+)\)'
                     + r' +from +(?P<associationName>\w+)'
                     + end )
                m = re.match(r, line)
                if m:
                    object_names = \
                        m.group('objectList').replace(' ', '').split(',')
                    association_name = m.group('associationName')
                    # link_name = '_'.join(object_names)
                    # del self.state.links[link_name]
                    print( 'delete link from %s between %s' % (
                        association_name,
                        object_names
                    ))
                    raise NotImplementedError('FIXME: implement link destruction')
                    # continue




            #==========================================================
            #  results of evaluation
            #==========================================================

            if self.evaluateScenario and line.startswith('|||||:'): # sex



                #------------------------------------------------------
                #  Cardinality evaluation
                #------------------------------------------------------

                r=(begin
                   +'checking structure...'
                   +end)
                # for some reason this appear as a blank line when
                # redirecting in a file. It was blank so the algorithm
                # below does not take it into account.
                m = re.match(r, line)
                if m:
                    continue

                r=(begin
                   +'checked structure in .*\.'
                   +end)
                # like "check structure...
                m = re.match(r, line)
                if m:
                    continue

                r=(begin
                    +r'Multiplicity constraint violation in association '
                    +r'`(?P<association>\w+)\':'
                    +end)
                m = re.match(r, line)
                if m:
                    current_cardinality_info={
                        'associationName':m.group('association')
                    }
                    continue

                if current_cardinality_info:
                    r=(begin
                        +r'  Object `(?P<object>\w+)\' of class '
                        +r'`(?P<sourceClass>\w+)\' is connected to '
                        +r'(?P<numberOfObjects>\d+) objects of class '
                        +r'`(?P<targetClass>\w+)\''
                        +end)
                    m = re.match(r, line)
                    if m:
                        current_cardinality_info['objectName']=m.group('object')
                        current_cardinality_info['sourceClassName']=(
                            m.group('sourceClass'))
                        current_cardinality_info['targetClassName'] = (
                            m.group('targetClass'))
                        current_cardinality_info['numberOfObjects'] = (
                            int(m.group('numberOfObjects')))
                        continue

                    r = (begin
                        +r'  at association end `(?P<role>\w+)\' but the '
                        +r'multiplicity is specified as'
                        +r' `(?P<cardinality>[^\']+)\'.'
                        +end)
                    m = re.match(r, line)
                    if m:
                        role=self.classModel.findRole(
                            current_cardinality_info['associationName'],
                            m.group('role'))
                        if role in last_check_evaluation.cardinalityEvaluations:
                            card_eval = (
                                last_check_evaluation.cardinalityEvaluations[role])
                        else:
                            card_eval = (
                                CardinalityViolation(
                                    checkEvaluation=last_check_evaluation,
                                    role=role,
                                ))
                        CardinalityViolationObject(
                            cardinalityViolation=card_eval,
                            violatingObject=(
                                current_cardinality_info['objectName']
                            ),
                            actualCardinality=(
                                current_cardinality_info['numberOfObjects']
                            )
                        )

                        continue



                #------------------------------------------------------
                #  Invariant evaluation
                #------------------------------------------------------

                r=(begin
                    +r'checked \d+ invariants in .*'
                    +end)
                m = re.match(r, line)
                if m:
                    current_invariant_violation=None
                    continue

                r=(begin
                   +'checking invariants...'
                   +end)
                # like "check structure...
                m = re.match(r, line)
                if m:
                    continue

                r=(begin
                    +r'checking invariant \(\d+\) `'
                    +r'(?P<context>\w+)'
                    +r'::(?P<invname>\w+)'
                    +r'\': '
                    +r'(?P<result>OK|FAILED)\.'
                    +end)
                m = re.match(r, line)
                if m:
                    invariant=self.classModel.findInvariant(
                        classOrAssociationClassName=m.group('context'),
                        invariantName=m.group('invname')
                    )
                    if m.group('result')=='OK':
                        InvariantValidation(
                            checkEvaluation=last_check_evaluation,
                            invariant=invariant,
                        )
                    else:
                        current_invariant_violation=InvariantViolation(
                            checkEvaluation=last_check_evaluation,
                            invariant=invariant,
                        )
                    continue

                if current_invariant_violation:

                    r=(begin
                        +r'Results of subexpressions:'
                        +end)
                    m = re.match(r, line)
                    if m:
                        continue



                    r=(begin
                        +r'Instances? of \w+ violating the invariant:'
                        +end)
                    m = re.match(r, line)
                    if m:
                        continue

                    r=(begin
                        +r'  -> Set\{(?P<expr>[\w ,]+)\}'
                        +r' : Set\((?P<type>\w+)\)'
                        +end)
                    m = re.match(r, line)
                    if m:
                        names=[ x.strip()
                                for x in m.group('expr').split(',')
                                if x!='' ]
                        current_invariant_violation.violatingObjects=names
                        current_invariant_violation.violatingObjectsType=m.group('type')
                        current_invariant_violation.violatingObjectType=m.group('type')
                        current_invariant_violation=None
                        continue

                    # WARNING: this rule MUST be after the one
                    # like -> Set\{ ...
                    # Otherwise this one catch the other one
                    r=(begin
                        +r'  -> (?P<expr>.*) : (?P<type>.*)'
                        +end)
                    m = re.match(r, line)
                    if m:
                        current_invariant_violation.resultValue=m.group('expr')
                        current_invariant_violation.resultType=m.group('type')
                        continue

                    # WARNING: this rule MUST be at the end
                    # Otherwise this one catch the other ones
                    r=(begin
                        +r'  (?P<expr>.*)'
                        +end)
                    m = re.match(r, line)
                    if m:
                        current_invariant_violation.subexpressions.append(
                            m.group('expr'))
                        continue

                #------------------------------------------------------
                #  query evaluation
                #------------------------------------------------------

                if current_query_evaluation:
                    r = (begin
                         + r'Detailed results of subexpressions:'
                         + end)
                    m = re.match(r, line)
                    if m:
                        current_query_evaluation.subexpressions=[]
                        continue

                    r=(begin
                        +r'  (?P<expr>.*)'
                        +end)
                    m = re.match(r, line)
                    if m:
                        current_query_evaluation.subexpressions.append(m.group('expr'))
                        continue

                    r=(begin
                        +r'-> (?P<expr>.*) : (?P<type>.*)'
                        +end)
                    m = re.match(r, line)
                    if m:
                        current_query_evaluation.resultValue=m.group('expr')
                        current_query_evaluation.resultType=m.group('type')
                        current_query_evaluation=None
                        continue


            # ---- check
            # WARNING: this rule MUST go after the rules thats starts
            # with 'check' something as this one will take precedence!
            r = begin + 'check *(?P<params>( -[avd])*)' + end
            m = re.match(r, line)
            if m:
                check = Check(
                    block=_getBlock(),
                    verbose='v' in m.group('params'),
                    showFaultyObjects='d' in m.group('params'),
                    all='a' in m.group('params'),
                    lineNo=_S.line_no,
                )
                if self.evaluateScenario:
                    last_check_evaluation = _USEImplementedCheckEvaluation(
                        blockEvaluation=None,
                        op=check)
                continue


            #---- unknown or unimplemented commands ---------------------------

            raise NotImplementedError(
                'Error at line #%i: cannot parse this line\n'
                   '"%s"' % (_S.line_no,_S.original_line)
            )


class SoilSource(_PolymorphicSource):
    """
    Source corresponding directly to the raw .soil source given
    as the parameter.
    WARNING: USE is *NOT* executed so some errors may
    be left undiscovered. Moreover, there is no cardinality check,
    no invariant checking, etc.
    From this soil source, one can get an object model.
    """
    def __init__(
            self,
            soilFileName,
            classModel,
            usecaseModel=None):
        #type: (Text, ClassModel) -> None
        super(SoilSource, self).__init__(
            evaluateScenario=False,
            soilFileName=soilFileName,
            sexFileName=None,
            classModel=classModel,
            usecaseModel=usecaseModel,
            parsePrefix='^',
            preErrorMessages=[])


class SexSource(_PolymorphicSource):
    """
    Source corresponding to a scenario execution with execution results.
    The .soil file merged with the trace of the execution of USE .soil file.
    """
    def __init__(
            self,
            soilFileName,
            classModel,
            usecaseModel=None,
            permissionModel=None):
        #type: (Text, ClassModel, Optional[UsecaseModel], Optional[PermissionModel]) -> None
        """
        The process is the following:

        1. The regular soilFileName is executed by USE OCL.
           After some merging this lead to a sex file with
           results of queries and checks computed by USE OCL.

        2. Then the scenario is abstractly executed
           (see ScenarioEvaluation).
           This allows to get the evaluation of operations
           that are not computed by USE OCL (update operations).

        All this results with a scenario which
        has an associated scenarioEvaluation.
        """
        assert classModel is not None
        assert classModel.source is not None  # TODO: it woudl be possible to parse/evaluate the scenario without .use

        # first execute USE with both the model and the scenario
        self.useFileName=classModel.source.fileName
        self.sexFileName=None #type: Optional[Text]
        e=self.__generateSex(soilFileName, classModel)
        # filled (or not) by __generateSex
        errors=[] if e is None else [e]


        super(SexSource, self).__init__(
            evaluateScenario=True,
            soilFileName=soilFileName,
            sexFileName=self.sexFileName,
            classModel=classModel,
            usecaseModel=usecaseModel,
            permissionModel=permissionModel,
            parsePrefix='^(\d{5}|\|{5}):',
            preErrorMessages=errors)

    def __generateSex(self, soilFileName, classModel):
        if not classModel.isValid:
            return '.use file is invalid'
        if not os.path.isfile(soilFileName):
            return 'File not found: %s' % self.soilFileName

        try:
            self.sexFileName = USEEngine.executeSoilFileAsSex(
                useFile=self.useFileName,
                soilFile=soilFileName)
        except IOError as e:   # TODO: add exception if required
            return 'Error during USE execution: %s' % str(e)
        return None