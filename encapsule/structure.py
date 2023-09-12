'''
[MUD]
document_class = MUD
system_classes =
	encapsulated=encapsule.structure.Factory


encapsule:
	interfaces/views::
		(encapsulated$view):
			- 'public:classification'

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

	def _render(self, request, path, **kwd):
		args = list(self._argsFull(request, path))

		return exeCall(*args, userId = \
			self._requestUserId(request))

	def _requestUserId(self, request):
		pass

	def _argsFull(self, request, path):
		resource = self._prefix
		if resource:
			if isinstance(resource, str):
				args = [resource]

			else:
				args = resource
				resource = '/'.join(resource)

			vmCurrentTask().checkAccess \
				(['system:encapsulate:view', \
				  resource, path], 'encapsulate')

			yield from args

		yield path
