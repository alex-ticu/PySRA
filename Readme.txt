Python Screen Recorder and Analyzer.

This is a simple app that captures screen video and audio and reports the volume.

// Setup & Installation

For simple setup:
	- cd to root directory of repo
	$ bash ./setup.sh

After running ./setup.sh use:
	$ source virtualEnvironment/devEnv/bin/activate
to activate the python environment.

This project was created and tested on Ubuntu 20.04 64-bit.
In order to run this project you should make sure that you have 
	- python3
	- python3-pip
	- virtualenv
	- portaudio
	- libsndfile
	- Firefox geckodriver 
installed.

	$ sudo apt update
	$ sudo apt install python3
	$ sudo apt install python3-pip
	$ sudo apt install portaudio19-dev
	$ pip3 install virtualenv

!! Do not install virtualenv from multiple sources (Eg. apt install python3-virtualenv and pip3 install virtualenv)!!
	If you find youself in the above situation, uninstall virtualenv by using "pip3 uninstall virtualenv" and then "sudo apt remove python3-virtualenv" and reinstall using pip3.

//

In order to work on this project you might want to create a new python virtual environment:
	$ virtualenv virtualEnvironment/devEnv
	
	# activate virtual environment:
	$ source virtualEnvironment/devEnv/bin/activate
	
	# install python packages:
	$ pip3 install -r requirements.txt

!! If pyaudio fails to install, please make sure that portaudio.h is visible to your c compiler (Eg. /usr/include/portaudio.h) !!