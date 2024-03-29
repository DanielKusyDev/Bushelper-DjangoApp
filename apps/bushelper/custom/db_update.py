from urllib.request import urlopen

from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core.checks import Error
from django.core.exceptions import ValidationError

from apps.bushelper.custom.email_management import send_email
from apps.bushelper.custom.scrapers import FremiksScraper, MpkScraper, MpkSoup
from apps.bushelper.models import Line, Carrier, BusStop, Course, Direction
from django.db import connection, transaction
import json


def refresh_all_id():
    table = 'bushelper_course'
    with connection.cursor() as cursor:
        cursor.execute("UPDATE sqlite_sequence SET seq=0 WHERE name LIKE %s", [table])


def update_fremiks_graph(table, direction):
    src, dst = None, None
    print('--- Creating Fremiks graph ---')
    for scrapped_bus_stop in table[0][0][1:]:
        if src is not None and dst is not None:
            print('%s -> %s' % (src, dst))
            src.neighbours.add(dst)
            src = dst
            dst = None
        for query_bus_stop in BusStop.objects.filter(fremiks_alias__isnull=False,
                                                     direction=direction):
            if str(query_bus_stop.fremiks_alias).lower().replace(' ', '') in scrapped_bus_stop.lower().replace(u'\xa0',u' ').replace(' ', ''):
                if src is None:
                    src = query_bus_stop
                else:
                    dst = query_bus_stop
                break
    if src is not None and dst is not None:
        print('%s -> %s' % (src, dst))
        src.neighbours.add(dst)
    print('')


def populate(schedule, line, direction, carrier):
    for bus_stop in schedule:
        for course_type in schedule[bus_stop]:
            for departure in schedule[bus_stop][course_type]:
                condition = departure.split(':')
                if condition[-1] != '':
                    Course.objects.create(line=line, direction=direction, bus_stop=bus_stop, course_type=course_type,
                                          departure=departure, carrier=carrier)


def fremiks_update():
    fremiks_lines = Line.objects.filter(url__contains='fremiks')
    carrier = Carrier.objects.get(name__iexact='fremiks')
    for line in fremiks_lines:
        print('--- %s Scraping %s ---' % (carrier, line))
        f_scrapper = FremiksScraper(line.url)
        data_table = f_scrapper.get_table()
        print('--- %s Getting schedule --- ' % carrier)
        schedule = f_scrapper.get_schedule(table=data_table)
        direction = f_scrapper.direction
        print('--- %s Populating database ---' % carrier)
        populate(schedule, line, direction, carrier)
        update_fremiks_graph(table=data_table, direction=direction)


def mpk_update():
    mpk_lines = Line.objects.filter(url__contains='mpk')
    carrier = Carrier.objects.get(name__icontains='mpk')
    for line in mpk_lines:
        print('--- %s Scraping %s ---' % (carrier, line))
        mpk_soup = MpkSoup(line.url)
        email_sent = False
        direction = None
        for url in mpk_soup.urls():
            if direction is not None:
                direction = None
            m_scraper = MpkScraper(url)
            try:
                print('--- %s Getting schedule ---' % carrier)
                schedule = m_scraper.get_schedule()
                direction = m_scraper.direction
                print('--- %s Populating database --- ' % line.name)
                schedule = {m_scraper.bus_stop: schedule}
                populate(schedule, line, direction, carrier)
            except BusStop.DoesNotExist:
                if email_sent:
                    continue
                email_sent = True
                # request = urlopen(static('json/emails.json'))
                # email_json = json.loads(request.read())['bus_stops_changed']
                # email_context = {'subject': email_json['subject'],
                #                  'body': email_json['body'] + '<br>' + str(line) + "<br><br>" + email_json['footer']}
                # send_email(receiver='daniel.kusy97@gmail.com', context=email_context)


if __name__ == '__main__':
    with transaction.atomic():
        refresh_all_id()
        Course.objects.all().delete()
        fremiks_update()
        mpk_update()
