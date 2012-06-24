# bash completion for phing

have phing &&
{
_phing()
{
    local cur prev buildfile i

    COMPREPLY=()
    _get_comp_words_by_ref cur prev

    case $prev in
        -buildfile|-file|-f)
            _filedir 'xml'
            return 0
            ;;
        -logfile)
            _filedir
            return 0
            ;;
        -logger|-listener|-D|-inputhandler)
            return 0
            ;;
    esac

    if [[ "$cur" == -* ]]; then
        COMPREPLY=( $( compgen -W '-help -version \
            -quiet -verbose -debug -logfile -logger -listener \
            -buildfile -D -inputhandler \
            -projecthelp \
            -find' \
            -- "$cur" ) )
    else
        # available targets completion
        # find which buildfile to use
        buildfile=build.xml
        for (( i=1; i < COMP_CWORD; i++ )); do
            if [[ "${COMP_WORDS[i]}" == -@(?(build)file|f) ]]; then
                buildfile=${COMP_WORDS[i+1]}
                break
            fi
        done
        [ ! -f $buildfile ] && return 0

        # parse buildfile for targets
        # some versions of sed complain if there's no trailing linefeed,
        # hence the 2>/dev/null
        COMPREPLY=( $( compgen -W "$( cat $buildfile | tr "'\t\n>" "\"  \n" | \
            sed -ne 's/.*<target .*name="\([^"]*\).*/\1/p' 2>/dev/null )" \
            -- "$cur" ) )
        fi
} &&
complete -F _phing phing
}

# Local variables:
# mode: shell-script
# sh-basic-offset: 4
# sh-indent-comment: t
# indent-tabs-mode: nil
# End:
# ex: ts=4 sw=4 et filetype=sh
