#!/bin/bash

PS3="Please select your choice: "
options=(
    "Install twitter_env" \
    "Recreate twitter_env" \
    "Uninstall twitter_env" \
    "Clean" \
    "Clean and build" \
    "View distribution" \
    "Install package in develop mode" \
    "Install package" \
    "View installation" \
    "Open Spyder" \
    "Start notebook" \
    "Quit")

select opt in "${options[@]}"; do
    case $opt in
        "Install twitter_env")
            eval "$($HOME/miniconda/bin/conda shell.bash hook)"
            conda activate base && conda info --envs
            conda env create -f ./scripts/local/environment.yml
            conda activate twitter_env && conda info --envs
            break
            ;;

        "Recreate twitter_env")
            eval "$($HOME/miniconda/bin/conda shell.bash hook)"
            conda activate base && conda info --envs
            conda remove -y -n twitter_env --all
            conda env create -f ./scripts/local/environment.yml
            break
            ;;

        "Uninstall twitter_env")
            eval "$($HOME/miniconda/bin/conda shell.bash hook)"
            conda activate base && conda info --envs
            conda remove -y -n twitter_env --all
            break
            ;;

        "Clean")
            cd ./src/main/python
            find . -type d -name __pycache__ -exec rm -r {} +
            rm -fr ./build ./dist ./*.egg-info
            break
            ;;

        "Clean and build")
            cd ./src/main/python
            find . -type d -name __pycache__ -exec rm -r {} +
            rm -fr ./build ./dist ./*.egg-info
            
            eval "$($HOME/miniconda/bin/conda shell.bash hook)"
            conda activate twitter_env && conda info --envs
            which python3 && python3 setup.py sdist bdist_wheel
            break
            ;;

        "View distribution")
            cd ./src/main/python
            if ls ./dist/*.whl 1> /dev/null 2>&1; then
                unzip -l ./dist/*.whl
                echo -e "\nDirectory:  $(pwd)"
                NAME=$(ls ./dist/*.whl | awk -F'/' 'NR==1{print $5}' | awk -F'-' 'NR==1{print $1}')
                find ./dist -name "*$NAME*"
            fi
            break
            ;;

        "Install package in develop mode")
            cd ./src/main/python
            eval "$($HOME/miniconda/bin/conda shell.bash hook)"
            conda activate twitter_env && conda info --envs
            pip3 install -e .
            break
            ;;

        "Install package")
            cd ./src/main/python
            eval "$($HOME/miniconda/bin/conda shell.bash hook)"
            conda activate twitter_env && conda info --envs
            pip3 install .
            break
            ;;

        "View installation")
            cd ./src/main/python
            eval "$($HOME/miniconda/bin/conda shell.bash hook)"
            conda activate twitter_env && conda info --envs
            NAME=$(ls ./dist/*.whl | awk -F'/' 'NR==1{print $3}' | awk -F'-' 'NR==1{print $1}')
            find $(conda info --envs | grep "*\**" | awk -F' ' 'NR==1{print $3}') -name "*$NAME*"
            break
            ;;

        "Open Spyder")
            eval "$($HOME/miniconda/bin/conda shell.bash hook)"
            conda activate twitter_env && conda info --envs
            spyder 1> /dev/null 2>&1 &
            break
            ;;

        "Start notebook")
            eval "$($HOME/miniconda/bin/conda shell.bash hook)"
            conda activate twitter_env && conda info --envs
            cd $HOME
            jupyter notebook
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
