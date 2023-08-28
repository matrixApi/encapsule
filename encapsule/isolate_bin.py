# XXX Todo: use a setuid-0 installation of python exe

'''
SYSBIN=/system/bin

setuid -u 0 "$SYSBIN/.isolate"
PATH=$SYSBIN:$PATH

.isolate --post-context assets/Itham/services/component/query \
    --keyword=value arg1 arg2 arg3 \
    | wget 'https://network/channel/x' -x post


assets/Itham/services:
    component::
        def query():
            return 'text/json/dumps' \
                (mapping(arguments = args$(), \
                         keywords = keywords$()))

    encapsule::
        XXX:
            This needs 

        def argsOf(kwdClass, args, kwd):
            for pair in keywords$().items():
                args.append(act(kwdClass, pair))

            return args

        def compartmentalize(context, name):
            exe = 'kernel/lookup$'('encapsule.exeCall') # Object')
            exe$error = exe.error

            userId = keywords$('impersonateAs', false)
            if is$false(userId):
                userId = context(programmer)

            try: return act(exe, argsOf \
                    (exe.keyword, args$slice(1), keywords$()), \
                        mapping(compartmentalize = true, \
                                impersonateAs = userId))

            except exe$error e:
                return namespace \
                    (code = e.returncode, \
                     error = e.stderrOutput, \
                     output = e.stdOutput)

            # 'kernel/info'(r)
            # return r

            usage:
                services = library('services').call.encapsule.call.system
                services.init$v()() # the install

                return action(services.call.compartmentalize \
                    .bindToInstance(.), security$context$new(), \
                     'x.sh', \

                     impersonateAs = none, keyword = 'value') \
                        ('arg1', 'arg2', 'arg3')


        def query():
            return 'text/json/dumps' \
                (mapping(arguments = args$(), \
                         keywords = keywords$()))


        def install(): # dynamic
            # path = (keywords$('path', none) or .compiled()).strip() <- instance$:
            #    return 'kernel/gen'('evaluate', 'configuration').encapsule.path

            env = 'kernel/lookup$'('os.environ')
            base = env['ENCAPSULE_HOME'] + '/'

            env['ENCAPSULE_COMPONENTS'] = base + 'jail'
            env['ENCAPSULE_KERNEL'] = base + 'kernel001'

            path = (keywords$('path', none) or run$python(code, mapping()).strip()) <- code:
                __return = configuration.encapsule.path

            if path:
                sys = 'kernel/lookup$'('sys.path')

                if not path in sys:
                    sys.append(path)

        return install

'''

import sys
import op

from json import loads as deserialize, dumps as serialize
from contextlib import contextmanager

from op.platform.path import CalledProcessError

from . import isolate_sys

__all__ = ['exeCall', 'exeCallObject', 'keyword']

publicName = hash

def invocation(argv = None):
    try: (options, output) = main(argv)
    except CalledProcessError as e:
        sys.stderr.write(e.stderrOutput.decode())
        sys.exit(e.returncode)

        raise SystemError(f'Could not exit (returncode: {e.returncode})')


    if options.post_context:
        # XXX Shouldn't be json
        # XXX limited UID specification here
        output = serialize(dict \
            (context = publicName \
                (isolate_sys.effectiveContextId()),
             content = output))

    sys.stdout.write(output)


def buildOptions_parent(options):
    return namespace \
        (# "chroot" mount point:
         component_root = isolate_sys.ENCAPSULE_COMPONENTS_PATH,

         compartmentalize = options.get('compartmentalize'),
         segments = options.get('segments'),
         post_context = options.get('post_context'))

def parseCmdln_subjective(argv):
    # Todo: wrong
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('--post-context', action = 'store_true')

    (options, args) = parser.parse_args(argv)

    # isolate_bin invocations are always 'compartmentalized',
    # for now, because it represents an entry point.
    return ((buildOptions_parent \
                (namespace(post_context = options.post_context,
                           compartmentalize = True)),
             (args[0],)), args[1:])


class Component:
    # This represents an invocation instance, so, we can
    # store invocation-specific data (taskId_new).

    @classmethod
    def Locate(self, options, name):
        return self(name, options, isolate_sys.restrict_path \
                    # Note: splitting on '/' means empty components are ignored.
                    (options.component_root, name.split('/')))

    def __init__(self, name, parentOptions, executable):
        self.name = name
        self.parentOptions = parentOptions
        self.executable = executable

    def newTaskId_env(self, **kwd):
        if self.parentOptions.compartmentalize:
            (kwd['env'], self.taskId_new) = isolate_sys.generateNewTaskId_env()
        else:
            # todo: Is this always true?
            self.taskId_new = isolate_sys.taskId()

        # _posixsubprocess-setuid: is this available on cygwin?
        # Todo: cygwin multi-user testing setup.
        # Todo: specification of UID?
        kwd['user'] = isolate_sys.componentOwnerUser \
            (self.name, enforce = kwd.pop('userId') \
                or isolate_sys.effectiveContextId())

        return kwd

    @contextmanager
    def runContext(self, process):
        # grr
        with isolate_sys.setTaskFrame_pid \
            (self.taskId_new, process.pid,
             self.parentOptions.compartmentalize) as x:

            yield x

    def pipeStringContext(self, args, **kwd):
        # Subject Main.
        # Perform access check.

        # setuid pipe invocation

        # XXX DISABLED FOR TESTING XXX
        # isolate_sys.checkAccessCurrentUser(self.name)

        settings = self.newTaskId_env \
            (runContext = self.runContext,
             userId = kwd.get('userId'))

        # import pdb; pdb.set_trace()
        return self.executable.pipe \
            (*args, **settings) \
            .decode() # Why subprocess returns bytes stream,
                      # but sys.stdout is default opened str.

def main(argv):
    # import pdb; pdb.set_trace()
    ((parentOptions, parentArgs), isoOptions) = \
        parseCmdln_subjective(argv)

    return (parentOptions, Component.Locate \
        (parentOptions, *parentArgs)    \
            .pipeStringContext(isoOptions))


class keyword:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __str__(self):
        return f'--{name}={value}'

def exeCall(name, *args, **kwd):
    '''
    from encapsulate import exeCallObject

    def run():
        try: return exeCallObject \
            ('assets/Itham/services/component/query',
             exeCallObject.keyword('keyword', 'value'),
             'arg1', 'arg2', 'arg3',
             compartmentalize = True)

        except exeCallObject.error as e:
            return namespace(code = e.returncode,
                             error = e.stderrOutput,
                             output = e.stdOutput)

    '''

    userId = kwd.pop('impersonateAs')

    # debugOn()
    return Component.Locate \
        (buildOptions_parent(kwd), name) \
            .pipeStringContext \
                (' '.join(map(str, args)),
                 userId = userId)

def exeCallObject(*args, **kwd):
    return deserialize(exeCall(*args, **kwd))

exeCall.error = CalledProcessError
exeCall.keyword = keyword

exeCallObject.error = CalledProcessError
exeCallObject.keyword = keyword


if __name__ == '__main__':
    invocation(sys.argv[1:])
    # invocation(sys.argv)
