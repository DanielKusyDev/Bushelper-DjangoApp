import re
import numpy as np
import pandas as pd
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup as bs
import django

django.setup()
from bushelper.models import *
from bushelper.utils import replace_types_gen

from bushelper.python_scripts import db_operations as db


def update_departures(hours):
    curr_hours = Departure.objects.all()
    temp_set = set()
    for h in curr_hours:
        h = h.hour.strftime('%H:%M')
        temp_set.add(h)
    hours = hours.difference(temp_set)
    for h in hours:
        Departure(hour=h).save()


def fremiks(url):
    """Get data from Fremiks website"""
    df_fremiks = pd.read_html(url)
    fremiks_html = df_fremiks[0]
    df_fremiks = np.array(df_fremiks[0])
    direction = 'lbn' if 'Świdnik' in df_fremiks[1, 0] else 'lsw'
    hours = set()
    departures, course_types = df_fremiks[1:, 1:], df_fremiks[0, 1:]
    departures = [[hour.replace(';', ':') for hour in time] for time in departures]
    stops = df_fremiks[1:, 0]
    carrier = Carrier.objects.get(name='Fremiks')
    if not carrier:
        Carrier(name='Fremiks').save()
        carrier = Carrier.objects.get(name='Fremiks')
    for row in departures:
        for col in row:
            hours.add(col.zfill(5))
    update_departures(hours)
    update_fremiks_courses(departures, course_types, stops, direction, carrier)


def update_fremiks_courses(departures, types, stops, direction, carrier):
    def alias_gen(name, stop):
        for word in name:
            if word in stop:
                yield True
            yield False

    df_stops = [stop.strip('Świdnik').strip('Lublin').lstrip().strip('ul.').lstrip() for stop in stops]
    direction = Direction.objects.filter(direction=direction)[0]
    db_stops = BusStop.objects.filter(direction=direction)
    print(direction)
    for db_stop in db_stops:
        for departure, df_stop in zip(departures, df_stops):  # Pilnować, żeby alias zawierał sie w df_stop
            if db_stop.fremiks_alias is not None:
                length = len(db_stop.fremiks_alias.lower().split())
                if length > 1:
                    alias = db_stop.fremiks_alias.lower().split()
                    alias = [state for state in alias_gen(alias, df_stop.lower())]
                    # If there is more than one word in the name, split it to list and check if all of these words match
                    if alias.count(True) == length:
                        # print(db_stop)
                        for i, hour in enumerate(departure):
                            c_type = "".join(types[i].split())
                            curr_dep = Departure.objects.filter(hour=hour)[0]
                            # print("%s\n%s\n%s\n%s" % (c_type, db_stop, carrier, curr_dep))
                            # print('')
                            Course(course_type=c_type,
                                   direction=direction,
                                   bus_stop=db_stop,
                                   carrier=carrier,
                                   departure=curr_dep).save()
                elif db_stop.fremiks_alias.lower() in df_stop.lower():
                    # print(db_stop)
                    for i, hour in enumerate(departure):
                        c_type = "".join(types[i].split())
                        curr_dep = Departure.objects.filter(hour=hour)[0]
                        # print("%s\n%s\n%s\n%s" % (c_type, db_stop, carrier, curr_dep))
                        # print('')
                        Course(course_type=c_type,
                               direction=direction,
                               bus_stop=db_stop,
                               carrier=carrier,
                               departure=curr_dep).save()


def mpk():
    """Get all ZTM Lublin bus stops that are connected with Świdnik-Lublin lines."""
    main_url = 'http://mpk.lublin.pl/index.php'
    lines = Line.objects.all()
    all_departures = []
    all_departures_set = set()
    all_directions = []
    all_line_numbers = []
    all_course_types = []
    all_bus_stops = []
    for line in lines:

        response = urlopen(line.url)
        soup = bs(response, 'html.parser')
        section = soup.find_all('a', href=re.compile('.przy.*lin.'))
        print(section)
        for stop_url in section:
            stop_url = stop_url.get()
            stop_url = main_url + stop_url.strip('./')
            print(stop_url)
            stop_departures, direction, course_types, bus_stop = get_mpk_data(stop_url, line.name)
            lines_id = {
                '055': 1,
                '0N2': 2,
                '035': 3,
                '005': 4
            }
            line_number = lines_id.get(line.name, ValueError)
            all_line_numbers.append(line_number)
            all_course_types.append(course_types)
            all_bus_stops.append(bus_stop)
            for hour in stop_departures:
                all_departures_set = all_departures_set.union(set(hour))
            all_departures.append(stop_departures)
            all_directions.append(direction)

    update_departures(all_departures_set)
    update_mpk_courses(all_departures, all_directions, all_line_numbers, all_course_types, all_bus_stops)


def get_mpk_data(url, line):
    """Get all departure times from ZTM Lublin"""
    request = Request(url)
    response = urlopen(request)
    soup = bs(response, 'html.parser')
    bus_stop = soup.find('div', {'class': 'rozklad-przystanek'})
    bus_stop = bus_stop.find('a').get_text()
    bus_stop = re.sub('^[0-9]* - ', '', bus_stop).lower()
    if line == '035':
        direction_keywords = {'lsw': ('Świdnik', 'Mełgiew'), 'lbn': ('Choiny', 'Gęsia', 'Brama', 'Felin')}
    else:
        direction_keywords = {'lsw': ('Świdnik', 'Mełgiew', 'Felin'), 'lbn': ('Choiny', 'Gęsia', 'Brama')}
    direction = str(soup.find('div', {'class': 'rozklad-kierunek'}))
    for key in direction_keywords:
        for value in direction_keywords[key]:
            if value in direction:
                direction = key
                break
    hours_soup = soup.find_all('td')
    minutes = list()
    response = pd.read_html(url)
    response = [np.array(tag) for tag in response]
    response = np.array(response)
    hours = response[0, 0, 1:]
    hours = [int(h) for h in hours]
    course_types = soup.find_all('span', {'class': 'rozklad-title'})
    course_types = [c.findAll(text=True) for c in course_types]
    course_types = np.array(course_types)
    course_types = np.squeeze(course_types)
    tables_num = len(response)
    last_min_pos = int(len(hours_soup) / 3) - 1
    counter = 0
    for plate in hours_soup[1:]:
        element = re.findall(r'[0-9]+', str(plate))
        length = len(element)
        if length == 0:
            if counter == last_min_pos:
                counter = 0
            else:
                minutes.append(-1)
                counter += 1
        elif length >= 2:
            element = [int(i) for i in element]
            minutes.append(element)
            counter += 1
        else:
            counter += 1
            minutes.append(int(element[0]))
    try:
        minutes = np.resize(minutes, (tables_num, int(len(minutes) / tables_num)))
    except ValueError:
        minutes[0] = [minutes[0]]
        minutes = np.resize(minutes, (tables_num, int(len(minutes) / tables_num)))
    hours_list = []
    for row in minutes:
        temp_hours_list = []
        for hour, minute in zip(hours, row):

            if minute != -1:
                if isinstance(minute, list):
                    for m in minute:
                        record = '%02d:%02d' % (hour, m)
                        temp_hours_list.append(record)
                else:
                    record = '%02d:%02d' % (hour, minute)
                    temp_hours_list.append(record)
            else:
                continue
        hours_list.append(np.array(temp_hours_list))
    hours_list = np.array(hours_list)

    try:
        course_types = np.array([type for type in replace_types_gen(course_types)])
    except TypeError:
        course_types = np.array([type for type in replace_types_gen([course_types])])

    return hours_list, direction, course_types, bus_stop


def update_mpk_courses(all_departures, all_directions, all_line_numbers, all_course_types, all_bus_stops):
    carrier = Carrier.objects.get(name='MPK')
    for departure, direction, line, type, bus_stop in zip(all_departures, all_directions, all_line_numbers,
                                                          all_course_types, all_bus_stops):
        direction = Direction.objects.filter(direction=direction).first()
        curr_bus_stops = BusStop.objects.filter(direction=direction)
        if 'nż' in bus_stop:
            bus_stop = bus_stop.replace(' nż', '')
        for curr_bus_stop in curr_bus_stops:
            street_name = curr_bus_stop.mpk_street.lower()
            if street_name == bus_stop or street_name in bus_stop:
                proper_stop = curr_bus_stop
                print(proper_stop)
                for course_type, row in zip(type, departure):
                    for record in row:
                        proper_departure = Departure.objects.filter(hour=record)[0]
                        Course(course_type=course_type,
                               direction=direction,
                               bus_stop=proper_stop,
                               line_id=line,
                               carrier=carrier,
                               departure=proper_departure).save()


if __name__ == "__main__":
    db.reset_sequence("Course")
    Course.objects.all().delete()
    db.reset_sequence("Departure")
    Departure.objects.all().delete()
    fremiks('http://www.fremiks.pl/index.php/rozklad-jazdy/swidnik-witosa-lublin')
    fremiks('http://www.fremiks.pl/index.php/rozklad-jazdy/lublin-witosa-swidnik')
    mpk()
    # get_mpk_data("http://mpk.lublin.pl/?przy=5582&lin=0N2", "0N2")
# TODO są jakieś duble w nocnych
# TODO ogarnąć te godziny w bazie
