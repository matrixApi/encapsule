export ENCAPSULE_CREATEUSERBIN=`which useradd`
export ENCAPSULE_CREATEUSER_NAMEFMT='encapsule:{name}'

`dirname $0`/isolate.sh --create-user $*
