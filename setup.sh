#!/bin/bash

chmod +x ./python-color
if [[ $2 -eq 1 ]]
then
    echo "not removing setup.sh :)"
else
    rm setup.sh
fi
#mv ../python-color ~/.python-color

pathtest="$(echo $PATH | grep 'python-color')"
if [[ $pathtest == $PATH ]]
then
    echo "python-color has already been installed in PATH"
else
    echo 'export PATH="$($HOME/.python-color)"' >> ~/$1
fi