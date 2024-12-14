#!/bin/bash

export PORT=5001
python app.py &

export PORT=5002
python app.py &

export PORT=5003
python app.py &
wait