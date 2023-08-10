from posix import geteuid as effectiveContextId

from os import kill as processKill, environ as os_environ
from signal import SIGSTOP, SIGCONT, SIGTERM # , SIGKILL
from contextlib import contextmanager
from string import ascii_letters as _taskId_alphabet
from base64 import b32encode

from random import choice # XXX entropy


# Environment.
ENCAPSULE_TASK_ID_ENV = 'ENCAPSULE_TASK_ID'
ENCAPSULE_STORE_ENV = 'ENCAPSULE_KERNEL'
ENCAPSULE_COMPONENTS_PATH_ENV = 'ENCAPSULE_COMPONENTS'
ENCAPSULE_OWNERSHIP_ENV = 'ENCAPSULE_OWNERSHIP'


class NoFramesError(RuntimeError):
	pass
class NoAccessException(Exception):
	pass


# Storage.
class storageClass:
	TASKS = 'tasks'
	ACCESS = 'access'
	EXE_OWNER = 'ownership'

class localFS(storageClass):
	SEP = ':'

	def __init__(self, path, exe_owner_path = None):
		# !!! These paths should be ROOT-ONLY !!!
		self.path = io.path(path)

		if exe_owner_path is None:
			exe_owner_path = self.path(self.EXE_OWNER)

		self.exe_owner_path = exe_owner_path

	def pathOf(self, i, name = ''):
		return i(name) if callable(i) else \
				self.path(i, *name.split(self.SEP))

	@contextmanager
	def pathOf_c(self, *args, **kwd):
		yield self.pathOf(*args, **kwd)

	def __iter__(self):
		yield self.store
		yield self.retrieve
		yield self.erase
		yield self.touch


	def store(self, i, name, value):
		with self.pathOf_c(i, name) as path:
			path.folder.ensure()
			path.write(str(value))

	def retrieve(self, i, name, **kwd):
		try: return self.pathOf(i, name).read()
		except Exception as e:
			try: return kwd['default']
			except:
				raise e

	def erase(self, i, name):
		# Todo: audit this destructive method.
		# return self.pathOf(i, name).delete()

		path = self.pathOf(i, name)

		if path.isdir:
			return destroydirs(path, force = True)

			# XXX removedirs might not be right algo at all
		    # XXX removedirs doesn't remove non-empty dirs
			# from os import removedirs
			# return removedirs(path)

		return path.delete()

	def touch(self, i, name):
		return self.store(i, name, '')


# Filesystem
from os import rmdir, listdir, unlink
from os.path import join as joindir, isdir

def destroydirs(name, force = False):
	if isdir(name):
		for c in listdir(name):
			# recurse
			destroydirs(joindir(name, c), force = force)

		if force:
			rmdir(name)
		else:
			print(f'removing {name}')

	elif force:
		unlink(name)

	else:
		print(f'removing {name}')

def restrict_path(root, path):
	r = root = io.path(root)

	for p in path:
		if p != '..' or r != root:
			# Note: empty components are ignored.
			r = r(p)

	return r


# Task:Identifiable
def taskId():
	return os_environ[ENCAPSULE_TASK_ID_ENV]


# Todo: move into orchObject
@contextmanager
def setTaskFrame_pid(i, pid, compartment):
	# "addTaskFrame"

	# i = taskId()

	# import pdb; pdb.set_trace()

	fu = f'{i}:frameCurrent'

	u = int(retrieve(storageClass.TASKS, fu, default = -1))
	ui = u + 1

	newU = f'{i}:processId:{ui}'
	store(storageClass.TASKS, newU, pid)

	store(storageClass.TASKS, fu, ui)

	try: yield
	finally:
		erase(storageClass.TASKS, newU)

		if compartment:
			completeTask(i)
		elif u < 0:
			erase(storageClass.TASKS, fu)
		else:
			store(storageClass.TASKS, fu, u)


def completeTask(i):
	try: taskCompletion = orchObject_i.storage.pathOf \
		(storageClass.TASKS, f'{i}:completions').listing

	except FileNotFoundError:
		taskCompletion = []

	for complete in taskCompletion:
		try: r = task_initiateCompletionScript(complete, i)
		except: pass
		else:
			if r:
				break

	try: erase(storageClass.TASKS, i)
	except IsADirectoryError:
		pass # not yet implemented: need a rigorously-safe impl

def task_initiateCompletionScript(pathScript, taskId):
	# todo: pathScript could be a folder containing identity info
	pass


INVALID_PID = -1

def pidOf_taskFrame(taskId, invalid_onerror = False):
	u = retrieve(storageClass.TASKS, f'{taskId}:frameCurrent', default = -1)
	if u < 0:
		raise NoFramesError()

	r = retrieve(storageClass.TASKS, f'{taskId}:processId:{u}', default = INVALID_PID)

	if not invalid_onerror and r == INVALID_PID:
		raise ValueError(f'No processId record for frame:{u}')

	return r


def _generateNewTaskId(length = 80):
	return ''.join(choice(_taskId_alphabet) for x in range(length))

def generateNewTaskId(tries = 1000000, **kwd):
	for x in range(tries):
		i = _generateNewTaskId(**kwd)

		if not orchObject_i.taskOf(i).exists:
			return i

	raise ValueError(tries)

def generateNewTaskId_env():
	i = generateNewTaskId()
	return ({ENCAPSULE_TASK_ID_ENV: i}, i)


# Permissions.
def encodeComponent(name):
	return b32encode(name.encode())


def exe_perm_owner(name):
	return localFS_i.exe_owner_path \
		(encodeComponent(name))

def componentOwnerUser(name, enforce = None):
	return retrieve(exe_perm_owner, name, default = enforce)
def setComponentOwner(name, userId):
	return store(exe_perm_owner, name, userId)


def permOf(userId, name, access = 'read'):
	return f'{userId}:{encodeComponent(name)}:{access}'

def checkAccess(userId, name, access = 'read', fail_onerror = False):
	if retrieve(storageClass.ACCESS, permOf(userId, name, access),
				default = False) is not False:

		return True

	if fail_onerror:
		return False

	raise NoAccessException

def grantAccess(userId, name, access = 'read'):
	checkAccess(userId, name, 'grant')
	return touch(storageClass.TASKS, permOf(userId, name, access))


def checkAccessCurrentUser(*args, **kwd):
	return checkAccess(effectiveContextId(), *args, **kwd)


# Process OM
def suspend_process(pid):
	return processKill(pid, SIGSTOP)
def resume_process(pid):
	return processKill(pid, SIGCONT)

def suspendTask(taskId):
	return suspend_process(pidOf_taskFrame(taskId))
def resumeTask(taskId):
	return resume_process(pidOf_taskFrame(taskId))


class processObject:
	def __init__(self, pid):
		self.pid = pid

	@property
	def path(self):
		return io.root.proc(str(self.pid))

	@property
	def environ(self):
		return dict(x.split('=', 1) for x in
					self.path.environ.read() \
						.split('\x00'))

	@property
	def taskId(self):
		return self.environ.get(ENCAPSULE_TASK_ID_ENV)


	def suspend(self):
		return suspend_process(self.pid)
	def resume(self):
		return resume_process(self.pid)

	def signal(self, signal):
		return signal_process(self.pid, signal)
	def terminate(self):
		return self.signal(SIGTERM)

	# def kill(self):
	# 	return self.signal(SIGKILL)


# Task OM
class frameObject:
	processObject = processObject
	pidCast = int # str

	def __init__(self, task, nr):
		self.task = task
		self.nr = nr

	@property
	def pidOf(self):
		return self.pidCast(self.task.path \
			('processId', str(self.nr)).read())

	@property
	def process(self):
		return self.processObject(self.pidOf)


class taskObject:
	frameObject = frameObject

	def __init__(self, path, orch = None):
		self.path = path
		self.orch = orch

	@property
	def exists(self):
		return self.path.exists

	def __iter__(self):
		u = int(self.path.frameCurrent.read()) # storage derefence

		# reverse
		for i in range(u, -1, -1):
			yield self.frameObject(self, i)

	frames = property(__iter__)


# Orchestration OM
class orchObject:
	taskObject = taskObject

	def __init__(self, storage):
		self.storage = storage

	def __iter__(self):
		return (self.taskObject(path, orch = self)
				for path in self.storage.pathOf \
					(storageClass.TASKS).listing)

	def taskOf(self, taskId):
		return self.taskObject(self.storage.pathOf \
			(storageClass.TASKS, taskId))


# Install - XXX These shouldn't be set by the environment.
(store, retrieve, erase, touch) = localFS_i = localFS \
	(os_environ[ENCAPSULE_STORE_ENV],
	 exe_owner_path = os_environ.get(ENCAPSULE_OWNERSHIP_ENV))

ENCAPSULE_COMPONENTS_PATH = os_environ[ENCAPSULE_COMPONENTS_PATH_ENV]

orchObject_i = orchObject(localFS_i)
