# coding=utf-8

"""
Parser package dealing with the parsing of stories.
This package provides a single class "StoryFiller".
This class allows, given an AST Story provided by the parser,
to get a "Story" AST.

This module allows to share this parsing among various parsers.

At the moment stories are used inside:
*   ObjectModel parser
*   Scenario parser.

Both modules call the StoryFiller to parse the subset(s) of
the AST corresponding to the story. Parameters makes it possible
to control a proprt subset of the (more general) language.
"""
from __future__ import print_function
from typing import Union, Text, Callable, Optional, List
from modelscripts.base.grammars import (
    ASTNodeSourceIssue
)
from modelscripts.base.issues import (
    Levels,
)
from modelscripts.scripts.textblocks.parser import (
    astTextBlockToTextBlock
)
from modelscripts.metamodels.classes.core import (
    dataTypeFromDataValueName
)
from modelscripts.metamodels.stories import (
    Story,
    TextStep,
    VerbStep,
    IncludeStep,
    AbstractStoryId
)
from modelscripts.metamodels.classes.types import EnumerationValue

from modelscripts.metamodels.stories.operations import (
    ObjectCreationStep,
    ObjectDeletionStep,
    SlotStep,
    LinkCreationStep,
    LinkDeletionStep,
    LinkObjectCreationStep,
    CheckStep,
    ReadStep
)

ISSUES={
    # 'DESCRIPTOR_TWICE':'st.syn.Descriptor.Twice',
    # 'ACTOR_NOT_FOUND':'st.syn.ActorInstance.NoActor',
    # 'ACTOR_INSTANCE_NOT_FOUND':'st.syn.Story.NoActorInstance',
    'BAD_STORY_ID':'st.syn.Story.BadInclude',
    'NO_INCLUDE':'st.syn.Story.NoInclude',
    'WRONG_INCLUDE':'st.syn.Story.WrongInclude',
    'NO_VERB':'st.syn.Story.NoVerb',
    'NO_ACTION':'st.syn.Story.NoAction',
    'NO_DEFINITION':'st.syn.Story.NoDefinition',
    'NO_CLASS_MODEL':'st.syn.Story.NoClassModel',
    'OBJECT_CLASS_NOT_FOUND':'st.syn.ObjectCreation.NoClass',
    'LINK_ASSOC_NOT_FOUND':'st.syn.LinkOperation.NoAssoc',
    'BAD_VALUE':'st.syn.Value.Bad',
    'NO_ENUM':'st.syn.Value.NoEnum',
    'NO_LITERAL':'st.syn.Value.NoLiteral',


}
def icode(ilabel):
    return ISSUES[ilabel]


GetStoryFun=Callable[[Text, Text], Optional[AbstractStoryId]]

class StoryFiller():
    """
    Creator of story AST models.
    Various parameters allow to tune what story features are valid
    or not. This allow reusing and tuning the parser in the context
    of "objects" and "scenarios".
    Virtual "check" statements are also added where appropriate.
    """

    def __init__(self,
                 model,
                 contextMessage,  # e.g. "object model" or "context"
                 allowDefinition,
                 allowAction,
                 allowVerb,
                 allowedIncludeKinds,
                 getStoryId,
                 astStory):
        #type: ('Model', Text, bool, bool, bool, List[Text], Optional[GetStoryFun], 'ASTStory') -> None
        """
        Create a StoryFiller with various parameters controlling what
        is accepted or not. The AST story to be parsed must be given.
        Use story() method to launch the parsing and get the result.

        The parameters "allowXXX" should speak for themselves.

        "getStoryId" is used only when allowIncluded not empty.
        Otherwise it can be None. This function is used when an
        "include" step is encountered. In this context the grammar
        rule "StoryId" is intentionally left abstract (two strings).
        The function getStoryId makes the mapping between the rule
        "StoryId" (in the "stories" grammar) and an actual StoryId object
        dependent on a client module. This allows the parsing of the
        "storyId" to be performed by the client module.
        In practice the "scenarios" parsing will provided a storyId
        function.
        If a valid StoryId cannot be created then the function
        return None. Note that this function just perform a syntactic
        validation, but no semantic ones. It will not check if the
        id corresponds to an actual story.

        getIsAllowedToBeIncluded is
        """
        self.astStory=astStory
        self.model=model

        self.contextMessage=contextMessage
        # Some string like "object model" or "context".
        # This string is used in error message.

        self.allowDefinition=allowDefinition
        #type: bool

        self.allowAction=allowAction
        # type: bool

        self.allowVerb=allowVerb
        # type: bool

        self.allowedIncludeKinds=allowedIncludeKinds
        # type: List[Text]
        # The kinds of storyId that are allowed.
        # For instance the 'scenarios' module set this
        # parameter to  ['fragment', 'context']. See this module
        # for an example and the usage of the parameter below to
        # see how it works.

        self.getStoryId=getStoryId
        #type: Optional[GetStoryFun]
        # This function must convert (kind,name) from the story syntax
        # to a story model. It must be defined when "allowIncluded".
        # It must be None otherwise. The function return None in case
        # of a syntatical error in the id.

        self.storyContainer=None
        #type: Optional['StoryContainer']
        # The container of this story if any. In practice this
        # will be a scenarios.StoryContainer but the type is not
        # specified here because the whole module has been designed
        # to be independent from the module scenarios.
        # This variable is set directly by the scenario parser
        # after having created the Story.
        # In practice this variable is used to give better label
        # to step and in particular to object step. It is useful
        # as well for the computation of superSubjects/subjectLabel

        self._is_check_needed=False
        # type: bool
        # This variable is "temporary" variable with respect to the
        # construction of Story. It is used by control the
        # creation of implicit CheckStep.
        # These steps should be created only if at least an operation
        # was issued before the potential check point.
        # Variable to keep along the creation of statements the
        # need to create an implict check statement. This is the
        # case when a new operation occur. Otherwise text block
        # do not count, and check statements set it to no.
        # See _add_check_if_needed.

        self._check_number=0
        # Just like _is_check_needed this is a "temporary" variable.
        # This is a counter incremented each time a step is created.
        # This allows to give a distinct number to each CheckStep in
        # the story.

    def story(self):
        #type: () -> Story
        self.story=Story(
            model=self.model,
            astNode=self.astStory)
        # textx => could be None even if it should not. => test
        if self.astStory is not None:
            for ast_step in self.astStory.steps:
                self._fill_step(
                    parent=self.story,
                    astStep=ast_step
                )
        self._add_check_if_needed(self.story, 'after', self.astStory)
        return self.story

    def _fill_step(self, parent, astStep):
        type_ = astStep.__class__.__name__
        if type_=='IncludeStep':
            step=self._fill_include_step(
                parent, astStep)
        elif type_=='TextStep':
            step=self._fill_text_step(
                parent, astStep)
        elif type_=='VerbStep':
            step=self._fill_verb_step(
                parent, astStep)
        elif type_=='ObjectCreationStep':
            step=self._fill_object_creation_step(
                parent, astStep)
        elif type_=='ObjectDeletionStep':
            step=self._fill_object_deletion_step(
                parent, astStep)
        elif type_=='SlotStep':
            step=self._fill_slot_step(
                parent, astStep)
        elif type_=='LinkOperationStep':
            step=self._fill_link_operation_step(
                parent, astStep)
        elif type_=='ReadStep':
            step=self._fill_read_step(
                parent, astStep)
        elif type_=='CheckStep':
            step=self._fill_check_step(
                parent, astStep)
        elif type_ == 'LinkObjectCreationStep':
            step=self._fill_link_object_creation_step(
                parent, astStep)
        else:
            raise NotImplementedError(
                'AST type not expected: %s' % type_)
        return step


    def _fill_include_step(self, parent, astStep):
        if len(self.allowedIncludeKinds)==0:
            ASTNodeSourceIssue(
                code=icode('NO_INCLUDE'),
                astNode=astStep,
                level=Levels.Fatal,
                message='Includes are forbidden in %s.' %
                        self.contextMessage)
        else:
            story_external_kind=astStep.storyId.kind
            story_external_name=astStep.storyId.name
            words=[story_external_kind, story_external_name]
            story_id=self.getStoryId(
                story_external_kind,
                story_external_name)
            if story_id is None:
                ASTNodeSourceIssue(
                    code=icode('BAD_STORY_ID'),
                    astNode=astStep,
                    level=Levels.Fatal,
                    message='Invalid include.')
            story_internal_kind = story_id.kind
            if story_internal_kind in self.allowedIncludeKinds:
                print('ZZ'*10, str(story_id))
                step = IncludeStep(
                    parent=parent,
                    storyId=story_id,
                    words=words,
                    astNode=astStep)
                return step
            else:
                ASTNodeSourceIssue(
                    code=icode('WRONG_INCLUDE'),
                    astNode=astStep,
                    level=Levels.Fatal,
                    message='This kind of includes is not allowed in %s' %
                               self.contextMessage)

    def _fill_text_step(self, parent, astStep):
        text_block = astTextBlockToTextBlock(
            container=parent,
            astTextBlock=astStep.textBlock)
        step = TextStep(
            parent=parent,
            textBlock=text_block,
            astNode=astStep)
        for sub_ast_step in astStep.steps:
            self._fill_step(
                parent=step,
                astStep=sub_ast_step
            )
        return step

    def _fill_verb_step(self, parent, astStep):
        if self.allowVerb:
            self._add_check_if_needed(
                parent,
                'before',
                astStep)
            step=VerbStep(
                parent=parent,
                subjectName=astStep.subjectName,
                verbName=astStep.verbName
            )
            for sub_ast_step in astStep.steps:
                self._fill_step(
                    parent=step,
                    astStep=sub_ast_step
                )
            self._add_check_if_needed(
                parent,
                'after',
                astStep)
            return step
        else:
            ASTNodeSourceIssue(
                code=icode('NO_VERB'),
                astNode=astStep,
                level=Levels.Fatal,
                message=(
                    'Statement not allowed in %s'
                    % self.contextMessage))

    def _fill_object_creation_step(self, parent, astStep):
        self._is_check_needed=True
        self._check_definition_action(astStep)
        self._check_class_model(astStep)
        on = astStep.objectDeclaration.name
        cn = astStep.objectDeclaration.type
        class_model=self.model.classModel

        c=class_model.class_(cn)
        if c is None:
            ASTNodeSourceIssue(
                code=icode('OBJECT_CLASS_NOT_FOUND'),
                astNode=astStep,
                level=Levels.Fatal,
                message=(
                    'Class "%s" does not exist.' % cn))
        else:
            step = ObjectCreationStep(
                parent=parent,
                isAction=astStep.action is not None,
                objectName=on,
                class_=c,
                astNode=astStep
            )
            return step

    def _fill_object_deletion_step(self, parent, astStep):
        self._is_check_needed=True
        self._check_definition_action(astStep)
        self._check_class_model(astStep)
        on = astStep.name

        step = ObjectDeletionStep(
                parent=parent,
                objectName=on,
                astNode=astStep
        )
        return step

    def _fill_slot_step(self, parent, astStep):

        def get_simple_value(ast_simple_value):
            simple_value_type = \
                ast_simple_value.__class__.__name__
            if simple_value_type=='EnumerationValue':
                #-- process EnumerationValue
                enum_name=ast_simple_value.enumerationName
                enum_literal_name=ast_simple_value.literalName
                class_model = self.model.classModel
                enum=class_model.enumeration(enum_name)
                if enum is None:
                    ASTNodeSourceIssue(
                        code=icode('NO_ENUM'),
                        astNode=astStep,
                        level=Levels.Fatal,
                        message='Enumeration "%s" does not exist.'
                                % enum_name)
                enum_literal=enum.literal(enum_literal_name)
                if enum_literal is None:
                    ASTNodeSourceIssue(
                        code=icode('NO_LITERAL'),
                        astNode=astStep,
                        level=Levels.Fatal,
                        message='Enumeration literal '
                                '"%s" does not exist.'
                                % enum_literal_name)

                return EnumerationValue(
                    literal=enum_literal)
            else:
                #-- process DataValue
                repr = ast_simple_value.repr
                # get the datatype, for example the instance
                # of DataType (see metamodel) with name
                # 'StringValue' or 'NullValue'.
                # The result is an instance of DataType.
                datatype=dataTypeFromDataValueName(
                    model=self.model.classModel,
                    datavalue_name=simple_value_type)
                try:
                    # Instanciate an object via the python
                    # implementation class.
                    pyclass=datatype.implementationClass
                    #TODO: optimize creation if required
                    # here we create a distinct
                    # datavalue for each occurence.
                    # This means that there will be
                    # many 5 integer values and many null
                    # values. Care should be taken with
                    # comparisons.
                    datavalue=pyclass(
                        stringRepr=repr,
                        type=datatype)
                    return datavalue
                except ValueError as e:
                    ASTNodeSourceIssue(
                        code=icode('BAD_VALUE'),
                        astNode=astStep,
                        level=Levels.Fatal,
                        message=e.message)

        self._is_check_needed=True
        self._check_definition_action(astStep)
        self._check_class_model(astStep)
        slot_decl = astStep.slotDeclaration
        step = SlotStep(
            parent=parent,
            isAction=astStep.action is not None,
            objectName=slot_decl.object,
            attributeName=slot_decl.attribute,
            value=get_simple_value(slot_decl.simpleValue),
            isUpdate=(astStep.action in ['update', 'modifie']),
            astNode=astStep
        )
        return step

    def _fill_link_operation_step(self, parent, astStep):
        self._is_check_needed=True
        self._check_definition_action(astStep)
        self._check_class_model(astStep)
        link_decl = astStep.linkDeclaration
        an = link_decl.association
        action = astStep.action
        class_model=self.model.classModel
        assoc=class_model.association(an)
        if assoc is None:
            ASTNodeSourceIssue(
                code=icode('LINK_ASSOC_NOT_FOUND'),
                astNode=astStep,
                level=Levels.Fatal,
                message=(
                    'Association "%s" does not exist.' % an))
        if action == 'create' or action is None:
            step = LinkCreationStep(
                parent=parent,
                isAction=(action == 'create'),
                sourceObjectName=link_decl.source,
                targetObjectName=link_decl.target,
                association=assoc,
                astNode=astStep
            )
            return step
        elif action == 'delete':
            step = LinkDeletionStep(
                parent=parent,
                sourceObjectName=link_decl.source,
                targetObjectName=link_decl.target,
                association=assoc,
                astNode=astStep
            )
            return step
        else:
            raise NotImplementedError(
                'Action not expected: %s' % action)

    def _fill_link_object_creation_step(self, parent, astStep):
        self._is_check_needed=True
        self._check_definition_action(astStep)
        self._check_class_model(astStep)
        ast_decl=astStep.linkObjectDeclaration
        lo_name = ast_decl.name
        ac_name = ast_decl.associationClass
        class_model=self.model.classModel

        ac=class_model.associationClass(ac_name)
        if ac is None:
            ASTNodeSourceIssue(
                code=icode('OBJECT_ASSCLASS_NOT_FOUND'),
                astNode=astStep,
                level=Levels.Fatal,
                message=(
                    'Association class "%s" does not exist.' % ac_name))
        else:
            step = LinkObjectCreationStep(
                parent=parent,
                isAction=astStep.action is not None,
                linkObjectName=lo_name,
                sourceObjectName=ast_decl.source,
                targetObjectName=ast_decl.target,
                associationClass=ac,
                astNode=astStep
            )
            return step

    def _fill_read_step(self, parent, astStep):
        step=ReadStep(
            parent=parent,
            astNode=astStep
        )
        return step

    def _fill_check_step(self, parent, astStep):
        self._check_number +=1
        step=CheckStep(
            parent=parent,
            number=self._check_number,
            position=None,
            astNode=astStep
        )
        self._is_check_needed=False
        return step

    def _check_class_model(self, astStep):
        if self.model.classModel is None:
            ASTNodeSourceIssue(
                code=icode('NO_CLASS_MODEL'),
                astNode=astStep,
                level=Levels.Fatal,
                message=('No class model is imported.' ))

    def _check_definition_action(self, astStep):
        """
        Check that the presence of the ast node "action"
        conforms to  allowAction and allowDefinition.
        This assume that all ast node provided has an
        action part.
        :param astStep:
        :return:
        """
        isAction = astStep.action is not None
        if not self.allowAction and isAction:
            ASTNodeSourceIssue(
                code=icode('NO_ACTION'),
                astNode=astStep,
                level=Levels.Fatal,
                message=(
                    '"%s" actions are forbidden in %s.' % (
                        astStep.action,
                        self.contextMessage)))
        if not self.allowDefinition and not isAction:
            ASTNodeSourceIssue(
                code=icode('NO_DEFINITION'),
                astNode=astStep,
                level=Levels.Fatal,
                message=(
                    'Definitions are forbidden in %s.' % (
                        self.contextMessage)))

    def _add_check_if_needed(self, parent, kind, astNode):
        if self._is_check_needed:
            self._check_number +=1
            CheckStep(
                parent=parent,
                number=self._check_number,
                position=kind,
                astNode=astNode
            )
        self._is_check_needed=False

    # TODO: add a check so that object model / context is at the top