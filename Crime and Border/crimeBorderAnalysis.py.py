#Authors: Cesar Guerrero, Dan Sokol, Pengchao Wang
from numpy import corrcoef
from math import radians, sin, cos, acos
from bs4 import BeautifulSoup
import pickle
import urllib.request
import os
import csv
import cProfile
import sys

def main():
    #deletes the cityData.csv to avoid adding duplicates to the csv file
    deleteCityData()

    #website with all the links
    rawUrl = "https://en.wikipedia.org/wiki/List_of_United_States_cities_by_crime_rate"
    wikiSite = BeautifulSoup(urllib.request.urlopen(rawUrl), "html5lib")

    #narrowing down to the table rows
    tableData = wikiSite.find('table',{'class':'wikitable sortable'})
    tableBody = tableData.find('tbody')
    tableRows = tableBody.find_all('tr')

    #data for correlation calculation
    allCrimeRates = []
    allDistances = []

    #skips the header information and reads all the data inside the table
    for i in range(3, 103):
        #this is the individual row
        cells = tableRows[i].find_all('td')

        #if crime rate is blank skip row
        if(not cells[3].text == ""):

            #city name and crime rate here for CSV
            cityName = removeDigitsAndSymbols(cells[1].text) #some city names have numbers, dashses, periods appended
            cityCrimeRate = cells[3].text

            print("EXTRACTING DATA: "+cityName)

            #use this url to go get the Longitude and Latitude
            cityUrl = "https://en.wikipedia.org" + cells[1].a.get('href')
            coordinates = getCoordinates(cityName, cityUrl)

            #calculating smallest distance for city
            smallestDistance = calculateDistanceToBorder(coordinates[0], coordinates[1])

            #saving all the values in array for correlation calculation
            allCrimeRates.append(float(cityCrimeRate))
            allDistances.append(smallestDistance)

            #save all extracted values to CSV to do Final distance calculations and make final CSV
            saveCityDataToCSV(cityName, cityCrimeRate, smallestDistance)

    #Coefficient(distance, crime rate)
    res = corrcoef(allDistances, allCrimeRates)[0,1]

    print("DONE")
    print(f"Correlation Coefficient is {res}")

def getCoordinates(cityName, url):
    #check to see if the data document exist
    fileName = "data/" + cityName + ".p"

    if(fileExists(fileName)):
        #get the coordinates from html file
        with open(fileName,'rb') as data:
            htmlData = pickle.load(data)
        html = BeautifulSoup(htmlData, "html5lib")
    else:
        #get the coordinates from url
        saveHTML(cityName, url) #save HTML for next time
        html = BeautifulSoup(urllib.request.urlopen(url), "html5lib")

    return extractCoordinates(html)

def extractCoordinates(html):
    latitude = html.find('span',{'class':'latitude'}).text
    longitude = html.find('span',{'class':'longitude'}).text
    coordinates = [convertCoordinateToDecimal(latitude), convertCoordinateToDecimal(longitude)];
    return coordinates;

def convertCoordinateToDecimal(coordinate):
    #this determines where to split the string by
    p1 = coordinate.find("°")
    p2 = coordinate.find("′")
    p3 = len(coordinate) - 2;

    #this gets the coordniates from the string
    front = int(float(coordinate[0:p1]))
    middle = int(float(coordinate[(p1+1):p2]))

    #this tests if the coordinates had a seconds to convert from DMS
    try:
        end = int(float(coordinate[(p2+1):p3]))
    except Exception as e:
        end = 0;

    #this grabs the direction
    direction = coordinate[-1];

    #calculate decimal
    num = front + (middle/60) + (end/3600)

    #if the direction is s or w, make num negative
    if(direction == "S" or direction == "W"):
        num = -num;

    return num

def calculateDistanceToBorder(latitude, longitude):
    latitude = radians(latitude)
    longitude = radians(longitude)

    #[latitude, longitude]: San Ysidro, Yuma, Tucson, El Paso, Laredo, Del Rio, and Brownsville
    borderCities = [[32.5549, -117.044306],[32.692222, -114.615278],[32.221667, -110.926389],[31.759167, -106.488611],[27.524445, -99.490593],[29.364, -100.9],[25.930278, -97.484444]]
    borderDistances = set();

    for borderLatitude, borderLongitude in borderCities:
        #convert from degress to to to Radians
        borderLatitude = radians(borderLatitude)
        borderLongitude = radians(borderLongitude)

        #this will get this distance in miles.
        dist = (1/1.609344) * (6371.01 * acos(sin(latitude)*sin(borderLatitude) + cos(latitude)*cos(borderLatitude)*cos(longitude - borderLongitude)))
        borderDistances.add(dist)

    return min(borderDistances);

def saveHTML(cityName, url):
    fileName = "data/"+ cityName +".p"
    try:
        page = urllib.request.urlopen(url).read()
        html = page.decode()
    except:
        print("Could not save html")

    with open(fileName, 'wb') as cache:
        pickle.dump(html, cache)

def fileExists(file):
    if(os.path.isdir('data/')):
        return os.path.exists(file)
    else:
        os.mkdir('data/')
        return False

def removeDigitsAndSymbols(cityName):
    res = ''.join([i for i in cityName if i.isalpha() or i.isspace() or i == "-" or i == "."])
    return res

def saveCityDataToCSV(name, crimeRate, distance):
    with open('citydata.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([name, crimeRate, distance])

def deleteCityData():
    file = "citydata.csv"
    if(fileExists(file)):
        os.remove(file)

main()
