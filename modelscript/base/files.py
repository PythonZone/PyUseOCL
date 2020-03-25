# coding=utf-8

from typing import Callable, Any
import io
import os
from distutils.dir_util import mkpath

from modelscript.base.issues import (
    Levels,
    Issue
)

__all__=(
    'ensureDir',
    'extension',
    'withoutExtension',
    'replaceExtension',
    'raiseIssueOrException',
    'readFileLines',
    'writeFile',
    'writeFileLines'
)

def ensureDir(dir):
    """
    :raises: IOError
    """
    if not os.path.isdir(dir):
        try:
            mkpath(dir)
        except Exception: #except:OK
            raise IOError(
                'Cannot create directory %s' % dir) #raise:TODO:3

def extension(path):
    filename, file_extension =os.path.splitext(os.path.basename(path))
    return file_extension

def withoutExtension(path):
    filename, file_extension =os.path.splitext(path)
    return filename

def replaceExtension(path, ext):
    return withoutExtension(path)+ext


def raiseIssueOrException(exception, message, issueOrigin):
    if issueOrigin is None:
        raise exception  #raise:TODO:1
    else:
        Issue(
            origin=issueOrigin,
            level=Levels.Fatal,
            message=message
        )

def readFileLines(
        file,
        issueOrigin=None,
        message='Cannot read file %s'):
    try:
        with io.open(file,
                     'rU',
                     encoding='utf8') as f:
            lines = list(
                line.rstrip() for line in f.readlines())
        return lines
    except Exception as e:
        raiseIssueOrException(
            e,
            message % file,
            issueOrigin)

def writeFile(
        text,
        filename,
        # extension='.txt',
        issueOrigin=None,
        message='Cannot write file'):
    try:
        # if outputFileName is not None:
        # else:
        #     (f, filename) = (
        #         tempfile.mkstemp(
        #             suffix=extension,
        #             text=True))
        #     os.close(f)
        import codecs
        with codecs.open(filename, "w", "utf-8") as f:
            f.write(text)
        return filename
    except Exception as e:
        raiseIssueOrException(
            exception=e,
            message=message,
            issueOrigin=issueOrigin)

def writeFileLines(
        lines,
        filename,
        issueOrigin=None,
        message='Cannot write file'):
    return writeFile(
        text='\n'.join(lines),
        filename=filename,
        issueOrigin=issueOrigin,
        message=message)





def filesInTree(directory, suffix):
    """
    Search for all filenames ending with the suffix(es)
    :param directory: the directory where to search
    :param suffix: a string or a list of string serving as suffixes
    :return: the lst of filenames ending with the suffix(es)
    """
    if isinstance(suffix,str):
        suffixes=[suffix]
    else:
        suffixes=suffix
    _=[]
    for root, dirs, files in os.walk(directory):
        for file in files:
            for s in suffixes:
                if file.endswith(s):
                    path=os.path.join(root, file)
                    _.append(path)
                    break
    return _

