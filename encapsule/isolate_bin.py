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

        def task$compartmentalize(context, name):
            return act(task$, [compartmentalize] + args$(), \
                keywords$())


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

INSTANCE_1 = '''\
# -f install-object.ela encapsule.isolate_bin.INSTANCE_1 run-isolate.ela

# cat < subordinate.ela > "
# if task$compartmentalize(none, 'instance', '-d').outcome().yes: # primary
#     shutdown()
# "

# -f install-path.ela system/initialize subordinate.ela
# -f run-isolate.ela -Ssystem:initialization=system/initialize

return act(task$compartmentalize.action \
    (none, 'instance', '-d', arguments.strip()), \
    args$()).outcome() <- arguments:

    -Ssystem:namespace=subordinate

'''


import sys

from json import loads as deserialize, dumps as serialize
from contextlib import contextmanager

from . import isolate_sys

__all__ = ['exeCall', 'exeCallObject', 'keyword']


class synthetic(dict):
    def __init__(self, *args, **kwd):
        dict.__init__(self, *args, **kwd)
        self.__dict__ = self


publicName = hash

def initWrlc_bin():
    global CalledProcessError

    # todo: combine these?
    isolate_sys.initWrlc()
    isolate_sys.install()

    exeCall.error = exeCallObject.error = \
    CalledProcessError = \
        isolate_sys.CalledProcessError


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


def optionsCopy(options, r, names):
    for n in names:
        r[n] = getattr(options, n, None) # options.get(n)

    return r


SEMIFULL_OPTIONS = ['action', 'segments', 'post_context', 'arguments']
FULL_OPTIONS = SEMIFULL_OPTIONS + ['compartmentalize']

def buildOptions_parent(options):
    namespace = synthetic

    return optionsCopy(options, namespace \
        (# "chroot" mount point:
         component_root = isolate_sys.ENCAPSULE_COMPONENTS_PATH),
        FULL_OPTIONS)


def parseCmdln_subjective(argv):
    # Todo: wrong
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-x', '--argument', '--arg', action = 'append', dest = 'arguments')
    parser.add_option('--action')

    parser.add_option('--post-context', action = 'store_true')

    parser.add_option('--check-access-resource', '--check', action = 'store_const',
        const = 'check-access-resource', dest = 'action')

    parser.add_option('--check-access', default = 'read')

    parser.add_option('--create-user', action = 'store_const',
        const = 'create-user', dest = 'action')

    (options, args) = parser.parse_args(argv)

    # isolate_bin invocations are always 'compartmentalized',
    # for now, because it represents an entry point.
    namespace = synthetic

    return ((buildOptions_parent \
                (optionsCopy(options, namespace(compartmentalize = True),
                             SEMIFULL_OPTIONS)),
             (None if options.action else args[0],)),
            args if options.action else args[1:])


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


mainActions = \
    {'create-user': lambda parentOptions, parentArgs, isoOptions:
        # ENCAPSULE_CREATEUSERBIN=`which useradd` \
        # ENCAPSULE_CREATEUSER_NAMEFMT='encapsule:{name}' \
        #     .isolate --create-user itham

        (parentOptions, isolate_sys.createUser_linuxStrict
            (*((parentArgs,) if parentArgs else () +
                (parentOptions.arguments or ())))),

     'create-user-set': lambda parentOptions, parentArgs, isoOptions:
        (parentOptions, '\n\n'.join
            (map(isolate_sys.createUser_linuxString,
                 (parentArgs,) if parentArgs else () +
                 (parentOptions.arguments or ())))),

     'check-access-resource': lambda parentOptions, parentArgs, isoOptions:
        (parentOptions, isolate_sys.checkAccessCurrentFrameUser \
            (isolate_sys.taskId(), # XXX Is this right?
             resource, parentOptions.check_access)),


     # Default action:
     None: lambda parentOptions, parentArgs, isoOptions:
            (parentOptions, Component.Locate \
                (parentOptions, *parentArgs) \
                    .pipeStringContext(isoOptions))}


def main(argv):
    # import pdb; pdb.set_trace()
    ((parentOptions, parentArgs), isoOptions) = \
        parseCmdln_subjective(argv)


    # Todo: configurable
    initWrlc_bin()


    return mainActions[parentOptions.action] \
        (parentOptions, parentArgs, isoOptions)



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


exeCall.keyword = exeCallObject.keyword = keyword


if __name__ == '__main__':
    invocation(sys.argv[1:])
    # invocation(sys.argv)
