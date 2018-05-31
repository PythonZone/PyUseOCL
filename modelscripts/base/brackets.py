


#######################################################
#
# This file is symlinked in _Sandbox
#
#######################################################





import re

class BracketedScript(object):

    SPACE_INDENT=4
    OPENING_BRACKET='{_'
    CLOSING_BRACKET='}_'
    EOL=';_'
    IS_BLANK_LINE='^ *(#.*)?$'
    IS_DOC_LINE_REGEX='^ *\|'
    CLOSING_DOC_LINE='|_'
    DOC_LINE_CONTENT=' *\| ?(?P<content>.*)\|_;_(}_;_)*$'


    def __init__(self, file, targetFilename=None):
        self.file=file
        self.lines=[line.rstrip('\n') for line in open(file)]
        self.bracketedLines=[]
        self.targetFilename=(
            self.file+'b' if targetFilename is None
            else targetFilename
        )

    def _is_blank_line(self, index):
        """ Check if the line is blank or a comment line """
        m=re.match(self.IS_BLANK_LINE, self.lines[index])
        return m is not None

    def _is_doc_line(self, index):
        m=re.match(self.IS_DOC_LINE_REGEX, self.lines[index])
        return m is not None

    def _terminate_doc_line(self, docLine):
        return  docLine +self.CLOSING_DOC_LINE


    @classmethod
    def extractDocLineText(cls, docLine):
        m = re.match(cls.DOC_LINE_CONTENT, docLine)
        assert m is not None
        return m.group('content')

    def _nb_spaces(self, index):
        m=re.match(' *', self.lines[index])
        if m:
            return len(m.group(0))
        else:
            return 0

    def _line_indent(self, index):
        blanks=self._nb_spaces(index)
        if blanks % self.SPACE_INDENT==0:
            return blanks // self.SPACE_INDENT
        else:
            raise SyntaxError('Wrong indentation: "%s"' %
                              self.lines[index])

    def _suffix(self, delta):
        if delta==1:
            return self.OPENING_BRACKET
        elif delta==0:
            return self.EOL
        else:
            return (
                self.EOL
                +  (self.CLOSING_BRACKET+self.EOL) * - delta
            )

    @property
    def text(self):
        self.bracketedLines=list(self.lines)
        # LNBL = Last Non Black Line
        lnbl_index=-1
        lnbl_indent=0
        # take all lines + a extra virtual line to close everything
        for (index, line) in enumerate(self.lines):
            if not self._is_blank_line(index):
                indent=self._line_indent(index)
                delta=indent-lnbl_indent
                if self._is_doc_line(index):
                    self.bracketedLines[index]=(
                        self._terminate_doc_line(self.bracketedLines[index])
                    )
                if delta>1:
                    # this will never happened for the last line
                    raise SyntaxError('Wrong indentation: "%s"'
                                      % line)
                else:
                    if lnbl_index!=-1:
                        self.bracketedLines[lnbl_index] += self._suffix(delta)
                lnbl_index=index
                lnbl_indent=indent
        # close the last line if any
        if lnbl_index!=-1:
            delta=0-lnbl_indent
            self.bracketedLines[lnbl_index] += self._suffix(delta)

        return '\n'.join(self.bracketedLines)

    def save(self):
        f = open(self.targetFilename, "w")
        f.write(self.text)
        f.close()
        return self.targetFilename

import sys
if __name__ == "__main__":
    source=sys.argv[1]
    text=BracketedScript(source).save()
