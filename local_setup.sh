#!/bin/bash
echo "========================================================="
echo "Setting up Local environment"

if [ -d ".env" ];
then
	echo ".env folder already exists. Installing using pip"
else
	echo "Creating environment and isntalling using pip"
	python3 -m venv .env
fi

. .env/bin/activate


pip install --upgrade pip
pip install -r requirements.txt

deactivate