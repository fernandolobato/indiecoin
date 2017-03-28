# Indiecoin

IndieCoin is a vanilla implementation of a decentralized cryptocurrency. A cryptocurrency is a digital asset that can work as a medium of exchange using cryptographic principles to ensure security. 

This is not a production project nor should it be used as an actual implementation of a cryptocurrencty. It is just a simple proof of concept of a blockchain. There are many security features not being considered and no optimization has been done. This project was done as second partial project for a software architecture class.

---
## Install
### Requirements
  - python 2.7
  - sqlite3

The project is made to be a pure pythonic implementation of a vanilla blockchain. The only library used was copied into the repo so no dependendies were required.

##### Virtual Enviornment
The recommended installation is to use a virtual enviornment. Some recommendations are:
- [virtualenv](https://python-docs.readthedocs.io/en/latest/dev/virtualenvs.html)
- [anaconda](https://www.continuum.io/downloads)

clone the repo
```
$ git clone https://github.com/fernandolobato/indiecoin.git
$ cd indiecoin/
$ pip install -r requirements.txt
```

The program is ready to use you can begin by running. To run a normal node just run the following command.
```
$ python indiecoin-node.py --initial-peers 104.131.120.174:6666
```

Wil begin a peer with a DNS seed pointing a server running an indiecoin. If the application is not in the server, you can just add the ip and port of any other peer running the client.

A more detailed documentation of parameters will be seen below.

To run a miner node just run with the --mine flag set to true. In the program by default its set to false.

```
python indiecoin-node.py  --initial-peers 104.131.120.174:6666 --mine True
```

---

## Library Overview
- ```indiecoin.blockchain``` - Manages blocks, transactions and database operations
- ```indiecoin.miner``` - Manages mining new blocks
- ```indiecoin.node``` - Connects to peer-to-peer network, mantains communication
- ```indiecoin.util``` - usefull things
- ```indiecoin.wallet``` - address management

## Tests
Unit test can be found under test folder.
To run unit test navigate to test folder and run:
```
$ cd tests
$ python -m unittest discover --pattern=*.py
```

## Libraries
- [python ecdsa](https://github.com/warner/python-ecdsa)
- [BerryTella P2P framework](ttp://cs.berry.edu/~nhamid/p2p/btpeer.py)

## Documentation
For documentation [numpy](https://github.com/numpy/numpy/blob/master/doc/example.py) documentation style was followed in a very slight way. All methods and classes have their respective docstrings.

All the required documentation for the class can be found under the docs folder.

## Coding standard
The project was done using [pep8](https://www.python.org/dev/peps/pep-0008/) coding standard. [flake8](https://pypi.python.org/pypi/flake8) was used as a linter to verify that the standard was being followed. To verify standar in project just navigate to root and type
```
$ flake8
```
If there are any errors in the style it will show it as output.
flake8 configuration file can be found in the root of the repo.

## User Guide

The simple way to run the system is to run a node. This can be done running. This will run a node that is ready to listen to peers, if another peer has the peer in his peer list it can start interacting. 

```
$ python indiecoin-node.py
```

The node can recieve a list of peers in the form host:port to which it should communicate and sync-up on start.

```
$ python indiecoin-node.py --initial-peers 0.0.0.0:6666,0.0.0.1:7777
```

You can also send a flag to the program to run a full mining node, if not you will jsut be listening and relaying transactions and blocks

```
$ python indiecoin-node.py --miner True
```

You can limit the number of peers the node keeps track off using the mas peers flag (the deafult value is 50)

```
$ python indiecoin-node.py --max-peers [num_peers]
```

You can bind the program to a specific ip address, using the --bind flag, the program uses the 0.0.0.0 address by default which is the system's ip address.

```
$ python indiecoin-node.py --bind 192.168.32.1
```

You can also specify the port at which the program runs, the default is 6666

```
$ python indiecoin-node.py --port 6666
```

The system uses sqlite3 for database operations. The blockchain is kept locally at ~/.indiecoin/data/


### Todos

 - Write MOAR Tests
 - Work with orphan blocks validations
 - A lot more validations

License
----
MIT
