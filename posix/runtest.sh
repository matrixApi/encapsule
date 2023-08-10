#!/bin/sh
export PYTHONPATH=/home/Owner/packages/library/packages/common
export ENCAPSULE_KERNEL=../kernel001 ENCAPSULE_COMPONENTS=../jail

python -m encapsule.isolate_bin ${1:-x.sh} ${@:2}
