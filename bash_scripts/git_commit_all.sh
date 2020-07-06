#!/bin/bash

# https://stackoverflow.com/questions/35800082/how-to-trap-err-when-using-set-e-in-bash

RED="\033[1;31m"
GREEN="\033[1;32m"
NC="\033[0m" # No Color


function func(){
    echo -e "${GREEN}@"$(hostname)"${NC}"
    base_dir=$(git rev-parse --show-toplevel)
    if [ ! -d "$base_dir" ]; then
        echo "base git directory does not exist, exited."
        exit
    fi
    current_dir=$PWD

    $HOME/eBlocBroker/bash_scripts/clean.sh
    # pre-commit autoupdate

    if [[ $PWD =~ "eBlocBroker" ]]
    then
        SKIP=mypy pre-commit run --all-files
    fi

    set -eE  # same as: `set -o errexit -o errtrace`
    trap 'printf "${RED}%s: %s\e[m\n" "BOO!" $?' ERR # EXIT
    # trap 'echo LEAVING: $?' EXIT

    git fetch
    # git pull --rebase --autostash

    arg=$#
    VAR1="c" # commit_right_away: gc y c
    while true; do
        if [ $# -eq 0 ]
        then
            read -p "#> Would you like to squash into the latest commit? [Y/n] exit [e]: " yn
        else
            arg=0
            yn=$1
        fi

        case $yn in
            [Yy]* )
		cd $base_dir
		git reset --soft HEAD~1
		git add -A .
		if [ -z "$2" ]
		then # if second argument (c) is not provided
		    git commit --quiet --no-verify --edit \
			-m "$(git log --format=%B --reverse HEAD..HEAD@{1})" \
			-m "$(cat ~/.git_commit_template.txt)"
		else  # (c) is provided:
		    if [ "$2" = "$VAR1" ]; then
			git commit --quiet --no-verify -m "$(git log --format=%B --reverse HEAD..HEAD@{1})"
		    else
			echo "Not committed"
		    fi
		fi
		git push -f --quiet 2>&1 &
		echo -e "${GREEN}Committed. Please wait few seconds for git to push${NC}"
		cd $current_dir
		exit
		;;
            [Nn]* )
		cd $base_dir
		git add -A .

		# To prevent commit empty commit message
		git commit --no-verify --quiet --edit \
                    -m "Fix" \
                    -m "$(cat ~/.git_commit_template.txt)"
		git push -f --quiet 2>&1 &
		echo -e "${GREEN}Committed. Please wait few seconds for git to push${NC}"
		cd $current_dir
		exit 0
		;;
            [Ee]* )
		echo "exit"
		exit 1
		;;
            * )
		echo "exit"
		exit 0
		;;
        esac
    done
}

# Thanks to -E / -o errtrace, this still triggers the trap,
# even though the failure occurs *inside the function*.
func $1 $2