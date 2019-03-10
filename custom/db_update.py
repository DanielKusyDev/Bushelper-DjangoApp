from urllib.request import urlopen

from django.contrib.staticfiles.templatetags.staticfiles import static

from apps.bushelper.custom.email_management import send_email
from apps.bushelper.custom.scrapers import FremiksScraper, MpkScraper, MpkSoup
from apps.bushelper.models import Line, Carrier, BusStop, Course, Direction
from django.db import connection
import json


def refresh_all_id():
    table = 'bushelper_course'
    with connection.cursor() as cursor:
        cursor.execute("UPDATE sqlite_sequence SET seq=0 WHERE name LIKE %s", [table])


def get_fremiks_schedules():
    fremiks_lines = Line.objects.filter(url__contains='fremiks')
    carrier = Carrier.objects.get(name__iexact='fremiks')
    schedules = {}
    for line in fremiks_lines:
        schedules[line] = {}
        f_scrapper = FremiksScraper(line.url)
        single_schedule = f_scrapper.get_schedule()
        direction = f_scrapper.direction
        schedules[line][direction] = single_schedule
    return carrier, schedules


def get_mpk_schedules():
    mpk_lines = Line.objects.filter(url__contains='mpk')
    carrier = Carrier.objects.get(name__icontains='mpk')
    schedules = {}
    for line in mpk_lines:
        mpk_soup = MpkSoup(line.url)
        schedules[line] = {}
        email_sent = False
        for url in mpk_soup.urls():
            m_scraper = MpkScraper(url)
            try:
                single_stop_schedule = m_scraper.get_schedule()
                direction = m_scraper.direction
                try:
                    schedules[line][direction][m_scraper.bus_stop] = single_stop_schedule
                except KeyError:
                    schedules[line][direction] = {}
                    schedules[line][direction][m_scraper.bus_stop] = single_stop_schedule
            except BusStop.DoesNotExist:
                if email_sent:
                    continue
                email_sent = True
                request = urlopen(static('json/emails.json'))
                email_json = json.loads(request.read())['bus_stops_changed']
                email_context = {}
                email_context['subject'] = email_json['subject']
                email_context['body'] = email_json['body'] + '<br>' + str(line) + "<br><br>" + email_json['footer']
                send_email(receiver='daniel.kusy97@gmail.com', context=email_context)
                # todo erase harcoded email address. Firstly send emails to all superusers, but later create user subapp and set to moderators

    return carrier, schedules

if __name__ == '__main__':
    refresh_all_id()
    schedules = {}
    carrier, schedule = get_fremiks_schedules()
    schedules[carrier] = schedule
    carrier, schedule = get_mpk_schedules()
    schedules[carrier] = schedule
    # todo lbn-lsw courses does not appear if you want to take bus from lsw to lsw
    Course.objects.all().delete()
    i = 0
    for carrier in schedules:
        for line in schedules[carrier]:
            for direction in schedules[carrier][line]:
                for bus_stop in schedules[carrier][line][direction]:
                    for c_type in schedules[carrier][line][direction][bus_stop]:
                        for departure in schedules[carrier][line][direction][bus_stop][c_type]:
                            i = i+1
                            course = Course(course_type=c_type,
                                            bus_stop=bus_stop,
                                            carrier=carrier,
                                            direction=Direction.objects.get(direction__iexact=direction),
                                            line=line,
                                            departure=departure)
                            course.save()