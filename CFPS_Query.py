import argparse
import csv
import requests
import json
from datetime import datetime

def main():
    """ Main method for querying the CFPS site to get information on an Aerodrome or FIR.

    The program should support a query against any of the 7 FIR regions or a specific Aerodrome identifier. When
    executing, parameters are as follows: CFPS_Query.py <Location Code> <Query Type> i.e. CFPS_Query.py CYKF
    UpperWind CFPS_Query.py CYYZ PIREP

    Each query type should have its own function to grab and parse the data.
    """

    # TO DO : Determine the best way to handle additional parameters for options, such as:
    #           - Upper winds (high, low or both?)
    #           - METAR (current or future data?)

    # TO DO : Is there a need to get a range around a specific aerodrome? Doesn't apply to the FIR, does it make most
    # sense to just get the JSON for the FIR and parse it for relevant info?

    parser = argparse.ArgumentParser(description='CFPS parser for specific location and report type')

    # Add positional arguments
    parser.add_argument('location', help='Location code (Aerodrome or FIR)')
    parser.add_argument('data', help='Type of data to retrieve (upperwind, taf, metar, pirep, etc)')

    # Parse the command-line arguments
    args = parser.parse_args()

    # Access the values of the arguments
    location_code = args.location
    data_type = args.data.lower()
    cfps_query_url = craftUrl(location_code, data_type)

    function_mapping = {
        "sigmet": parse_sigmets,
        "airmet": parse_airmets,
        "notam": parse_notams,
        "metar": parse_metar,
        "taf": parse_taf,
        "pirep": parse_pireps,
        "upperwind": parse_upper_winds,
    }

    # Your program logic goes here
    print(f'Location: {location_code}')
    print(f'Type of data : {data_type}')

    if data_type in function_mapping:
        function_mapping[data_type](cfps_query_url)
    else:
        print(f'{data_type} is not currently supported as an option for querying')


def craftUrl(location_code, data_type):
    # First determine if the location is one of the 7 FIRs or is a specific Aerodrome
    # While a specific aerodrome can be queried with the 'fir' tag, the FIRs cannot be queried with the 'site' tag

    # Base URL for every CFPS search
    base_cfps_url = "https://plan.navcanada.ca/weather/api/alpha/?"

    # Valid Canadian FIR codes
    valid_fir_regions = ["CZEG", "CZQM", "CZQX", "CZUL", "CZVR", "CZWG", "CZYZ"]

    # There may be a need to add additional location codes in the future for things like weather stations,
    # so not defaulting to SITE or FIR at this point
    if location_code in valid_fir_regions:
        location_type = "FIR"
        query_type = "polygon"
        location_cords = '00.000,00.000'
    else:
        location_type = "site"
        query_type = "point"
        location_cords = aerodrome_location_lookup(location_code)

    return (base_cfps_url + query_type + "=" + location_code + "|" + location_type + "|-" + location_cords + "&alpha=" +
            data_type)


def aerodrome_location_lookup(location_code):
    # CFPS uses the decimal degrees format for its site location coordinates and not DMS. The Ontario GeoHub does
    # provide a dataset containing all Ontario airports. CFPS expects the data in long,lat format with only 3 decimal
    # points. URL used to retrieve a CSV of Ontario aerodromes:
    # https://geohub.lio.gov.on.ca/datasets/f03edc813b4542bdad0f1bbaa58b70b6/explore

    # TO DO : Determine how to get aerodrome info for regions outside of Ontario TO DO : Determine if the lat/long
    # positions are important for FIRs. Because there are only 7, can likely be stored in an array alongside the FIR
    # codes
    # TO DO : Figure out how to consolidate issues with the DMS co-ords not matching what the CFPS is expecting. They
    # can be off by 1 from what CFPS expects, anything more than that seems to return an empty data set. See CYVV as
    # an example

    aerodrome_location_file = 'assets/ontario_official_airports.csv'

    with open(aerodrome_location_file, 'r') as file:
        reader = csv.DictReader(file)

        for row in reader:
            if row['AIRPORT_IDENT'] == location_code:
                # return row.get('LONGITUDE') + "," + row.get('LATITUDE')
                return ("{:.3f}".format(float(row.get('LONGITUDE'))) +
                        ',' +
                        "{:.3f}".format(float(row.get('LATITUDE'))))


def parse_sigmets(cfps_query_url):
    print("Process SIGMETS")


def parse_airmets(cfps_query_url):
    print("Process AIRMETS")


def parse_notams(cfps_query_url):
    print("Process NOTAMS")


def parse_metar(cfps_query_url):
    print("Process METAR")


def parse_taf(cfps_query_url):
    print(f"Process TAF")


def parse_pireps(cfps_query_url):
    print(f"Process PIREPS")


def parse_upper_winds(cfps_query_url):
    """ Format of the winds aloft data appears as follows (Specifically the Data -> Text element). All times in the
        data are listed in UTC.
        - Report Type       : FBCN31/33/35 messages. Code is based on valid time (31
        - Issuer            : CCMEP issues 3000-18000ft levels (CWAO). US NWS issues high level data (KWNO)
        - Approx Issue Time : Normally available earlier. (15:20,15:30,15:30 for CWAO, for KWNO generally its the
                                actual issue time)
        - Data Based On     : The time the data for the forecast was based on
        - Valid At          : When this data is valid at
        - For Use Starting  : The starting time that data is valid for
        - For Use Ending    : The end time for that data
        - 4 Values          : These values are listed as null. Have not been able to reverse what these fields
                                represent yet, but they have always appeared null thus far.
        - Winds aloft data  : Values for winds aloft at various values. Broken down further below.

        Winds Aloft Data
            The winds aloft data includes all values for various heights. The format of the array is as follows:
                -  Level : Height (ASL). For low level CWAO messages, this includes the following levels (feet ASL):
                            3000, 6000, 9000, 12000, 18000
                        For high level KWNO messages, this would include (feel ASL):
                            24000, 30000, 34000, 39000, 45000, 53000
                - Wind direction (heading)
                - Wind speed (knots)
                - Temperature (degrees Celsius).

        Note that unlike the old AWWS system, the CFPS can report winds greater than 100 knots without needing to
        add to the direction. In additional, for heights above 24000 feet (KNWO data) the negative sign is included.
        This was not the case with AWWS data.

    """

    # TO DO : Is FBCN31 always valid at 1800Z or do those codes rotate based on current time?

    # TO DO : Try to confirm why temp does not always show up? Example below where the temp at 3000ft is returned as
    # null. Is it not available?
    # ["FBCN35", "CWAO", "2023-11-10T15:30:00+00:00", "2023-11-10T12:00:00+00:00",
    # "2023-11-11T12:00:00+00:00", "2023-11-11T06:00:00+00:00", "2023-11-11T18:00:00+00:00", null, null, null, null,
    # [[18000,280,37,-24,0],[3000,310,17,null,0],[6000,330,11,-7,0],[9000,300,20,-10,0],[12000,300,21,-14,0]]]

    # TO DO : Do positive temps show up with a + or just as an int? Only have negative temps currently, need to confirm
    #           what positive temps look like when available.

    cfps_query_url += "&upperwind_choice=both"

    print(f"{cfps_query_url}")
    response = requests.get(cfps_query_url)
    json_data = response.json()

    if json_data.get("data") and len(json_data["data"]) > 0:
        for element in json_data["data"]:

            print (element.get("location") + "  " +
                   json.loads(element.get("text"))[1] + "  " +
                   "Issued at: " + datetime.fromisoformat(json.loads(element.get("text"))[3]).strftime("%Y-%m-%d %H:%M:%S %Z") + "  " +
                   "Valid from : " + datetime.fromisoformat(json.loads(element.get("text"))[4]).strftime("%Y-%m-%d %H:%M:%S %Z"))
            print("For use starting : " + datetime.fromisoformat(json.loads(element.get("text"))[5]).strftime("%Y-%m-%d %H:%M:%S %Z") + "  " +
                   "Ending " + datetime.fromisoformat(json.loads(element.get("text"))[6]).strftime("%Y-%m-%d %H:%M:%S %Z"))

            winds_aloft_values_array = json.loads(element.get("text"))[-1]
            winds_aloft_values_array_sorted = sorted(winds_aloft_values_array, key=lambda x: x[0])

            for winds_aloft_level_values in winds_aloft_values_array_sorted:
                level = str(winds_aloft_level_values[0])
                wind_direction = str(winds_aloft_level_values[1])
                wind_speed = str(winds_aloft_level_values[2])
                temperature = str(winds_aloft_level_values[3])

                print("   " + level + " feet AGL | Winds "
                      + wind_direction + "@" +
                      wind_speed + " | Temp " +
                      temperature)
            print("")
    else:
        print("No winds aloft data reported")


if __name__ == '__main__':
    main()
