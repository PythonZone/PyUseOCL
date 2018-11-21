import argparse

from modelscript.config import Config

__all__=(
    'getOptions',
)

FULL_INTERFACE=False

OPTIONS=[
    ('Dimp','realtimeImportPrint'),
    ('Diss','realtimeIssuePrint'),
    ('Dckk','realtimeCheckers'),
]


def _argParser():
    """
    Return a (argparse) parser for command arguments.
    The parsing can then be done using
         parser.parse_args(args)
    """
    parser = argparse.ArgumentParser(
        prog='modelc',
        description='Compile the given sources.')
    if FULL_INTERFACE:
        for (parameter,label) in OPTIONS:
            parser.add_argument(
                '--'+parameter,
                dest=parameter,
                const=1,
                # default=0,
                type=int,
                nargs='?',
                help='debug: control %s' % label)
        parser.add_argument(
            '-bw',
            dest='bw',
            action='store_true',
            help='black and white output',
            default=False)
        parser.add_argument(
            '-dg',
            dest='dg',
            action='store_true',
            default=False)
        parser.add_argument(
            '--issues', '-i',
            dest='issues',
            const='top',
            default='inline',
            help='choose location of issues wrt to the listing.',
            choices=['top','inline','bottom'],
            type=str,
            nargs='?')
        parser.add_argument(
            '--list', '-l',
            dest='listing',
            const='source',
            default='no',
            help='display a listing of model.',
            choices=['no', 'source', 'model'],
            type=str,
            nargs='?')
        parser.add_argument(
            '--summary', '-s',
            dest='summary',
            const='bottom',
            default='no',
            help='display a summary of model.',
            choices=['no', 'top', 'bottom'],
            type = str,
            nargs = '?')
    parser.add_argument(
        '-mode', '-m',
        dest='mode',
        const='full',
        default='full',
        help='choose the checking level.',
        choices=['justAST', 'justASTDep', 'full'],
        type=str,
        nargs='?')
    parser.add_argument(
        '--verbose', '-v',
        dest='verbose',
        action='store_true',
        default=False,
        help='make output verbose.')
    parser.add_argument(
        '--quiet', '-q',
        dest='quiet',
        action='store_true',
        help='create minimal amount of output.',
        default=False)
    parser.add_argument(
        '--version', '-V',
        dest='version',
        action='store_true',
        help='display modelscript version.',
        default=False)
    parser.add_argument(
        'sources',
        metavar='source',
        nargs='*',
        help='A model source file or a directory.')
    return parser

def _updateConfig(options):
    for (parameter, configOption) in OPTIONS:
        val = getattr(options, parameter)
        if val is not None:
            # update config only if value is specified
            print('%s(%s)=%s' % (configOption, parameter, val))
            setattr(Config, configOption, val)

def getOptions(args):
    parser = _argParser()
    options = parser.parse_args(args)
    if FULL_INTERFACE:
        _updateConfig(options)
    return options
