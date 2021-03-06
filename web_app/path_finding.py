import os
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')
import csv
import pymongo
from itertools import combinations
from graph import Graph

client = pymongo.MongoClient("mongodb+srv://admin:admin@clusteria.tvj6u.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = client['iadb']
collection4 = db['graphSegments']
collection5 = db['stopCoords2']

cursor = collection5.find({})
fields = ['stop_name','stop_lat','stop_lon','commune']
stopCoords = pd.DataFrame(list(cursor), columns = fields)

def checkCity(city):
    city = city.lower()
    city = city.replace("-", " ")
    city = city.replace("saint", "st")
    stopCoords['commune'] = stopCoords['commune'].str.replace("-", " ")
    stopCoords['commune'] = stopCoords['commune'].str.lower()

    ar = stopCoords.loc[stopCoords['commune'] == city]['stop_name'].values
    if (len(ar) == 0):
        ar = stopCoords.loc[stopCoords['commune'].str.contains(city, case=False)]['stop_name'].values

    return ar


def dijsktra(graph, initial, end):
    # shortest paths is a dict of nodes
    # whose value is a tuple of (previous node, weight)
    shortest_paths = {initial: (None, 0)}
    current_node = initial
    visited = set()
    weight = 99999999

    while current_node != end:
        visited.add(current_node)
        destinations = graph.edges[current_node]
        weight_to_current_node = shortest_paths[current_node][1]

        for next_node in destinations:
            weight = graph.weights[(current_node, next_node)] + weight_to_current_node
            if next_node not in shortest_paths:
                shortest_paths[next_node] = (current_node, weight)
            else:
                current_shortest_weight = shortest_paths[next_node][1]
                if current_shortest_weight > weight:
                    shortest_paths[next_node] = (current_node, weight)
        
        next_destinations = {node: shortest_paths[node] for node in shortest_paths if node not in visited}
        if not next_destinations:
            return "Route Not Possible"
        # next node is the destination with the lowest weight
        current_node = min(next_destinations, key=lambda k: next_destinations[k][1])
    
    # Work back through destinations in shortest path
    path = []
    while current_node is not None:
        path.append(current_node)
        next_node = shortest_paths[current_node][0]
        current_node = next_node
    # Reverse path
    path = path[::-1]
    
    return (path, weight)


def formatResults(resList):
    stopCoords.head(10)
    path = []
    for res in resList:
        rowStation = stopCoords.loc[stopCoords['stop_name'].str.contains(res, case=False)]
        if (len(rowStation.values) > 0):
            rowStation =  rowStation.values[0]
            path.append({
                'city': rowStation[3],
                'station': rowStation[0],
                'lat': rowStation[1],
                'lng': rowStation[2]
            })
    return path


def process_path_finding(departure, arrival):
    theList = []
    for doc in collection4.find():
        d = (doc['from'], doc['to'], doc['time'])
        theList.append(d)

    departureList = checkCity(departure)
    arrivalList = checkCity(arrival)

    graph = Graph()
    for edge in theList:
        graph.add_edge(*edge)

    # Get all gares from departure city
    # get all gares from arrival city
    # calculate all combinations and keep the shortest
    resList = ""
    for dep in departureList:
        for arr in arrivalList:    
            ww = dijsktra(graph, dep, arr)
            if(len(resList)==0):
                resList = ww
            elif(resList[1]>ww[1]):
                resList = ww

    time = (resList[-1]/3600)
    timeInHours = "%dh%02d" % (int(time), (time*60) % 60)

    # Format results
    formattedList = formatResults(resList[0])

    ressultPath = (formattedList, "Dur??e du voyage : "+timeInHours)
    return ressultPath