#Main class for the monster chess game. Includes validity checks for players interactions and the game logic.
#Data-Storage is shared among all players with a Redis-DB
class GameEngine:
    def __init__(self, redis_client, max_height, max_width):
        self.playingfield_height = max_height
        self.playingfield_width = max_width
        self.valid_types = ["", "robot", "dinosaur"]
        self.redis_client = redis_client
        self.empty_field = ""
        self.valid_commands = ["turn_left", "turn_right", "forward", "backward", "attack"]
        self.valid_orientation_robots = ["up", "down", "left", "right"]
        self.valid_orientation_miscellaneous = [""]

        #Initiate playing field with 0 as a placeholder for empty fields.
        for index_w in range(self.playingfield_width):
            for index_h in range(self.playingfield_height):
                self.set_element(index_h, index_w, self.empty_field, self.empty_field)

    #----------------------------------------------------
    #----------- User interaction logic  ----------------
    #----------------------------------------------------
        
    def create_robot(self, height, width, orientation):
        return self.set_element(height, width, "robot", orientation)
    
    def create_dinosaur(self, height, width):
        return self.set_element(height, width, "dinosaur")

    def get_playingfield_state(self):
        state_output = []
        for index_w in range(self.playingfield_width):
            for index_h in range(self.playingfield_height):
                type, orientation = self.get_element(index_h, index_w)
                state_output.append({"width": index_w, "height": index_h, "type" : type, "orientation": orientation})
        
        return state_output

    def command_robot(self, height, width, command):
        #check if there is a robot at the position
        type, robot_orientation = self.get_element(height, width)
        
        if not type == "robot":
            raise ValueError("There is no robot at the given height, width position.")
        
        if self.is_valid_command(command):
            if command == "turn_left":
                #cover all 4 orientation cases for turn_left
                if robot_orientation == "up":
                    self.set_element(height, width, "robot", "left")
                elif robot_orientation == "left":
                    self.set_element(height, width, "robot", "down")
                elif robot_orientation == "down":
                    self.set_element(height, width, "robot", "right")
                elif robot_orientation == "right":
                    self.set_element(height, width, "robot", "up")
            elif command == "turn_right":
                #cover all 4 orientation cases for turn_right
                if robot_orientation == "up":
                    self.set_element(height, width, "robot", "right")
                elif robot_orientation == "left":
                    self.set_element(height, width, "robot", "up")
                elif robot_orientation == "down":
                    self.set_element(height, width, "robot", "left")
                elif robot_orientation == "right":
                    self.set_element(height, width, "robot", "down")
            elif command == "forward":
                new_height = height
                new_width = width
                if robot_orientation == "up":
                    new_height -= 1
                elif robot_orientation == "left":
                    new_width -= 1
                elif robot_orientation == "down":
                    new_height += 1
                elif robot_orientation == "right":
                    new_width += 1
                #Move robot forward
                self.simulate_movement(height, width, new_height, new_width, robot_orientation)
            elif command == "backward":
                new_height = height
                new_width = width
                if robot_orientation == "up":
                    new_height += 1
                elif robot_orientation == "left":
                    new_width += 1
                elif robot_orientation == "down":
                    new_height -= 1
                elif robot_orientation == "right":
                    new_width -= 1
                #Move robot backwards
                self.simulate_movement(height, width, new_height, new_width, robot_orientation)
            elif command == "attack":
                #Calc positions from one field to the left, right, up and down
                left_position = {"height": height, "width": (width-1)} 
                bottom_position = {"height": (height-1), "width": width} 
                right_position = {"height": height, "width": (width+1)}   
                top_position = {"height": (height+1), "width": width}                              
                all_positions = (left_position, bottom_position, right_position, top_position)

                #Destroy dinosaurs at all valid adjacent positions
                for position in all_positions:
                    #check if position is within the playing fields boundaries
                    if self.get_element(position["height"], position["width"]):
                        type = self.get_element(position["height"], position["width"])[0]
                        #destroy dinosaur. if empty field already, simply overwrite
                        if not type == "robot":
                            self.set_element(position["height"], position["width"], self.empty_field, self.empty_field)
            return True

    #----------------------------------------------------
    #---------------- CRUD Util methods -----------------
    #----------------------------------------------------

    #Returns the elements type and orientation as a tuple thats at the given height and width coordinates.
    def get_element(self,height,width):
        if self.is_valid_position(height,width):
            redis_position = self.get_redis_position(height, width)
            return self.redis_client.hget(redis_position, "type").decode("utf-8"), self.redis_client.hget(redis_position, "orientation").decode("utf-8")
        return False

    #An element (creature or player) is to be placed at the given height and width. Only players have an orientation
    def set_element(self,height,width, type, orientation = ""):
        #check input value validity
        if not self.is_valid_type(type):
            raise ValueError("Invalid type used for element placement.")
        if not self.is_valid_orientation(orientation, type):
            raise ValueError("Invalid orientation for element placement.")
    
        if self.is_valid_position(height,width):
            redis_position = self.get_redis_position(height, width)
            #execute positioning of element in database
            self.redis_client.hset(redis_position, "type", type)
            self.redis_client.hset(redis_position, "orientation", orientation)               
            return True
        #Something fails before placement of the element
        return False

    #get the redis-entry position for the given height and width position on the playing field
    def get_redis_position(self, height, width):
        return str(height) + "," + str(width)

    #Moves element of type "robot" to new location
    def simulate_movement(self, old_height, old_width, new_height, new_width, orientation):
        #validation of new position
        if not self.is_valid_position(new_height, new_width):
            raise ValueError("Invalid command for robot. Forward would result in Out of Bounds Error.")
        if self.is_occupied_position(new_height, new_width):
            raise ValueError("Robot can't move forward. New location already occupied.")
        
        #Movement simulation
        #remove Robot at old location
        self.set_element(old_height, old_width, self.empty_field, self.empty_field)
        #create Robot at new location
        self.set_element(new_height, new_width, "robot", orientation)
        return True

    #----------------------------------------------------
    #------------------ Validity Checks -----------------
    #----------------------------------------------------

    def is_valid_command(self, command):
        if not command in self.valid_commands:
            return False
        return True

    #checks validity of positional argument. If position exceeds playing field boundaries raise ValueError. If position is valid return True
    def is_valid_position(self, height, width):
        #validity check: position within in the playing field boundaries
        if ((height < 0) or 
            (height >= self.playingfield_height)):
            return False
        if ((width < 0) or 
            (width >= self.playingfield_width)):
            return False

        return True       
    
    def is_occupied_position(self, height, width):
        is_occupied = False

        if not self.is_valid_position(height, width):
            raise ValueError("Invalid position. Check boundaries.")
        
        if not self.get_element(height, width)[0] == self.empty_field:
            is_occupied = True
        return is_occupied

    def is_valid_type(self, type):
        if not type in self.valid_types:
            return False
        return True
    
    def is_valid_orientation(self, orientation, type="dinosaur"):
        valid_orientation = True
        if type == "dinosaur":
            if not orientation in self.valid_orientation_miscellaneous:
                valid_orientation = False
        if type == "robot":
            if not orientation in self.valid_orientation_robots:
                valid_orientation = False
        if type == self.empty_field:
            if not orientation == self.empty_field:
                valid_orientation = False

        return valid_orientation   