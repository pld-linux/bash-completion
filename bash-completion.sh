# $Id$

# Check for bash (and that we haven't already been sourced).
[ -z "$BASH_VERSION" -o -n "$BASH_COMPLETION" ] && return

# must be interactive shell, not script
[[ $- = *i* ]] || return
[ -n "$PS1" ] || return

# Check for recent enough version of bash.
bash=${BASH_VERSION%.*}; bmajor=${bash%.*}; bminor=${bash#*.}
if [ "$bmajor" -eq 2 -a "$bminor" '>' 04 ] || [ "$bmajor" -gt 2 ]; then
	# Source completion code
	. /etc/bash_completion
fi
unset bash bminor bmajor
