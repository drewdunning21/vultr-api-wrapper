# Vultr API Wrapper

This is a python wrapper I have made to interact with the Vultr API

The wrapper has 2 classes: Account and server

## Account Class

* The account class is one that you create first to authenticate your API key
* Once authenticated you can use your account to create servers and see a list of the current servers deployed on your account

## Server Class

* Each server created by your account will have its own server object
* This class can be used to SSH into the server and execute commands
* Can start a server with a start up script if you choose
