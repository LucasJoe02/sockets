# Sockets

A simple server-client socket program

## Description

This python program uses the sockets library to allow a client to query a 
server for the date or time and recieve a response packet back from the server

## Getting Started

### Dependencies

* Python3 must be installed to run the python files

### Installing

* You can install the program by downloading this repo as a zip folder
* Extract the folder on your machine

### Executing program

* Use the command line to navigate to directory containing the server.py and client.py files
* Run the below command to start the the server
```
python3 server.py 'port-1' 'port-2' 'port-3'
```
* Change the three ports to integers between 1,024 and 64,000 without quote marks
* The three ports refer to the language the response packet will be sent in either English, Maori or German for 1, 2 and 3
* Open up a seperate terminal in the same directory and run the following command to run the client
```
python3 client.py 'query' localhost 'port'
```
* Change 'query' to either date or time depending on what you want the server to return
* Change 'port' to one of the ports hosted by the server based on what language you want the server to return the date/time in

## Help

Contact me with any problems or issues.

## Authors

Lucas Redding
[lucasredding07@gmail.com](lucasredding07@gmail.com)

## Version History

* 0.1
    * Initial Release

## License

This project is licensed under the MIT License - see the LICENSE.txt file for details
