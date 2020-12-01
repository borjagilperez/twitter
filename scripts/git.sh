#!/bin/bash

PS3="Please select your choice: "
options=(
    "Start release/hotfix" \
    "Push origin master-develop-tags" \
    "Quit")

select opt in "${options[@]}"; do
    case $opt in
        "Start release/hotfix")
            git status && echo ''
            read -p 'Have you committed the changes? [y/N]: ' RESP_COMMIT
            case $RESP_COMMIT in
                'y'|'Y')
                    read -p 'Start release or hotfix? [RELEASE/hotfix]: ' RESP_BRANCH
                    case $RESP_BRANCH in
                        "")
                            BRANCH='release'
                            ;;
                        'release'|'RELEASE'|'hotfix'|'HOTFIX')
                            BRANCH=$RESP_BRANCH
                            ;;
                        *)
                            echo "Invalid option"
                            break
                            ;;
                    esac

                    eval "$($HOME/miniconda/bin/conda shell.bash hook)"
                    conda activate base && conda info --envs
                    echo 'Increment the <major> version when you make incompatible API changes.'
                    echo 'Increment the <minor> version when you add functionality in a backwards-compatible manner.'
                    echo 'Increment the <patch> version when you make backwards-compatible bug fixes.'
                    read -p 'Increment for repository: ' NAME

                    CURR_VERSION=$(cat ./VERSION | awk -F' ' 'NR==1{print $1}')
                    bumpversion --current-version $CURR_VERSION $NAME ./VERSION
                    NEW_VERSION=$(cat ./VERSION | awk -F' ' 'NR==1{print $1}')
                    git restore ./VERSION
                    git flow $BRANCH start v$NEW_VERSION
                    bumpversion --current-version $CURR_VERSION $NAME ./VERSION
                    git add --all && git commit -m "refactor: repo version $NEW_VERSION"
                    ;;
                'n'|'N'|"")
                    echo 'Commit the changes first.'
                    ;;
                *)
                    echo "Invalid option"
                    break
                    ;;
            esac
            break
            ;;

        "Push origin master-develop-tags")
            git config credential.helper cache
            git push origin master
            git push origin develop
            git push origin --tags
            git remote prune origin
            break
            ;;
            
        "Quit")
            break
            ;;
        *)
            echo "Invalid option"
            break
            ;;
    esac
done
