#!/bin/bash

# Script used to automate the setup of the environment

virtualEnvPath='virtualEnvironment/devEnv'

python3Path=$(which python3)

if [ $? -eq  0 ]
then
	echo "Python3 installed at ${python3Path}"
else
	echo "Installing python3..."
	sudo apt install python3
fi;

pip3Path=$(which pip3)

if [ $? -eq 0 ]
then
	echo "Pip3 installed at ${pip3Path}"
else
	echo "Installing pip3"
	sudo apt install python3-pip
fi;

# portaudio.h is needed to install pyaudio
if [[ -e /usr/local/include/portaudio.h ]] || [[ -e /usr/include/portaudio.h ]]
then
	echo "portaudio.h found"
else
	echo "poraudio.h not found... Installing portaudio"
	#sudo apt-get install portaudio19-dev
fi;

echo 'Installing python3 required packages...'

pip3 install -r requirements.txt

if [ $? -ne 0 ]
then
	echo "Could not install packages..."
	exit 1
fi

virtualenv ${virtualEnvPath}
source ${virtualEnvPath}/bin/activate

echo 'Installing geckodriver...'

cp external/geckodriver ${virtualEnvPath}/bin/
