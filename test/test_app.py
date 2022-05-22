import unittest
from unittest import result
import numpy as np
from app import app
from game.game_engine import GameEngine
import requests
from flask import Flask, jsonify, render_template
#Flask-Redis Bridge
from flask_redis import FlaskRedis
#waitress server for deployment

class TestBase(unittest.TestCase):
    #Reference started app
    def setUp(self):
        self.app = app.test_client()
        #Connect Redis DB
        self.redis_client = FlaskRedis(app)
        #Initialize Game: height = 50 fields, width = 50 fields
        self.game_client = GameEngine(self.redis_client, 50, 50)
        return app

    #Tear down after test
    def tearDown(self):
        pass

# -----------------  Tests -------------------------

#Test GET HTML response
class TestBasicFunctions(TestBase):
    #Test if HTML is properly shown by searching for the word malicious in the description
    def test_RedisPosition(self):
        self.assertIn(self.game_client.get_redis_position(10,20), "10,20")
        self.assertIn(self.game_client.get_redis_position(5,"test"), "5,test")
        self.assertIn(self.game_client.get_redis_position(43,92321), "43,92321")
        self.assertIn(self.game_client.get_redis_position(-43,-92321), "-43,-92321")

    def test_is_valid_position(self):
        self.assertTrue(self.game_client.is_valid_position(3,6))
        self.assertFalse(self.game_client.is_valid_position(366,699))
        self.assertFalse(self.game_client.is_valid_position(4,699))
        self.assertFalse(self.game_client.is_valid_position(111,2))
        self.assertFalse(self.game_client.is_valid_position(-366,-699))
        self.assertTrue(self.game_client.is_valid_position(0,0))
        self.assertFalse(self.game_client.is_valid_position(-1,-1))

    def test_set_element(self):
        self.assertTrue(self.game_client.set_element(41,2,"robot", "right"))
        self.assertFalse(self.game_client.set_element(-2,-3, "dinosaur"))
        self.assertFalse(self.game_client.set_element(50,50, "robot", "left"))

    def test_get_element(self):
        self.game_client.create_robot(2,3,"up")
        self.assertTrue(self.game_client.get_element(2,3))
        self.assertTrue(self.game_client.get_element(33,3))
        self.assertFalse(self.game_client.get_element(500,1))
        self.assertFalse(self.game_client.get_element(50,50))        
        self.assertTrue(self.game_client.get_element(0,0))        

    def test_CreateRobot(self):
        self.assertTrue(self.game_client.create_robot(10,4,"up"))
        self.assertFalse(self.game_client.create_robot(40,432,"up"))
        self.assertTrue(self.game_client.create_robot(10,4,"down"))
        self.assertRaises(ValueError, lambda: self.game_client.create_robot(22,10,""))
        self.game_client.create_robot(18,23, "right")
        self.assertTrue(self.game_client.is_occupied_position(18,23))

    def test_CreateDinosaur(self):
        self.assertTrue(self.game_client.create_dinosaur(2,3))
        self.assertFalse(self.game_client.create_dinosaur(-2,0))
        self.assertFalse(self.game_client.create_dinosaur(2,300))
        self.game_client.create_dinosaur(4,8)
        self.assertTrue(self.game_client.is_occupied_position(4,8))

    def test_is_occupied_position(self):
        self.assertFalse(self.game_client.is_occupied_position(2,4))
        self.assertRaises(ValueError, lambda: self.game_client.is_occupied_position(-23,4))
        self.assertRaises(ValueError, lambda: self.game_client.is_occupied_position(50,50))
        self.assertRaises(ValueError, lambda: self.game_client.is_occupied_position(51,51))
        self.assertFalse(self.game_client.is_occupied_position(0,0))
        self.game_client.create_dinosaur(4,6)
        self.assertTrue(self.game_client.is_occupied_position(4,6))

    def test_is_valid_type(self):
        self.assertTrue(self.game_client.is_valid_type("robot"))
        self.assertTrue(self.game_client.is_valid_type("dinosaur"))
        self.assertTrue(self.game_client.is_valid_type(""))
        self.assertFalse(self.game_client.is_valid_type("  "))
        self.assertFalse(self.game_client.is_valid_type(423))

    def test_is_valid_command(self):
        self.assertTrue(self.game_client.is_valid_command("attack"))
        self.assertTrue(self.game_client.is_valid_command("forward"))
        self.assertTrue(self.game_client.is_valid_command("backward"))
        self.assertTrue(self.game_client.is_valid_command("turn_left"))
        self.assertTrue(self.game_client.is_valid_command("turn_right"))
        self.assertFalse(self.game_client.is_valid_command("attacks"))
        self.assertFalse(self.game_client.is_valid_command(321))

    def test_is_valid_orientation(self):
        #dinosaur defaut. valid orientations none
        self.assertFalse(self.game_client.is_valid_orientation("up"))
        self.assertFalse(self.game_client.is_valid_orientation("down"))
        self.assertFalse(self.game_client.is_valid_orientation("left"))
        self.assertFalse(self.game_client.is_valid_orientation("right"))
        self.assertFalse(self.game_client.is_valid_orientation("error"))
        self.assertTrue(self.game_client.is_valid_orientation(""))

        #valid orientations for robots
        self.assertTrue(self.game_client.is_valid_orientation("up", "robot"))
        self.assertTrue(self.game_client.is_valid_orientation("down", "robot"))
        self.assertTrue(self.game_client.is_valid_orientation("left", "robot"))
        self.assertTrue(self.game_client.is_valid_orientation("right", "robot"))
        self.assertFalse(self.game_client.is_valid_orientation("error", "robot"))
        self.assertFalse(self.game_client.is_valid_orientation("", "robot"))

        #valid orientations for "" none object. Only "" is valid
        self.assertFalse(self.game_client.is_valid_orientation("up", ""))
        self.assertFalse(self.game_client.is_valid_orientation("down", ""))
        self.assertFalse(self.game_client.is_valid_orientation("left", ""))
        self.assertFalse(self.game_client.is_valid_orientation("right", ""))
        self.assertFalse(self.game_client.is_valid_orientation("error", ""))
        self.assertTrue(self.game_client.is_valid_orientation("", ""))

    def test_simulate_movement(self):
        self.game_client.create_robot(4, 2, "down")
        self.game_client.create_dinosaur(5,1)
        self.game_client.simulate_movement(4,2,13,7, "up")
        self.assertTrue(self.game_client.get_element(13,7))
        self.assertTrue(self.game_client.get_element(4,2) == ("", ""))

    def test_command_robot(self):
        self.game_client.create_dinosaur(13,13)
        self.game_client.create_robot(18,2, "down")
        self.game_client.create_dinosaur(18,3)
        self.assertTrue(self.game_client.is_occupied_position(18,3))
        self.assertTrue(self.game_client.command_robot(18,2,"attack"))
        self.assertRaises(ValueError, lambda: self.game_client.command_robot(13,13, "attack"))
        #Dinosaur destroyed by attack of robot?
        self.assertFalse(self.game_client.is_occupied_position(18,3))

        #test forward movement
        self.assertFalse(self.game_client.is_occupied_position(19,2))
        self.game_client.command_robot(18,2,"forward")
        self.assertFalse(self.game_client.is_occupied_position(18,2))
        self.assertTrue(self.game_client.is_occupied_position(19,2))

        #test backward movement and turn movement
        self.game_client.command_robot(19,2, "turn_left")
        self.game_client.command_robot(19,2, "backward")
        self.game_client.command_robot(19,1, "turn_left")
        self.assertTrue(self.game_client.is_occupied_position(19,1))
        self.assertFalse(self.game_client.is_occupied_position(19,2))

    def test_get_playing_field_state(self):
        self.game_client = GameEngine(self.redis_client, 50, 50)
        self.game_client.create_dinosaur(13,4)
        state_array = self.game_client.get_playingfield_state()
        self.assertTrue(next(item for item in state_array if item["type"] == "dinosaur"))
        self.assertRaises(Exception, lambda: next(item for item in state_array if item["type"] == "robot"))
        self.game_client.create_robot(15,9, "down")
        state_array = self.game_client.get_playingfield_state()
        self.assertTrue(next(item for item in state_array if item["type"] == "robot"))
        
class TestAPI(TestBase):
    def test_api_robot_creation(self):
        self.game_client = GameEngine(self.redis_client, 50, 50)
        self.assertEqual(self.app.put("/robot/30/20/up").data.decode("utf-8"), "Robot successfully created.")
        self.assertEqual(self.app.put("/robot/550/230/right").data.decode("utf-8"), "Robot creation failed.")
        
    def test_api_dinosaur_creation(self):
        self.game_client = GameEngine(self.redis_client, 50, 50)
        self.assertEqual(self.app.put("/dinosaur/11/15").data.decode("utf-8"), "Dinosaur successfully created.")
        self.assertEqual(self.app.put("/dinosaur/333/-0").data.decode("utf-8"), "Dinosaur creation failed.")

    def test_api_display_state(self):
        self.game_client = GameEngine(self.redis_client, 50, 50)
        self.assertNotIn("dinosaur", self.app.get("/state").data.decode("utf-8"))
        self.game_client.create_dinosaur(12,14)
        self.assertIn("dinosaur", self.app.get("/state").data.decode("utf-8"))
        self.game_client.create_robot(13,14,"up")
        self.game_client.command_robot(13,14,"attack")
        self.assertIn("robot", self.app.get("/state").data.decode("utf-8"))
        self.assertNotIn("dinosaur", self.app.get("/state").data.decode("utf-8"))
    
    def test_command(self):
        self.game_client = GameEngine(self.redis_client, 50, 50)
        self.app.put("/robot/11/22/left")
        self.assertEqual(self.app.put("/command/11/22/turn_left").data.decode("utf-8"), "Command successfully executed.")
        self.assertEqual(self.app.put("/command/12/22/attack").data.decode("utf-8"), "An internal Server Error has occured.")
        self.assertEqual(self.app.put("/command/11/22/attack").data.decode("utf-8"), "Command successfully executed.")
        self.assertEqual(self.app.put("/command/11/22/turn_right").data.decode("utf-8"), "Command successfully executed.")
        self.assertEqual(self.app.put("/command/11/22/forward").data.decode("utf-8"), "Command successfully executed.")

    def test_command_display_creation_combination(self):
        self.game_client = GameEngine(self.redis_client, 50, 50)
        self.app.put("/robot/30/20/up")
        self.app.put("/dinosaur/30/21")
        self.app.put("/dinosaur/30/22")
        self.app.put("/command/30/20/attack")
        self.assertIn("dinosaur", self.app.get("/state").data.decode("utf-8"))
        self.assertIn("robot", self.app.get("/state").data.decode("utf-8"))
        self.app.put("/robot/31/22/up")
        self.app.put("/command/31/22/attack")
        self.assertNotIn("dinosaur", self.app.get("/state").data.decode("utf-8"))

if __name__ == "__main__":
    unittest.main()