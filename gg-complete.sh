_gg_completion() {
    COMPREPLY=( $( env COMP_WORDS="${COMP_WORDS[*]}" \
                   COMP_CWORD=$COMP_CWORD \
                   _GG_COMPLETE=complete $1 ) )
    return 0
}

complete -F _gg_completion -o default gg;
