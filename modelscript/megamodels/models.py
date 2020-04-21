# coding=utf-8
"""Define models with their features.
"""

from abc import abstractmethod, ABCMeta
from typing import Optional, List

from modelscript.megamodels.issues import WithIssueModel
from modelscript.base.metrics import (
    Metrics,
    Metric)
from modelscript.megamodels.megamodels import (
    MegamodelElement)
from modelscript.megamodels.elements import ModelElement
from modelscript.metamodels.textblocks import WithTextBlocks

Metamodel = 'Metamodel'
ModelSourceFile = 'ModelSourceFile'
ModelDependency = 'ModelDependency'
MetamodelDependency = 'MetamodelDependency'

__all__ = (
    'Model',
    'Placeholder',
)

DEBUG = 2


class Model(
        MegamodelElement,
        ModelElement,
        WithIssueModel,
        WithTextBlocks,
        metaclass=ABCMeta):
    """The root class for all models.

    Basically a model has:
    * a name,
    * possibly a source file if the model is the result
      of parsing this file,
    * a metamodel
    * an issue box. This issue box stores "semantical"
      errors found on the model, while the source
      file issue box stores "syntax" errors.
      The _issueBox has as a parent the sourceFile'
      issue box if any.
    """

    name: str
    """Name of the model"""

    source: Optional[ModelSourceFile]
    """Source file from where the model originates or None
    if the model has been created in some other ways
    """

    kind: str
    """A keyword like "conceptual", "preliminary', ...
    Could be '' if no kind specified
    """

    status: str
    """a keyword like "draft" | "" | "consolidated"""



    def __init__(self) -> None:

        self.name = ''
        # set later
        # If the model originates from a sourceFile
        # then set by parseToFillImportBox

        self.source = None
        # Set later if build from a ModelSourceFile.
        # Set in the constructor of ModelSourceFile

        MegamodelElement.__init__(self)

        WithIssueModel.__init__(self, parents=[])
        # Parents set at the same time as source

        ModelElement.__init__(self, self)

        WithTextBlocks.__init__(self)

        self.kind = ''
        # Set later.
        # If the model is from a sourceFile then
        # this attribute
        # is set by parseToFillImportBox

        self.status = ''
        # Set later

        # FIXME:3 add model dependencies.
        # First check the code below (outDep, etc.)
        # The source contains importBox, but
        # here we should have dependency box

    @property
    @abstractmethod
    def metamodel(self) -> Metamodel:
        # Makes it sure that subclasses define metamodel()
        # This should never happened if all model classes
        # are properly defined.
        raise NotImplementedError( # raise:OK
            'INTERNAL ERROR: The model class "%s"'
            ' does not redefine the method metamodel()' % self.name
        )

    @property
    def label(self):
        name = '_' if self.name == '' else self.name
        if self.source is None:
            return '%s:%s()' % (
                name,
                self.metamodel.id)
        else:
            return '%s:%s(%s)' % (
                name,
                self.metamodel.id,
                self.source.label)

    # @property
    # def originLabel(self):
    #     return self.label

    @property
    def metrics(self) -> Metrics:
        ms = Metrics()
        ms.add(
            Metric('model descriptor', len(self.descriptors))
        )
        ms.addMetrics(self.textBlocksMetrics)
        return ms

    @property
    def fullMetrics(self) -> Metrics:
        ms = self.metrics
        if self.source is not None:
            ms.addMetrics(self.source.metrics)
        return ms

    @property
    def text(self):
        return self.metamodel.modelPrinterClass(self).do()

    def resolve(self):
        """
        Resolve the model. This is useful for instance to create actual
        references to model element by replacing symbols. What this
        method do is metamodel dependent. All sub methods have to call
        this method. This method solve references in text blocks.
        """
        if DEBUG >= 1:
            _ = (' RESOLVE MODEL'+self.label+' ').center(70, '.')
            print(('MOD: '+_))
        self.resolveTextBlocks()

    def finalize(self):
        if DEBUG>=1:
            _ = (' FINALIZE MODEL'+self.label+' ').center(70, '.')
            print(('MOD: '+_))
        self.check()

    def str(self,
             method='do',
             config=None):
        printer_class = self.metamodel.modelPrinterClass
        printer = printer_class(
            theModel=self,
            config=config
        )
        try:
            the_method = getattr(printer_class, method)
            return the_method(printer)
        except AttributeError:
            raise NotImplementedError(  # raise:OK
                "INTERNAL ERROR: "
                "Class `{}` does not implement `{}`".format(
                    printer_class.__class__.__name__,
                    method))

    def theModel(self, targetMetamodel, acceptNone=False):
        lm = self.usedModels(targetMetamodel=targetMetamodel)
        if len(lm) == 0:
            if acceptNone:
                return None
            else:
                raise ValueError(  # raise:TODO:2
                    'No %s model found. Expected one.'
                    % targetMetamodel.label)
        elif len(lm) >= 2:
            raise ValueError(    # raise:TODO:2
                '%i %s models found. Expected one.'
                % (len(lm), targetMetamodel.label))
        else:
            return lm[0]

    def usedModels(self,
                   targetMetamodel=None,
                   metamodelDependency=None):
        outdeps=self.outDependencies(
            targetMetamodel=targetMetamodel,
            metamodelDependency=metamodelDependency)
        return [dep.targetModel for dep in outdeps]

    def clientModels(self,
                     targetMetamodel=None,
                     metamodelDependency=None):
        indeps = self.outDependencies(
            targetMetamodel=targetMetamodel,
            metamodelDependency=metamodelDependency)
        return [ dep.targetModel for dep in indeps]

    def outDependencies(self,
                        targetMetamodel: Optional[Metamodel] = None,
                        metamodelDependency=None)\
            -> List[ModelDependency]:
        """Returns the dependencies starting from this
        dependency filtered either by targetMetamodel,
        or by metamodelDependency.
        """

        # select all out dependencies from self
        from modelscript.megamodels import Megamodel
        all_deps = Megamodel.modelDependencies(source=self)
        if targetMetamodel is None:
            deps = all_deps
        else:
            deps = [
                dep for dep in all_deps
                if (
                    dep.targetModel.metamodel
                    == targetMetamodel)
            ]
        if metamodelDependency is None:
            return deps
        else:
            return [
                dep for dep in deps
                # could raise ValueError, but should not
                # raise:except:TODO:2
                if (dep.metamodelDependency
                    == metamodelDependency)
            ]

    @property
    def outgoingDependencies(self):
        return self.outDependencies()


    def inDependencies(self,
                       sourceMetamodel: Optional[Metamodel] = None)\
            -> List[ModelDependency]:
        """Returns the dependencies towards from this
        dependency filtered either by targetMetamodel,
        or by metamodelDependency.
        """
        from modelscript.megamodels import Megamodel
        deps = Megamodel.modelDependencies(target=self)
        if sourceMetamodel is None:
            return deps
        return [
            dep for dep in deps
            if (dep.sourceModel.metamodel
                == sourceMetamodel)
        ]

    @property
    def incomingDependencies(self):
        return self.inDependencies()


    def checkDependencies(self,
                          metamodelDependencies:
                          List[MetamodelDependency] = None) \
            -> None:
        """ Check if this model has not problems with
        dependencies.
        Do nothing if this is not the case. Otherwise
        raise a ValueError.
        This could be because there is no corresponding
        metamodel dependency for a model metamodel.
        This could also due because of too much outgoing
        dependency of the same typel.
        This could be because of missing dependency.
        """

        # -- metamodels dependencies to be check against
        from modelscript.megamodels import Megamodel
        if metamodelDependencies is None:
            mm_deps = Megamodel.metamodelDependencies(
                source=self.metamodel)
        else:
            mm_deps = metamodelDependencies

        # -- perform check for all metamodels dependencies
        for mm_dep in mm_deps:
            # all model dependencies of type mm_dep
            # starting from here
            m_deps = self.outDependencies(
                metamodelDependency=mm_dep)
            if len(m_deps) == 0 and not mm_dep.optional:
                raise ValueError(  # raise:TODO:2
                    'Reference to a %s model'
                    ' is model is missing'
                    % mm_dep.targetMetamodel)
            elif len(m_deps) >= 0 and not mm_dep.multiple:
                raise ValueError(  # raise:TODO:2
                    'Too many %s models associated'
                    ' with this model'
                    % mm_dep.targetMetamodel)
            else:
                pass

    def __str__(self):
        return '<model:%s>' % self.label

    def __repr__(self):
        return '<model:%s>' % self.label


class Placeholder(object):
    """Placeholder waiting to be substituted with a later value.
    Used just to put some symbol value in some model
    waiting for some kind of symbol resolution. This will be
    replaced by an actual reference to a model element.
    Placerholder are created during the "fillModel" phase and
    are replaced by actual values during the "resolve" phase.
    """
    def __init__(self, placeholderValue, astNode=None, type=None):
        self.placeholderValue = placeholderValue
        self.astNode = astNode
        self.type = type

    def __str__(self):
        return ('***%s(%s)***' %(
            self.placeholderValue,
            self.type))
