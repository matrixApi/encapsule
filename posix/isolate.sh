export ENCAPSULE_KERNEL=./jail001
export ENCAPSULE_COMPONENTS=./jail001/install

export PYTHONPATH=$HOME/packages/external

exec python -m encapsule.isolate_bin $*
