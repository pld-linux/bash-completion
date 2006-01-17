have poldek && {

# poldek(1) completion
# 
_poldek()
{
	local cur prev ver nodig nosig

	COMPREPLY=()
	cur=${COMP_WORDS[COMP_CWORD]}
	prev=${COMP_WORDS[COMP_CWORD-1]}
	nodig=""
	nosig=""

	if [ $COMP_CWORD -eq 1 ]; then
		# first parameter on line
		case "$cur" in
		--*)
			COMPREPLY=( $( compgen -W '--help --version --erase \
			' -- $cur ) )
			;;
		*)
			COMPREPLY=( $( compgen -W '-F -N -O -P -Q -V -e -i -l -m -n -q -r -s -t -u -v' \
				       -- $cur ) )
			;;
		esac

	return 0
	fi

	case "${COMP_WORDS[1]}" in
	-@(e|-erase))
		if [[ "$cur" == -* ]]; then
			COMPREPLY=( $( compgen -W '--nodeps --nofollow --test' -- $cur ) )
		else
			_rpm_installed_packages
		fi
		;;
	esac

	return 0
}
complete -F _poldek $filenames poldek
}
