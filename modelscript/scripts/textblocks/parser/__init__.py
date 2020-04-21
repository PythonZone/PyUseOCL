# # coding=utf-8

from typing import Any, Optional

from modelscript.base.exceptions import (
    UnexpectedCase)
from modelscript.metamodels.textblocks import (
    TextBlock,
    TextLine,
    PlainText,
    TextReference)
#  import modelscript.metamodels.textblocks in script due to cycle
from modelscript.metamodels.glossaries import GlossaryModel


def astTextBlockToTextBlock(
        container: 'SourceModelElement',
        astTextBlock: Optional['grammar.TextBlock']) \
        -> Optional[TextBlock]:
    """Creates a semantic TextBlock from syntactic textBlock.

    Args:
        container: source element logically containing the TextBlock.
            This could be a class, an attribute or whatever.
        astTextBlock:  the part of the ast corresponding to the
            documentation to parse or none if there is no such part.
            None can by due to an optional documentation grammar rule.

    Returns:
        The newly created TextBlock or None if astTextBlock was None.

    """
    if astTextBlock is None:
        # ---- The syntactic part is None so just return None
        return None

    else:

        # ---- Create a new TextBlock (a semantic element) ----
        text_block = TextBlock(
            container=container,
            astTextBlock=astTextBlock)

        # ---- Add a (semantic) TextLine for each line found ----
        for ast_text_line in astTextBlock.textLines:
            text_line = TextLine(text_block, ast_text_line)
            # ---- Create PlainText segments and text references
            for ast_text_token in ast_text_line.textTokens:
                type_ = ast_text_token.__class__.__name__
                if type_ == 'PlainText':
                    PlainText(
                        textLine=text_line,
                        text=ast_text_token.text,
                        astPlainText=ast_text_token)
                elif type_ == 'TextReference':
                    TextReference(
                        textLine=text_line,
                        text=ast_text_token.text,
                        astTextReference=ast_text_token)
                else:
                    raise UnexpectedCase(  # raise:OK
                        'Type %s not supported' % type_)

        #TODO:2 add a reference to this text block into the model
        # here container.model is the model we need
        # add something like:
        #      container.model.textBlocks.append(text_block)
        return text_block

GRAMMAR='''
'''