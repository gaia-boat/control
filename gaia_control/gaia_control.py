import math
from gaia_router.map_route.map_route import MapRouter as Router
from gaia_router.macros import GPS_PRECISION
from gaia_communication import gaia_communication
# from image_processing import capture
import time
import os

TIME_BETWEEN_STOPS = 1
MESSAGE_START_SIGNAL = "i"


def get_boat_evasion():
    # status = capture()
    status = input("evade? ")
    if(status == '1'):
        return True
    else:
        return False
    return status


def get_gps_position():
    os.system("sudo gpsd /dev/serial0 -F /var/run/gpsd.sock")
    lat, lon, speed = gaia_communication.gps_data()
    os.system("sudo killall gpsd")
    return (lat, lon)


def send_activate_collection(activate_collection):
    print("esteira ativada ", activate_collection)
    if(activate_collection):
        message = '1,'
    else:
        message = '0,'
    return message


def send_angle(new_direction):
    if(new_dire
    print("sending angle", new_direction)
    message = str(new_direction)+','

    return message


def send_point(point_lat, point_long):
    message = str(point_lat) + ','
    message += str(point_long) + ','
    print("message",message)
    return message


def send_go(go):
    print("sending go", go)
    return message + ','


class GaiaControl():

    def __init__(self):

        os.system('sudo systemctl stop gpsd.socket')
        os.system('sudo systemctl disable gpsd.socket')

        self.recive_first_message()

        self.route = self.router.trace_collection_route()
        print("-----collection route------",self.route)
        self.state = 'collecting'
        self.was_collecting = False
        self.was_returning = False
        self.activate_collection = True
        self.go = 's'
        self.angle_to_send = 0

    def send_information(self):
        message = send_go(self.go)
        message += send_point(self.current_position[0],
                              self.current_position[1])
        print("sending message - ", message)
#        gaia_communication.data_sender(message)
        if(self.go == 'g'):
            self.current_position = get_gps_position()
#            time.sleep(TIME_BETWEEN_STOPS)
            a = input("waiting to go") 
            self.go = 's'
            self.send_information()

    def recive_first_message(self):

        # message = gaia_communication.data_receiver()
        # message = message.split(',')
        self.current_position = get_gps_position()
        print(self.current_position)
        a = input()
        aux = get_gps_position()
        # self.router = Router((float(message[0]), float(message[1])), (float(
        # message[2]), float(message[3])), self.current_position,
        # self.current_position)
        self.router = Router(self.current_position, aux,
                             self.current_position, self.current_position)

        self.direction = 0
        self.activate_collection = False

    def recive_message(self):
        message = gaia_communication.data_receiver()
        message = message.split(',')
        if(int(message[0]) == 1):
            is_too_heavy = True
        else:
            is_too_heavy = False
        distance = int(message[1])
        if(distance > 4 and distance < 15):
            is_full = True
        else:
            is_full = False
        self.status = is_full or is_too_heavy

    def run(self):
        while(self.state != 'final'):
            print("current state -", self.state)
            print("current route -", self.route)
            self.send_information()
            if(self.state == 'collecting'):
                self.collecting()
            elif(self.state == 'evading'):
                self.evading()
            elif(self.state == 'returning_to_base'):
                self.returning_to_base()
            elif(self.state == 'waiting'):
                self.waiting()
            else:
                self.state = 'final'

    # This method is responsible to control the boat actions when in route
    def in_route(self):

        # TODO change this method to the eletronic method
        self.current_position = get_gps_position()
        # chage this method to return only the real distance
        dist = (Router._calculate_real_distance(
            self.current_position, self.route[0]))[0]
        print("-------------------------------------------------------------")

        if(dist < GPS_PRECISION/2):
            self.route.pop(0)
            print("******reomoving point******")
            if(self.route != []):
                self.in_route()
            return

        self.recive_message()

        evasion = get_boat_evasion()

        self.position_to_send = self.current_position
        self.activate_collection = self.activate_collection
        self.go = 's'

        self.router.current_position = self.current_position

        # TODO change to the communication method that gets
        # this information from eletronic

        # if(self.status  and (self.state != 'returning_to_base')):
        if(self.status == '1' and (self.state != 'returning_to_base')):
            if(self.state == "collecting"):
                self.was_collecting = True
                self.current_position
                self.route = [self.current_position] + self.route
                self.collection_route = self.route
                self.activate_collection = False
            self.route = [self.router.base_location]
            self.state = 'returning_to_base'
            print("******status******")
            return

        new_direction = self.direction_change_angle()
        direction_diference = new_direction - self.direction
        print("---", new_direction, "---", self.direction)
        if(direction_diference > 0.05):
            # TODO change to the communication method that
            # sends this information to eletronic
            # TODO wait for the response
            # self.angle_to_send = float(direction_diference)
            new_direction = new_direction % (2*math.pi)
            direction_diference = new_direction - self.direction
            if(direction_diference > 0):
                if(direction_diference >180):
                    self.go = 'l'
                else:
                    self.go = 'r'
            else:
                if(direction_diference < -180):
                    self.go = 'r'
                else:
                    self.go = 'l'

            print("direction changed to --", self.direction)
            print("******change direction******")
            return

        # TODO change to the communication method that gets
        # this information from eletronic
        print("evasion  -  ", evasion)
        if(evasion and (self.state != 'evading')):
            if(self.state == "returning_to_base"):
                self.was_returning = True
                self.return_route = self.route
            elif(self.state == "collecting"):
                self.was_collecting = True
                self.collection_route = self.route
            self.state = 'evading'
            self.route = self.router.trace_evasion_route(
                self.route, self.direction)
            print("******evading******")
            return

        # TODO change to the communication method that
        # sends this information to eletronic
        # TODO wait for the response
        print(self.current_position, type(self.current_position))
        print(self.route[0], type(self.route[0]))

        print("******going******")
        self.go = 'g'

    # method responsible to control the boat when in the default collection
    # route
    def collecting(self):
        if(self.route == []):
            self.state = 'returning_to_base'
            self.route.append(self.router.base_location)
            return
        self.in_route()

    # method responsible to control the boat when in tracing a evasion route
    def evading(self):

        if(self.route == []):
            if(self.was_returning):
                self.state = "returning_to_base"
                self.route = self.return_route
                self.was_returning = False
                self.return_route = []
            elif(self.was_collecting):
                self.state = "collecting"
                self.route = self.collection_route
                self. was_collecting = False
                self.collection_route = []
            return
        self.in_route()

    # method responsible to control the boat when going to base
    def returning_to_base(self):
        if(self.route == []):
            self.state = "waiting"
            return
        self.in_route()

    # method responsible to control the boat when in waiting
    def waiting(self):
        # wait signal

        signal = input("signal? ")
        if(signal != "end" and self.was_collecting):
            self.state = "collecting"
            self.route = self.collection_route
            self. was_collecting = False
            self.collection_route = []
        else:
            self.state = "final"

    def direction_change_angle(self):

        x0 = self.router.current_position[0]
        y0 = self.router.current_position[1]
        x1 = self.route[0][0]
        y1 = self.route[0][1]

        dist_x = x1 - x0
        dist_y = y1 - y0

        if(dist_x == 0 and dist_y == 0):
            return self.direction

        if(dist_x == 0):
            if(dist_y > 0):
                return math.pi/2
            else:
                return 3*math.pi/2

        if(dist_y == 0):
            if(dist_x > 0):
                return 0
            else:
                return math.pi

        tg = abs(dist_y/dist_x)
        angle = math.atan(tg)
        if(dist_x > 0):
            if(dist_y > 0):
                return angle
            else:
                return 2 *math.pi - angle
        else:
            if(dist_y > 0):
                return math.pi - angle
            else:
                return angle + math.pi

        return angle


if __name__ == '__main__':
    control = GaiaControl()
    control.run()
