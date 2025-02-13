import json
import logging
import os
from pprint import pprint
from urllib import error, request

from .. import utils

_module = 'World Tides API'


def fetch_tides(api_key: str, loc: list):
    request_url = f'https://www.worldtides.info/api/v3?extremes&localtime&datum=CD&lat={loc[0]}&lon={loc[1]}&key={api_key}'
    logging.info(request_url)

    try:
        response = request.urlopen(request_url)
        data = response.read()
    except error.HTTPError as e:
        data = e.read().decode('utf8')

    try:
        data = json.loads(data)
    except ValueError as e:
        # we got bad JSON from worldtides.info, probably a 500 ISE
        api_down = 'Our tide data source seems to be down at the moment, ' \
                 'please try again later.' + e.message
        return utils.error_builder(_module, 500, api_down)

    status = data['status']

    if status == 200:
        return data

    if status == 400:
        return utils.error_builder(module=_module, status=status, msg='Bad API Key')

    return utils.error_builder(module=_module, status=status, msg=data)


def fetch_stations(api_key):
    stations_url = 'https://www.worldtides.info/api?stations&key={key}'.format(
        options='stations',
        key=api_key,
    )
    logging.info(stations_url)
    response = request.urlopen(stations_url)
    data = response.read()

    try:
        data = json.loads(data)
    except ValueError as e:
        # we got bad JSON from worldtides.info, probably a 500 ISE
        return utils.error_builder(
            module=_module,
            status=500,
            msg='Our tides information source seems to be down at the moment, '
                'please try again later.' + e.message
        )

    try:
        return {
            'status': 'OK',
            'stations': data['stations']
        }
    except KeyError:
        return utils.error_builder(
            module=_module,
            status='Error: Bad JSON Data\n',
            msg=str(data)
        )


def main():
    from dotenv import load_dotenv
    load_dotenv()
    tides_api_key = os.environ['WORLDTIDES_INFO_API_KEY']

    req_loc = utils.test_location

    print('Testing WorldTides Location API:')
    tides_data = fetch_tides(tides_api_key, req_loc)
    print('Request completed.')
    if tides_data['status'] == 200:
        print('SUCCESS: Accepted API Key and returned results:')
        print(tides_data)
    else:
        print('FAILURE:')
        print(utils.error_dump(tides_data))

    # now break it on purpose
    print('')
    print('Testing WorldTides API error handling (bad API key):')

    tides_data = fetch_tides('foobar', req_loc)
    print('Request completed')
    if tides_data['status'] == 400:
        print('SUCCESS: Failed on bogus API Key:')
        print(tides_data)
    elif tides_data['status'] == 200:
        print('FAILURE: Accepted bogus API Key:')
        pprint(tides_data)
    else:
        print(f'FAILURE: Unexpected Response: {tides_data["status"]}')
        print(utils.error_dump(tides_data))
    print('')


    stations_filename = 'stations.json'
    print(f'Writing stations list to {stations_filename}')
    stations = fetch_stations(tides_api_key)
    with open(stations_filename, 'w') as outfile:
        outfile.write(json.dumps(stations, indent=4))


if __name__ == '__main__':
    main()
