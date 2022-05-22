# Solution Coding-Challange - Robots vs Dinosaurs
## Flask as REST-API and Redis as database for the game
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)

Grover is assembling an army of remote-controlled robots to fight the dinosaurs and the first step towards that is to run simulations on how they will perform. You are tasked with implementing a service that provides a REST API to support those simulations

## Features
- Able to create an empty simulation space - an empty 50 x 50 grid;
- Able to create a robot in a certain position and facing direction;
- Able to create a dinosaur in a certain position;
- Issue instructions to a robot - a robot can turn left, turn right, move forward, move backward, and attack;
- A robot attack destroys dinosaurs around it (in front, to the left, to the right or behind);
- Dinosaurs don't move;
- Display the simulation's current state;
- Two or more entities (robots or dinosaurs) cannot occupy the same position;
- Attempting to move a robot outside the simulation space is an invalid operation.
- 100% coverage ofUnit- and Integrationtests.

## Quick Start with Docker Compose

```shell
docker-compose up -d
```

## API-Commands for CURL and / or Browser
### Create Robot at a certain position (width, height) and a certain orientation (up, left, down, right)
```shell
#PUT Request
http://localhost:5000/robot/<width>/<height>/<orientation>
```
### Create a Dinosaur at a certain position (width, height). Dinosaurs don't have an orientation
```shell
#PUT Request
http://localhost:5000/dinosaur/<width>/<height>
```
### Get the current state of the game as JSON. Returns width, height, type (robot, dinosaur, empty) and orientation ("only relevant for robots")
```shell
#GET Request
http://localhost:5000/dinosaur/state
```
### Issue a command for a robot at a cerain position (width, height) on the playing field. Possible commands (forward, backward, attack, turn_left, turn_right)
```shell
#PUT Request
http://localhost:5000/command/<width>/<height>/<command>
```
  
## Thank you
Thank you very much at Grover for the opportunity to join this Coding-Challenge.
