#This needs to be tidied up if it going to be submitted
#Probably stick it in a container and run it on an ec2, might get some marks

from flask import Flask
from flask import request
from flask import Response
from flask import jsonify
import json

from math import radians, cos, sin, asin, sqrt
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

app = Flask(__name__)

class Bar:
    def __init__(self, lat, lng):
        self.lat = lat
        self.lng = lng

@app.route('/tsm', methods=['GET', 'POST'])
def tsm():
    
    #All the json input still needs to be filter
    req = request.get_json()
    print(req)

    bars = []
    
    for item in req:
        for data_item in item['bars']:
            print (data_item['lat'], data_item['lng'])
            lat = float(data_item['lat'])
            lng = float(data_item['lng'])
            tempbar = Bar(lat, lng)
            bars.append(tempbar)
    
    data = create_matrix(bars)

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                           data['num_vehicles'], data['depot'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if solution:
        return_list = print_solution(manager, routing, solution)
        return_json = json.dumps(return_list)
        return return_json, 200
    else:
        #Format into json
        return "Error", 400

    

def haversine(lng1, lat1, lng2, lat2):
    """
    Calculate the great circle distance in kilometers between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lng1, lat1, lng2, lat2 = map(radians, [lng1, lat1, lng2, lat2])

    # haversine formula 
    dlng = lng2 - lng1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth (km)
    return c*r


def create_matrix(bars):
    #b1 = Bar(54.59325364874902, -5.9285263607450505)
    #b2 = Bar(54.589271103918136,-5.934308594437078)
    #b3 = Bar(54.59209519204566,-5.932592293398167)
    #bars = []
    #bars.append(b1)
    #bars.append(b2)
    #bars.append(b3)
    
    distance_matrix = []
    for i in bars:
        new = []
        for j in bars:
            new.append(haversine(i.lng, i.lat, j.lng, j.lat))
            print(haversine(i.lng, i.lat, j.lng, j.lat ))
        distance_matrix.append(new)

    data = {}
    data['distance_matrix'] = distance_matrix
    data['num_vehicles'] = 1
    data['depot'] = 0 #The starting point
    return data



def print_solution(manager, routing, solution):
    """Prints solution on console."""
    print('Objective: {} miles'.format(solution.ObjectiveValue()))
    index = routing.Start(0)
    plan_output = 'Route for vehicle 0:\n'
    route_distance = 0
    route = []
    while not routing.IsEnd(index):
        route.append(index)
        plan_output += ' {} ->'.format(manager.IndexToNode(index))
        previous_index = index
        index = solution.Value(routing.NextVar(index))
        route_distance += routing.GetArcCostForVehicle(previous_index, index, 0)
    plan_output += ' {}\n'.format(manager.IndexToNode(index))
    #print(plan_output)
    print(route)
    return route


if __name__ == '__main__':
    app.run(host= '0.0.0.0',debug=True)


# curl --header "Content-Type: application/json" --request POST --data '[{"bars":[{"lng":"-5.9285263607450505","lat":"54.59325364874902"},{"lng":"-5.934308594437078","lat":"54.589271103918136"},{"lng":"-5.932592293398167","lat":"54.59209519204566"}]}]' http://127.0.0.1:5000/tsm
# Should return the list order as [0,2,1]