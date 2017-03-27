# Indiecoin

IndieCoin is a vanilla implementation of a decentralized cryptocurrency. A cryptocurrency is a digital asset that can work as a medium of exchange using cryptographic principles to ensure security. 

This is not a production project nor should it be used as an actual implementation of a cryptocurrencty. It is just a simple proof of concept of a blockchain. There are many security features not being considered and no optimization has been done. This project was done as second partial project for a software architecture class.

---
## Install
### Requirements
  - python 2.7

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

The program is ready to use you can begin by running 
```
$ python indiecoin-node.py --initial-peers 104.131.120.174:6666
```
Wil begin a peer with a DNS seed pointing a server running an indiecoin. If the application is not in the server, you can just add the ip and port of any other peer running the client.

A more detailed documentation of parameters will be seen below.

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

## Coding standard
The project was done using [pep8](https://www.python.org/dev/peps/pep-0008/) coding standard. [flake8](https://pypi.python.org/pypi/flake8) was used as a linter to verify that the standard was being followed. To verify standar in project just navigate to root and type
```
$ flake8
```
If there are any errors in the style it will show it as output.
flake8 configuration file can be found in the root of the repo.

### Todos

 - Write MOAR Tests
 - Work with orphan blocks validations
 - A lot more validations

License
----
MIT
