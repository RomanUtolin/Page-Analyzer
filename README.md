### Hexlet tests and linter status:
[![Actions Status](https://github.com/RomanUtolin/python-project-83/workflows/hexlet-check/badge.svg)](https://github.com/RomanUtolin/python-project-83/actions)
[![flake8](https://github.com/RomanUtolin/python-project-83/actions/workflows/flake8.yml/badge.svg)](https://github.com/RomanUtolin/python-project-83/actions/workflows/flake8.yml)
[![Maintainability](https://api.codeclimate.com/v1/badges/01bc8c84e510be5582d9/maintainability)](https://codeclimate.com/github/RomanUtolin/python-project-83/maintainability)
### Description of project:
Page Analyzer - a site that analyzes the specified pages for SEO suitability
### App on Railway: [Page Analyzer](https://python-project-83-production-481c.up.railway.app/)
### Install 

````
git clone git@github.com:RomanUtolin/python-project-83.git
````
````
add '.env' in the root directory of your project

    add DATABASE_URL - Flask app secret key
    add SECRET_KEY - Database connection url
````
````
make install
````
````
make start (to start Development Server)
or
make dev (to start gunicorn)
````