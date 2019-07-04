import math
from gaia_router.map_route.map_route import MapRouter as Router
from gaia_router.macros import GPS_PRECISION
from gaia_communication import gaia_communication
import time

TIME_BETWEEN_STOPS = 1


def get_collection_area():
    return [(-15.82395, -47.8449737), (-15.822749, -47.8444752)]


def get_base_location():
    return (-15.82395, -47.8449737)


def get_direction():
    return 0


def get_boat_status():
    status = input("Should i return to base ? ")
    return status


def get_boat_evasion():
    status = input("Should i evade ? ")
    return status


def send_angle(new_direction):
    print("sending angle", new_direction)


def send_point(point_lat, point_long):
    print("sending point", point_lat, point_long)


def get_gps_position():
    lat = 0
    lon = 0
    while lat == 0 and lon == 0:
        lat, lon, speed = gaia_communication.gps_data()
        time.sleep(2)
        print("deu ruim -- ", lat, lon)
    return (lat, lon)


def interrupt():
    #  gaia_communication.interruption_to_esp()
    print("interrupt")


class GaiaControl():

    def __init__(self):
        # TODO change this method to the method of the communication packge
        # that gests the collection area
        points = get_collection_area()

        # TODO change this method to the method of the communication packge
        # that gests the base location
        base = get_base_location()

        # TODO change this method to the method of the communication packge
        # that gests current position
        current_position = get_gps_position()

        # TODO change this method to the method of the communication packge
        # that gests current positio
        self.direction = get_direction()

        self.router = Router(points[0], points[1], current_position, base)
        # TODO init object detection
        self.route = self.router.trace_collection_route()
        self.state = 'collecting'
        self.was_collecting = False
        self.was_returning = False

    def run(self):
        while(self.state != 'final'):
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
        print('gps deu bom porra - ', self.current_position)
        self.router.current_position = self.current_position

        # TODO change to the communication method that gets
        # this information from eletronic
        return_to_base = get_boat_status()

        if(return_to_base == 'yes' and (self.state != 'returning_to_base')):
            if(self.state == "collecting"):
                self.was_collecting = True
                self.current_position
                self.route = [self.current_position] + self.route
                self.collection_route = self.route
            self.route = self.router.trace_route_to_base() + self.route
            self.state = 'returning_to_base'
            return

        new_direction = self.direction_change_angle()
        direction_diference = new_direction - self.direction
        print("---", new_direction, "---", self.direction)
        if(direction_diference != 0):
            if(direction_diference > 0):
                direction_diference += (2*math.pi)
            # TODO change to the communication method that
            # sends this information to eletronic
            # TODO wait for the response
            send_angle(float(direction_diference))
            self.direction = new_direction
            return

        # TODO change to the communication method that gets
        # this information from eletronic
        evasion = get_boat_evasion()

        if(evasion == 'yes' and (self.state != 'evading')):
            if(self.state == "returning_to_base"):
                self.was_returning = True
                self.return_route = self.route
            elif(self.state == "collecting"):
                self.was_collecting = True
                self.collection_route = self.route
            self.state = 'evading'
            self.route = self.router.trace_evasion_route(
                self.route, self.direction)
            return

        # TODO change to the communication method that
        # sends this information to eletronic
        # TODO wait for the response
        print(self.current_position, type(self.current_position))
        print(self.route[0], type(self.route[0]))

        # chage this method to return only the real distance
        dist = (Router._calculate_real_distance(
            self.current_position, self.route[0]))[0]

        if(dist <= GPS_PRECISION):
            self.route.pop(0)
            return
        send_point(float(self.route[0][0]), float(
            self.route[0][1]))
        time.sleep(TIME_BETWEEN_STOPS)
        interrupt()

    # method responsible to control the boat when in the default collection
    # route
    def collecting(self):
        if(self.route == []):
            self.state = 'returning_to_base'
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
                return angle + (3*math.pi/4)
        else:
            if(dist_y > 0):
                return angle + math.pi/2
            else:
                return angle + math.pi/4

        return angle


if __name__ == '__main__':
    control = GaiaControl()
    control.run()
