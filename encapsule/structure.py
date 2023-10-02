'''
[MUD]
document_class = MUD
system_classes =
	encapsulated=encapsule.structure.Factory


-SMUD:document-class=MUD -SMUD:system-classes=encapsulated=encapsule.structure.Factory


encapsule:
	interfaces/views::
		(encapsulated$public$view):
			- 'public:classification'
'''

from kernelos.structure import Submapping, View
from kernelos.kernel import vmCurrentTask

from encapsule.isolate_bin import exeCall


class Factory(Submapping):
	def view(self, name, value, **kwd):
		return EncapsulatedView(value)
	def _publicView(self, name, value, **kwd):
		return EncapsulatedView(value, True)

	vars()['public$view'] = _publicView


class EncapsulatedView(View):
	_prefix = ''

	def __init__(self, prefix, public = False):
		self._prefix = prefix
		self._public = public

    def _render(self, request = None, path = None, programmer = None):
		args = list(self._invocationArgs(request, path, programmer))

		return exeCall(*args, userId = \
			self._requestUserId(request))

	def _requestUserId(self, request):
		pass

	def _checkAccess(self, resource, path, programmer,
					 access = 'encapsulate')

		resource = ['system:encapsulate:view',
			  	    resource, path]

		if self._public:
			(vmCurrentTask().libraryCore or agentSystem) \
				.checkAccess(programmer, resource, access)
		else:
			vmCurrentTask().checkAccess \
				(resource, access)

	def _invocation_resource(self):
		resource = self._prefix

		return (([resource], resource)
			if isinstance(resource, str)
			else (resource, '/'.join(resource))) \
				if resource else [None, None]


	def _invocationArgs(self, request, path, programmerContext):
		(resource, args) = self._invocation_resource()
		if resource:
			self._checkAccess(resource, path, programmerContext)

			yield from args

		else:
			self._checkAccess('', path, programmerContext)

		yield path



C_IMPL = r'''\
def rawCall(args):
	return act('kernel/callObject$', \
		['string.rawCall'] + args)

def renderCall(name):
	return render(code, mapping(call = \
		rawCall([name] + args.value + \
		args$slice(1))) \

	<- args:
		- '.isolate'
		- 'public:classification'

	<- code:
		// #include "encapsule.h"

		void main(int argc, char **argv)
		{
			if (argc > 1)
			{
				encapsuleSetIdentity(argv[0]);
				{{ call|safe }};
			}
		}


def preparefiles(wd):
	sourcefile = wd.temporary + '.c'
	objectfile = targetfile(sourcefile, 'o')

	return [sourcefile, objectfile]

def compileCall(wd, name):
	scatter(preparefiles(wd), 'sourcefile', 'objectfile')

	sourcefile.write(act(renderCall, \
		[name] + keywords$('args', [])))

	keywords$('gcc').pipe \
		('-shared', '-o', objectfile, sourcefile, \
		 '-L' + keywords$('libpath'), '-lencapsule')

	return objectfile.pipe
		

path = 'kernel/lookup$'('builtins.io.root')

return compileCall,
	(path.tmp, 'encapsuleCreateUserTask', \
	 args = args.value, \
	 gcc = path.usr.bin.gcc, \
	 libpath = path.usr.lib) \
		(programmer()) <- args:

		- get-identity

'''
