import sys
import argparse
import csv


def main():
    """ Main method for querying the CFPS site to get information on an Aerodrome or FIR.

    The program should support a query against any of the 7 FIR regions or a specific Aerodrome identifier. When
    executing, parameters are as follows: CFPS_Query.py <Location Code> <Query Type> i.e. CFPS_Query.py CYKF
    WindsAloft CFPS_Query.py CYYZ PIREP

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
    parser.add_argument('data', help='Type of data to retrieve (upperwind, TAF, Metar, PIREP, etc)')

    # Parse the command-line arguments
    args = parser.parse_args()

    # Access the values of the arguments
    location_code = args.location
    data_type = args.data
    cfps_url = craftUrl(location_code, data_type)

    # Your program logic goes here
    print(f'Location: {location_code}')
    print(f'Type of data : {data_type}')
    print(f'URL : {cfps_url}')


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
    # points. URL used to retrieve a CSV of airports:
    # https://geohub.lio.gov.on.ca/datasets/f03edc813b4542bdad0f1bbaa58b70b6/explore

    # TO DO : Determine how to get aerodrome info for regions outside of Ontario TO DO : Determine if the lat/long
    # positions are important for FIRs. Because there are only 7, can likely be stored in an array alongside the FIR
    # codes
    # TO DO : Determine if the lat/long values are actually needed for FIRs and Aerodromes. They may only be
    # required if searching based on a radius around a specific aerodrome

    aerodrome_location_file = 'assets/ontario_official_airports.csv'

    with open(aerodrome_location_file, 'r') as file:
        reader = csv.DictReader(file)

        for row in reader:
            if row['AIRPORT_IDENT'] == location_code:
                print(row.get('LATITUDE') + "," + row.get('LONGITUDE'))
                return ("{:.3f}".format(float(row.get('LONGITUDE'))) +
                        ',' +
                        "{:.3f}".format(float(row.get('LATITUDE'))))


if __name__ == '__main__':
    main()
