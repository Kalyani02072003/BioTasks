#!/bin/bash
docker build -t api .
docker run -p 5000:5000 api
