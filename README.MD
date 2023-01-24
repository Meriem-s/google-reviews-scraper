# Google Review Scraper Project

A brief description of the project and its purpose.

## Getting Started
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.
## Prerequisites
Python3 or Docker

## Installation 
First clone the repository as follows
``` git clone https://github.com/username/projectname.git ```

### Local Installation using venv

1.  Create virtual environment using venv
``` python3 -m venv venv ```
2. Activate virtual enviroment
``` source venv/bin/activate ```

2. Install the dependencies
``` pip install -r requirements.txt ```

3. under  creds.py add the API_KEY
``` API_KEY = <YOUR_API_KEY> ```

4. Run the spider
``` scrapy crawl spider_name```

### Docker Installation
2. Build the docker image  then start the container

``` docker-compose up --build ```

### Run the Spider
1. Install the dependencies related to the development environment 
``` docker-compose run scrapy scrapy crawl <> ```

### Run Tests
1. Install the dependencies related to the development environment 
``` pip install -r requirements-dev.txt ```

2. Run tests
```  ```

## Built With
Scrapy - The web framework used
Python - Programming language

## Authors
Your Name - Initial work - username

## License
This project is licensed under the MIT License - see the LICENSE.md file for details
