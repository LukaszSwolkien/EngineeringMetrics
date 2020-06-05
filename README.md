README
======

This is the library to analyze Jira issues to measure teams efficiency in terms of engineering processes, structure and practices. Metrics once calculated can be later published on the Confluance page (Confluance Jira macros are supported for dynamic data refresh). It is also possible to publish data to the html file. All the setup can be done in jupyter notebooks.
The ultimate goal is to use those metrics to continuously improve efficiency and enable fast delivery

# Setup project

`brew install pipenv`

or

`pip install pipenv`

## install all dependencies for a project (including dev)

`pipenv install --dev`


## activate venv and run jupyter to create notebooks to define metrics

`pipenv shell`

`jupyter notebook`


## if you have notebooks setup you can execute all of them from the command line using below script

`./gen_dashboards.sh`

Go to your Confluance page to see generated dashboard


