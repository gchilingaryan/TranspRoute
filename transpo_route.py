import json
from urllib.request import urlopen
from gmplot import gmplot
from bus_url import *
import bus_streets

class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class Bus:
    def __init__(self, number, url):
        self.__head = None
        self.__number = number
        self.__url = url

    def append(self, street):
        if self.__head == None:
            self.__head = Node(street)
        else:
            temp = self.__head
            while temp.next is not None:
                temp = temp.next

            new_street = Node(street)
            temp.next = new_street

class Data:
    def __init__(self):
        self.bus_list = []

    def store_data(self):
        for i in range(len(bus_streets.bus_str)):
            new_bus = Bus(i+1, bus_url[i])
            new_reverse_bus = Bus(i+1, bus_reverse_url[i])
            for j in range(len(bus_streets.bus_str[i])):
                new_bus.append(bus_streets.bus_str[i][j])
                new_reverse_bus.append(bus_streets.bus_str[i][len(bus_streets.bus_str[i]) - (j + 1)])
            self.bus_list.append(new_bus)
            self.bus_list.append(new_reverse_bus)

        return self.bus_list

class Plot(Data):
    __API_KEY = 'AIzaSyAPjFl1yYCGsN0iSOJiVSWxNj1vnSjRq_M'
    __colors = ['red', 'blue', 'green', 'yellow', 'black', 'red', 'blue', 'green', 'yellow', 'black']

    def __init__(self, origin, destination):
        super().__init__()
        self.origin = origin
        self.destination = destination
        self.data = self.store_data()

    def find_bus(self):
        bus_dict = {}

        for bus in self.data:
            temp = bus._Bus__head
            count = 0
            while temp is not None:
                if temp is not None and temp.data == self.origin:
                    while temp is not None and temp.data != self.destination:
                        temp = temp.next
                        count += 1
                    if temp == None:
                        break
                    else:
                        bus_dict[bus] = count
                        break
                temp = temp.next

        if len(bus_dict) == 0:
            return False

        minimum_distance = min(bus_dict.items(), key=lambda x: x[1])[1]

        return [i for i in bus_dict if bus_dict[i] == minimum_distance]

    def route_url(self, bus_url):
        url = urlopen(bus_url.format(self.__API_KEY))
        route_url_data = json.load(url)
        return route_url_data

    def get_locations(self, route_url_data):
        start_location = []
        locations = []

        for i in range(len(route_url_data['routes'][0]['waypoint_order']) + 1):
            for element in route_url_data['routes'][0]['legs'][i]['steps']:
                start_location.append([element['start_location']['lat'], element['start_location']['lng'], '|'])
                start_location.append([element['end_location']['lat'], element['end_location']['lng'], '|'])
        for i in start_location[1::2]:
            locations.append(str(i[0]) + ',' + str(i[1]) + str(i[2]))

        return locations

    def get_road_data(self, locations):
        url = ('https://roads.googleapis.com/v1/snapToRoads?path={}&interpolate=true&key={}'.format(''.join(locations), self.__API_KEY))
        url = url.rsplit('|', 1)
        url = ''.join(url)
        url = urlopen(url)

        url_data = json.load(url)

        roads = []
        for elem in url_data['snappedPoints']:
            roads.append((elem['location']['latitude'], elem['location']['longitude']))
        return roads

    def plot(self):
        gmap = gmplot.GoogleMapPlotter(40.177574, 44.512579, 13)
        buses = self.find_bus()
        bus_numbers = []
        roads = []

        for bus in buses:
            route_url_data = self.route_url(bus._Bus__url)
            locations = self.get_locations(route_url_data)
            roads.append(self.get_road_data(locations))
            bus_numbers.append(str(bus._Bus__number))

        for i in range(len(buses)):
            place_lats, place_lons = zip(*roads[i])
            gmap.plot(place_lats, place_lons, self.__colors[i], edge_width=10)
        gmap.draw("my_map.html")

        return bus_numbers

def main():
    print ("<-<-<-<-< Welcome to TranspoRoute >->->->->")
    origin = input("Input your origin point: ").title()
    destination = input("Input your destination point: ").title()

    my_route = Plot(origin, destination)
    while not my_route.find_bus():
        print("Please try again! ")
        origin = input("Input your origin point: ").title()
        destination = input("Input your destination point: ").title()
        my_route = Plot(origin, destination)

    bus_numbers = my_route.plot()
    print("You can use bus/buses number " + ', '.join(bus_numbers) + " to get from " + origin + " to " + destination)
    print("Have a nice trip!")

main()


