import re

import django
django.setup()
import pandas as pd
import numpy as np
from apps.bushelper import BusStop, Direction
from urllib.request import urlopen
from urllib.parse import *
from bs4 import BeautifulSoup as bs


def erase_direction_name(bus_stop):
    tmp_stop = bus_stop.lower()
    lsw = "świdnik"
    lbn = "lublin"
    if 'ul.' in tmp_stop:
        bus_stop = bus_stop.split('ul.')
    elif lsw in bus_stop:
        bus_stop = bus_stop.split(lsw)
    else:
        bus_stop = bus_stop.split(lbn)

    return bus_stop[-1].strip()


def get_direction(direction):
    """Accepts lowercase string"""
    if "świdnik" in direction:
        result = 'lbn'
    else:
        result = 'lsw'
    return result


def bus_stop_match(bus_stop):
    tmp_stop = bus_stop.lower()

    def _filter(queryset_object):
        alias = queryset_object.fremiks_alias.lower()
        if alias in tmp_stop:
            return queryset_object
    return _filter


class MpkSoup(object):

    def __init__(self, url):
        response = urlopen(url)
        self.soup = bs(response, 'html.parser')
        pattern = urlparse(url)
        self.pattern = pattern.scheme + '://' + pattern.netloc + '/?'
        self.url_section = self.soup.find_all('a', href=re.compile('.przy.*lin.'))

    def urls(self):
        """ Returns (url, bus_stop_name) """

        for a in self.url_section:
            url = a.get('href')
            url = self.pattern + urlparse(url).query
            yield url


def proper_course_types(types):
    for t in types:
        c_type = str(t).lower()
        if 'powszedni' in c_type:
            yield 'D'
        elif 'sobot' in c_type:
            yield 'E'
        elif 'niedz' in c_type or 'świąt' in c_type:
            yield 'E7'
        elif 'nocn' in c_type:
            yield 'DE7'
        else:
            yield t


class Scraper(object):
    def __init__(self, url=None):
        self.url = url
        self.direction = None
        self.bus_stop = None

    def arrange_data(self, *args):
        pass

    def get_table(self):
        table = pd.read_html(self.url)
        return table

    def get_soup(self):
        soup = bs(urlopen(self.url), 'html.parser')
        return soup

    def get_schedule(self):
        """Only outer list is regular, python list. Others are numpy_arraylists.
            {Bus Stop:
                [
                    {CourseType: [departures]}
                ]
            }"""
        pass


class FremiksScraper(Scraper):
    """ Scraps schedule from fremiks """

    def get_schedule(self):
        tables = self.get_table()
        data_arr = self.arrange_data(tables[0])
        return data_arr

    def arrange_data(self, table):
        data_frame = np.array(table)
        for tmp in data_frame[:, 0]:
            tmp = tmp.lower()
            if 'świdnik' in tmp or 'lublin' in tmp:
                self.direction = get_direction(tmp)
                break

        dep_dict = {}
        course_types = [c_type.replace(u'\xa0', u' ') for c_type in data_frame[0][1:]]

        queryset = BusStop.objects.filter(direction__direction__iexact=self.direction, fremiks_alias__isnull=False)
        for row in data_frame[1:]:
            stop_name = row[0].replace(u'\xa0', u' ')
            stop_name = erase_direction_name(stop_name)
            match_filter = bus_stop_match(stop_name)
            bus_stop = filter(match_filter, queryset).__next__()
            c_types_dict = {}
            for c in course_types:
                c_types_dict[c] = []
            dep_dict[bus_stop] = c_types_dict

            for hour, c_type in zip(row[1:], course_types):
                hour = hour.replace(';', ':')
                c_types_dict[c_type].append(hour)
            dep_dict[bus_stop] = c_types_dict
            self.bus_stop = bus_stop
        return dep_dict


class MpkScraper(Scraper):

    DIRECTIONS = {
        'lbn': ('Choiny', 'Gęsia', 'Brama', 'Felin'),
        'lsw': ('Świdnik', 'Mełgiew', 'Felin')
    }

    def get_schedule(self):
        tables = self.get_table()
        soup = self.get_soup()
        self.set_direction(soup)
        self.set_bus_stop(soup)

        course_types = soup.find_all('span', {'class': 'rozklad-title'})
        course_types = [t.get_text() for t in course_types]
        course_types = [t for t in proper_course_types(course_types)]
        schedule = {}
        for single_table, c_type in zip(tables, course_types):
            departures = self.arrange_data(single_table)
            schedule[c_type] = departures
        return schedule

    def arrange_data(self, table):
        table = np.array(table)
        departures = []
        shitty_mpk_programmer_condition = re.compile(r'\..')
        for hour, minutes in zip(table[0, 1:], table[1, 1:]):
            if shitty_mpk_programmer_condition.search(str(hour)):
                continue
            minutes = str(minutes)
            hour = str(hour)
            if self.direction.direction == 'lbn':
                if len(minutes) % 2 != 0:
                    minutes = '0' + minutes
                minutes = re.sub(r'[a-z]', '', minutes)
                minutes = re.findall(r'..?', minutes)
                for minute in minutes:
                    departures.append(str(hour + ':' + minute))
            else:
                for pos in re.finditer(r'[b-z]', minutes):
                    pos = pos.start()
                    minute = minutes[:pos][-2:]
                    departures.append(str(hour + ':' + minute))
        return departures

    def set_bus_stop(self, soup):
        url_query = urlparse(self.url).query
        url_query = url_query.split('&')[0]
        bus_stop = soup.find('a', href='../../?' + url_query).get_text()
        bus_stop = bus_stop.split(' - ')[-1]
        self.bus_stop = BusStop.objects.get(mpk_street__iexact=bus_stop, direction=self.direction)

    def set_direction(self, soup):
        direction = soup.find('div', {'class': 'rozklad-kierunek'}).get_text()
        direction = direction.split('Kierunek:')[-1].strip()
        for k in self.DIRECTIONS:
            for street in self.DIRECTIONS[k]:
                if street in direction:
                    self.direction = Direction.objects.get(direction__iexact=k)
                    break