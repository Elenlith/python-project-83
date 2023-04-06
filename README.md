# Page Analyzer
[![Actions Status](https://github.com/Elenlith/python-project-83/workflows/hexlet-check/badge.svg)](https://github.com/Elenlith/python-project-83/actions)
<a href="https://codeclimate.com/github/Elenlith/python-project-83/maintainability"><img src="https://api.codeclimate.com/v1/badges/6935b60f9d56dd425474/maintainability" /></a>
[![Github Actions Status](https://github.com/Elenlith/python-project-83/actions/workflows/pyci.yml/badge.svg)](https://github.com/Elenlith/python-project-83/actions)

## Description

Page analyzer is a simple web-app getting website base SEO characteristics. 

## The aplication is deployed here
<a href="http://python-project-83-production-b0f6.up.railway.app">python-project-83-production-b0f6.up.railway.app</a>

## How to install and run

1) Clone the repo:
```
git clone https://github.com/Elenlith/python-project-83.git
```
2) Go to python-project-83 directory:
```
cd python-project-83
```
3) Install dependencies (requires Poetry):
```
make install # see Makefile for details
```
4) Add .env file to the project root with DATABASE_URL and SECRET_KEY variables
```
##.env
DATABASE_URL=<insert your link>
SECRET_KEY=<insert your value>
```
5) Run the app using make dev (development mode) or make start (production mode, gunicorn) command
```
make dev # see Makefile for details
```
```
make start # see Makefile for details
```
