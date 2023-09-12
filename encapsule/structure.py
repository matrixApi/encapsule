'''
[MUD]
document_class = WRLC

[WRLC]
system_classes =
	encapsulated=encapsule.structure.Factory


encapsule:
	interfaces/views::
		(encapsulated$view):
			- 'system:classification'

'''

from kernelos.structure import Submapping, View
from kernelos.kernel import vmCurrentTask

from encapsule.isolate_bin import exeCall


class Factory(Submapping):
	def view(self, name, value, **kwd):
		return EncapsulatedView(value)

class EncapsulatedView(View):
	_prefix = ''

	def __init__(self, prefix):
		self._prefix = prefix

	def _requestUserId(self, request):
		pass

	def _argsFull(self, request, path):
		if self._prefix:
			checkAccess = vmCurrentTask().checkAccess

			if isinstance(self._prefix, str):
				checkAccess(['system:encapsulate:view', \
					self._prefix, path], 'encapsulate')

				yield self._prefix
			else:
				checkAccess(['system:encapsulate:view', \
					'/'.join(self._prefix), path], 'encapsulate')

				yield from self._prefix

		yield path

	def _render(self, request, path, **kwd):
		args = list(self._argsFull(request, path))

		return exeCall(*args, userId = \
			self._requestUserId(request))
