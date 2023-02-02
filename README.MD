# Scrapy Project for Parsing Google Maps Reviews


## Requirements  📌

- Docker 🐳
- Docker-Compose 🐳
- Python >= 3.8


## Getting Started 🚀

1. Build the Docker image:
```
$ docker build -t scrapy-docker .
```
2. Run the Docker container
```
docker run -it scrapy-docker
```
3. Start the Scrapy Crawler from the docker container


## Usage

The following arguments are available:

search      search for the business 
-o      the filename of the csv output file (default is "reviews.csv")

## Output

The Crawler outputs the list of the reviews in a CSV file.


### Testing  🚨
To run the tests for this project run:
```
pytest
```

This will discover and run all tests in the tests/ directory.

You can also run a specific test file or test case by providing the path to the file or the case name:

```
pytest path/to/test_file.py
```