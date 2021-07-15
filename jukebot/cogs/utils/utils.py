import json
import logging
from pprint import pprint


def get_time_string(seconds):
    hours = seconds / 3600
    minutes = (seconds / 60) % 60
    seconds = seconds % 60
    return '%0.2d:%02d:%02d' % (hours, minutes, seconds)


def fileIO(filename, IO, data=None):
    if IO == 'load' and data == None:
        with open(filename, encoding='utf-8', mode="r") as f:
            return json.loads(f.read())


def json_io_load(filename):
    """ Gets the JSON data and returns it as a dictionary from filename

    :arg filename <string> - Filename of json to point to
    """
    with open(filename, encoding='utf-8', mode='r') as json_file:
        return json.loads(json_file.read())


def json_io_dump(filename, data):
    """ Dumps the the JSON data and returns it as a dictionary from filename

    :arg filename <string> - Filename of json to point to
    :arg data - The already formatted data to dump to JSON
    """
    with open(filename, encoding='utf-8', mode='w') as json_file:
        json.dump(data, json_file)
        return True


def day_to_num(day):
    weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    try:
        return weekdays.index(day.lower())
    except ValueError:
        return None

