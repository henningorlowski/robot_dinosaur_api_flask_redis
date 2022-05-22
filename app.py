#Flask Server and Request-utilities
from flask import Flask
#Redis Server for playingfield-persistence
from redis import Redis
#Waitress server for deployment
from waitress import serve
#Game Logic
from game.game_engine import GameEngine
import json

#Start Flask Server
app = Flask(__name__)
#Connect Redis DB
redis_client = Redis(host = "redis", port = 6379)
#Initialize Game: height = 50 fields, width = 50 fields
game_client = GameEngine(redis_client, 50, 50)

#Create robot at position and with orientation and return success message
@app.route("/robot/<width>/<height>/<orientation>", methods=["PUT"])
def create_robot(width, height, orientation):
	try:
		result = game_client.create_robot(int(height), int(width), orientation)
		if result:
			return "Robot successfully created.", 201
		if not result:
			return "Robot creation failed.", 400
	except:
		return "An internal Server Error has occured."

#Create dinosaur at position and return success message
@app.route("/dinosaur/<width>/<height>", methods=["PUT"])
def create_dinosaur(width, height):
	try:
		result = game_client.create_dinosaur(int(height), int(width))
		if result:
			return "Dinosaur successfully created.", 201
		if not result:
			return "Dinosaur creation failed.", 400
	except:
		return "An internal Server Error has occured."

#Init command for robot at given position and return success message
@app.route("/command/<width>/<height>/<command>", methods=["PUT"])
def init_command(width, height, command):
	try:
		response = ""
		result = game_client.command_robot(int(height), int(width), command)
		if result:
			return "Command successfully executed.", 201
		if not result:
			return "Command failed.", 400
	except:
		return "An internal Server Error has occured."

#Display state of the playing field => every type and orientation of every element on the field
@app.route("/state")
def display_state():
	try:
		result = json.dumps(game_client.get_playingfield_state())
		return result, 201
	except:
		return "An internal Server Error has occured."

if __name__ == "__main__":
	print("Waitress started. API running.")
	#Run WSGI deployment server. Listen @port 5000
	serve(app, host='0.0.0.0', port=5000)
	print("API closed.")