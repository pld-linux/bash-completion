have poldek && {

# poldek(1) completion
#
_poldek()
{
	local cur prev

	COMPREPLY=()

	case "${COMP_WORDS[1]}" in
	-@(e|-erase))
		if [[ "$cur" == -* ]]; then
			COMPREPLY=( $( compgen -W '--nodeps --nofollow --test' -- $cur ) )
		else
			_rpm_installed_packages
		fi
		return 0
		;;
	esac


	cur=${COMP_WORDS[COMP_CWORD]}
	prev=${COMP_WORDS[COMP_CWORD-1]}

	case "$prev" in
	-@(n|-sn))
		COMPREPLY=( $( poldek -l | awk "/^$cur/{print \$1}" ) )
		return 0
		;;
	--verify)
		COMPREPLY=( $( compgen -W 'deps conflicts file-conflicts file-orphans file-missing-deps' -- $cur ) )
		return 0
		;;
	esac

	case "$cur" in
	--*)
		COMPREPLY=( $( compgen -W '
		--mkidx --makeidx --mt --nocompress --nodesc --nodiff --notimestamp
		--dn --dt --sn --prefix --source --st --clean --clean-pkg
		--clean-whole --cleana --sl --stl --update --up --update-whole
		--upa --caplookup --pset --downgrade --install --reinstall
		--upgrade --install-dist --reinstall-dist --root --upgrade-dist
		--dump --dumpn --fetch --follow --force --fresh --greedy --hold
		--ignore --justdb --mercy --nodeps --nohold --noignore --nofollow
		--parsable-tr-summary --pm-force --pm-nodeps --pmopt --promoteepoch
		--uniq --test --erase --greedy --nodeps --nofollow --test --verify
		--priconf --split --split-out --ask --cachedir --cmd --conf --log
		--noask --noconf --pmcmd --runas --shell --skip-installed --sudocmd
		--upconf --help --usage --version
		' -- $cur ) )
		;;
	*)
		COMPREPLY=( $( compgen -W '-F -N -O -P -Q -V -e -i -l -m -n -q -r -s -t -u -v' \
				   -- $cur ) )
		;;
	esac

	return 0
}
complete -F _poldek $filenames poldek
}
