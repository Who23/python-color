#!/bin/bash

chmod +x ./python-color
if [[ $2 -eq 1 ]]
then
    echo "not removing files for dev :)"
else
    rm ./setup.sh
    rm ./disp2.png
    rm ./README.md
fi

mv ../python-color ~/.python-color

pathtest="$(echo $PATH | grep 'python-color')"
if [[ $pathtest == $PATH ]]
then
    echo "python-color has already been installed in PATH"
else
    echo 'PATH=$PATH:$HOME/.python-color' | cat - ~/$1 > temp && mv temp ~/$1
    echo "modified PATH in ~/$1 at line 1"
fi

echo -e '\033[34m=====================================================\033[0m'
echo -e '\033[32m\033[1mpython-color\033[0m\033[1m has been installed!'
echo -e 'restart your terminal and type \033[32mpython-color\033[0m\033[1m to use!\033[0m'
echo -e '\033[34m=====================================================\033[0m'
