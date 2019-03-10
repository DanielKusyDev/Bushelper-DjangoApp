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
    # refresh_all_id()
    # schedules = {}
    # carrier, schedule = get_fremiks_schedules()
    # schedules[carrier] = schedule
    # carrier, schedule = get_mpk_schedules()
    # schedules[carrier] = schedule
    # # todo lbn-lsw courses does not appear if you want to take bus from lsw to lsw
    # Course.objects.all().delete()
    # i = 0
    # for carrier in schedules:
    #     for line in schedules[carrier]:
    #         for direction in schedules[carrier][line]:
    #             for bus_stop in schedules[carrier][line][direction]:
    #                 for c_type in schedules[carrier][line][direction][bus_stop]:
    #                     for departure in schedules[carrier][line][direction][bus_stop][c_type]:
    #                         i = i+1
    #                         course = Course(course_type=c_type,
    #                                         bus_stop=bus_stop,
    #                                         carrier=carrier,
    #                                         direction=Direction.objects.get(direction__iexact=direction),
    #                                         line=line,
    #                                         departure=departure)
    #                         course.save()
    Direction(direction='lbn').save()
    Direction(direction='lsw').save()
    Carrier(name='Fremiks').save()
    Carrier(name='MPK').save()
    Line(url="http://mpk.lublin.pl/index.php?s=rozklady&lin=055", name="055").save()
    Line(url="http://mpk.lublin.pl/index.php?s=rozklady&lin=0N2", name="0N2").save()
    Line(url="http://mpk.lublin.pl/index.php?s=rozklady&lin=035", name="035").save()
    Line(url="http://mpk.lublin.pl/index.php?s=rozklady&lin=005", name="005").save()
    BusStop(mpk_street="Lotników Polskich stacja paliw 01", fremiks_alias="cpn powrót", latitude="51.213444",
            longtitude="22.686484", direction_id=2).save()
    BusStop(mpk_street="Lotników Polskich stacja paliw 02", fremiks_alias="cpn", latitude="51.21436",
            longtitude="22.6873", direction_id=1).save()
    BusStop(mpk_street="Jana Pawła II 02", fremiks_alias="Rondo", latitude="51.20919", longtitude="22.68069",
            direction_id=1).save()
    BusStop(mpk_street="Jana Pawła II", fremiks_alias="12-6167-02", latitude="51.21005", longtitude="22.67258",
            direction_id=2).save()
    BusStop(mpk_street="Racławicka I 02", fremiks_alias="Bank", latitude="51.215103", longtitude="22.705779",
            direction_id=1).save()
    BusStop(mpk_street="Racławicka I 01", fremiks_alias="Jarzębinowa powrót", latitude="51.215236",
            longtitude="22.702978", direction_id=2).save()
    BusStop(mpk_street="Racławicka II 02", fremiks_alias="Czereśniowa", latitude="51.21594", longtitude="22.69535",
            direction_id=1).save()
    BusStop(mpk_street="Racławicka II 01", fremiks_alias="Carrefour powrót", latitude="51.215944",
            longtitude="22.692502", direction_id=2).save()
    BusStop(mpk_street="Kusocińskiego 01", fremiks_alias="Olimpijczyków", latitude="51.210531", longtitude="22.708484",
            direction_id=2).save()
    BusStop(mpk_street="Armii Krajowej", fremiks_alias="Galant", latitude="51.21884", longtitude="22.71732",
            direction_id=1).save()
    BusStop(mpk_street="Kosynierów II 02", fremiks_alias="Kościół", latitude="51.2195", longtitude="22.71049",
            direction_id=1).save()
    BusStop(mpk_street="Kosynierów 01", fremiks_alias="Hallera powrót", latitude="51.21729", longtitude="22.7093",
            direction_id=2).save()
    BusStop(mpk_street="Kusocińskiego 02", fremiks_alias="Olimpijczyków", latitude="51.210531", longtitude="22.708484",
            direction_id=1).save()
    BusStop(mpk_street="Jana Pawła II", fremiks_alias="12-6167-01", latitude="51.21057", longtitude="22.67072",
            direction_id=1).save()
    BusStop(mpk_street="Doświadczalna 02", fremiks_alias="Doświadczalna 02", latitude="51.22402", longtitude="22.63127",
            direction_id=1).save()
    BusStop(mpk_street="Grygowej 02", fremiks_alias="Grygowa", latitude="51.22882", longtitude="22.61884",
            direction_id=1).save()
    BusStop(mpk_street="Witosa Carrefour 02", fremiks_alias="Witosa Carrefour 02", latitude="51.233",
            longtitude="22.60647", direction_id=1).save()
    BusStop(mpk_street="Witosa Carrefour 01", fremiks_alias="Witosa Carrefour 01", latitude="51.23407",
            longtitude="22.60146", direction_id=2).save()
    BusStop(mpk_street="Grygowej 01", fremiks_alias="Grygowa 01", latitude="51.22738", longtitude="22.61976",
            direction_id=2).save()
    BusStop(mpk_street="Doświadczalna 05", fremiks_alias="Doświadczalna 05", latitude="51.22312", longtitude="22.63276",
            direction_id=2).save()
    BusStop(mpk_street="Dworzec Gł. PKS", fremiks_alias="Tysiąclecia 6", latitude="51.25229", longtitude="22.57151",
            direction_id=2).save()
    BusStop(mpk_street="Dworzec Gł. PKS", fremiks_alias="Dworzec Gł. PKS", latitude="51.25181", longtitude="22.57282",
            direction_id=1).save()
    BusStop(mpk_street="Witosa Atrium Felicity 01", fremiks_alias="Witosa Atrium Felicity 01", latitude="51.23084",
            longtitude="22.61564", direction_id=2).save()
    BusStop(mpk_street="Witosa Atrium Felicity 01", fremiks_alias="Witosa Atrium Felicity 01", latitude="51.23084",
            longtitude="22.61564", direction_id=1).save()
    BusStop(mpk_street="Lotników Polskich - działki 01", latitude="51.20952", longtitude="22.68243",
            direction_id=2).save()
    BusStop(mpk_street="Świdnik Helikopter 02", latitude="51.21828", longtitude="22.69233", direction_id=1).save()
    BusStop(mpk_street="Świdnik Helikopter 01", latitude="51.21824", longtitude="22.69195", direction_id=2).save()
    BusStop(mpk_street="Kino Lot 01", latitude="51.22026", longtitude="22.69323", direction_id=1).save()
    BusStop(mpk_street="Niepodległości - szpital 02", latitude="51.22057", longtitude="22.69586", direction_id=1).save()
    BusStop(mpk_street="Niepodległości - szpital 01", latitude="51.22092", longtitude="22.69436", direction_id=2).save()
    BusStop(mpk_street="Okulickiego II 01", latitude="51.22168", longtitude="22.70188", direction_id=2).save()
    BusStop(mpk_street="Okulickiego I 01", latitude="51.22067", longtitude="22.70835", direction_id=2).save()
    BusStop(mpk_street="Niepodległości I 02", latitude="51.21871", longtitude="22.7078", direction_id=1).save()
    BusStop(mpk_street="Lotników Polskich - działki 02", latitude="51.21304", longtitude="22.68553",
            direction_id=1).save()
    BusStop(mpk_street="Kosynierów I 02", latitude="51.21711", longtitude="22.70901", direction_id=1).save()
    BusStop(mpk_street="Lotników Polskich - szpital 02", latitude="51.22217", longtitude="22.69417",
            direction_id=2).save()
    BusStop(mpk_street="Felin Europark 02", latitude="51.22038", longtitude="22.64042", direction_id=1).save()
    BusStop(mpk_street="Witosa Felicity 02", latitude="51.23074", longtitude="22.61265", direction_id=1).save()
    BusStop(mpk_street="Witosa Makro 02", latitude="51.23493", longtitude="22.60106", direction_id=1).save()
    BusStop(mpk_street="Pogodna 02", latitude="51.23599", longtitude="22.59466", direction_id=1).save()
    BusStop(mpk_street="Łabędzia 02", latitude="51.23252", longtitude="22.59171", direction_id=1).save()
    BusStop(mpk_street="Lotnicza 02", latitude="51.23293", longtitude="22.58695", direction_id=1).save()
    BusStop(mpk_street="Park Bronowice 04", latitude="51.23702", longtitude="22.57558", direction_id=1).save()
    BusStop(mpk_street="Zamojska 02", latitude="51.24163", longtitude="22.56937", direction_id=1).save()
    BusStop(mpk_street="Plac Wolności 01", latitude="51.24693", longtitude="22.56307", direction_id=1).save()
    BusStop(mpk_street="Okopowa 02", latitude="51.24539", longtitude="22.55565", direction_id=1).save()
    BusStop(mpk_street="Ogród Saski 03", latitude="51.24773", longtitude="22.55044", direction_id=1).save()
    BusStop(mpk_street="KUL 01", latitude="51.24994", longtitude="22.54255", direction_id=1).save()
    BusStop(mpk_street="Krakowskie Przedmieście 02", latitude="51.24762", longtitude="22.55381", direction_id=2).save()
    BusStop(mpk_street="Mościckiego 02", latitude="51.24525", longtitude="22.55944", direction_id=2).save()
    BusStop(mpk_street="Plac Wolności 02", latitude="51.24674", longtitude="22.56299", direction_id=2).save()
    BusStop(mpk_street="Zamojska 01", latitude="51.24211", longtitude="22.56883", direction_id=2).save()
    BusStop(mpk_street="Rondo Lubelskiego Lipca 80 01", latitude="51.23776", longtitude="22.57257",
            direction_id=2).save()
    BusStop(mpk_street="Park Bronowice 03", latitude="51.23609", longtitude="22.57746", direction_id=2).save()
    BusStop(mpk_street="Lotnicza 01", latitude="51.23318", longtitude="22.58566", direction_id=2).save()
    BusStop(mpk_street="Łabędzia 01", latitude="51.2333", longtitude="22.59292", direction_id=2).save()
    BusStop(mpk_street="Pogodna 01", latitude="51.23503", longtitude="22.59455", direction_id=2).save()
    BusStop(mpk_street="PTHW 01", latitude="51.23299", longtitude="22.60497", direction_id=2).save()
    BusStop(mpk_street="Ordonówny II 01", latitude="51.2319", longtitude="22.60798", direction_id=2).save()
    BusStop(mpk_street="Witosa Felicity 01", latitude="51.22987", longtitude="22.61398", direction_id=2).save()
    BusStop(mpk_street="Pancerniaków 04", latitude="51.23019", longtitude="22.62195", direction_id=2).save()
    BusStop(mpk_street="Świdnik stadion 04", latitude="51.22438", longtitude="22.69404", direction_id=1).save()
    BusStop(mpk_street="Żwirki i Wigury II 02", latitude="51.22598", longtitude="22.68383", direction_id=1).save()
    BusStop(mpk_street="Nadleśnictwo Świdnik 02", latitude="51.22887", longtitude="22.67562", direction_id=1).save()
    BusStop(mpk_street="Kolonia Świdnik Mały - rondo 02", latitude="51.241", longtitude="22.67793",
            direction_id=1).save()
    BusStop(mpk_street="Kolonia Świdnik Mały 02", latitude="51.24167", longtitude="22.67231", direction_id=1).save()
    BusStop(mpk_street="Metalurgiczna - hurtownia 02", latitude="51.24358", longtitude="22.6351", direction_id=1).save()
    BusStop(mpk_street="Tokarska 02", latitude="51.24522", longtitude="22.6235", direction_id=1).save()
    BusStop(mpk_street="Outlet Center 02", latitude="51.2468", longtitude="22.61395", direction_id=1).save()
    BusStop(mpk_street="Mełgiewska WSEI 02", latitude="51.24752", longtitude="22.60979", direction_id=1).save()
    BusStop(mpk_street="Montażowa 02", latitude="51.24875", longtitude="22.60222", direction_id=1).save()
    BusStop(mpk_street="Dworzec Gł. PKS 02", latitude="51.2516", longtitude="22.57115", direction_id=1).save()
    BusStop(mpk_street="Szewska 02", latitude="51.25106", longtitude="22.56646", direction_id=1).save()
    BusStop(mpk_street="Brama Krakowska 03", latitude="51.24857", longtitude="22.56616", direction_id=1).save()
    BusStop(mpk_street="Brama Krakowska 03", latitude="51.24857", longtitude="22.56616", direction_id=2).save()
    BusStop(mpk_street="Dworzec Gł. PKS 01", latitude="51.2514", longtitude="22.56979", direction_id=2).save()
    BusStop(mpk_street="Tarasy Zamkowe 03", latitude="51.25069", longtitude="22.57637", direction_id=2).save()
    BusStop(mpk_street="Montażowa 01", latitude="51.24861", longtitude="22.60103", direction_id=2).save()
    BusStop(mpk_street="Mełgiewska WSEI 01", latitude="51.24691", longtitude="22.61128", direction_id=2).save()
    BusStop(mpk_street="Outlet Center 01", latitude="51.24649", longtitude="22.61362", direction_id=2).save()
    BusStop(mpk_street="Tokarska 01", latitude="51.24532", longtitude="22.62087", direction_id=2).save()
    BusStop(mpk_street="Tyszowiecka 01", latitude="51.24424", longtitude="22.62759", direction_id=2).save()
    BusStop(mpk_street="Metalurgiczna - hurtownia 01", latitude="51.24242", longtitude="22.63705",
            direction_id=2).save()
    BusStop(mpk_street="Kolonia Świdnik Mały 01", latitude="51.24133", longtitude="22.6741", direction_id=2).save()
    BusStop(mpk_street="Kolonia Świdnik Mały - rondo 01", latitude="51.23867", longtitude="22.68008",
            direction_id=2).save()
    BusStop(mpk_street="Nadleśnictwo Świdnik 01", latitude="51.22801", longtitude="22.67504", direction_id=2).save()
    BusStop(mpk_street="Żwirki i Wigury II 01", latitude="51.22574", longtitude="22.68475", direction_id=2).save()
    BusStop(mpk_street="Świdnik stadion 01", latitude="51.22488", longtitude="22.69544", direction_id=2).save()
    BusStop(mpk_street="Franciszków - Szkolna 01", latitude="51.22698", longtitude="22.72059", direction_id=2).save()
    BusStop(mpk_street="Port Lotniczy Lublin - odloty 01", latitude="51.23471", longtitude="22.71977",
            direction_id=2).save()
    BusStop(mpk_street="Franciszków - skrzyżowanie 01", latitude="51.23379", longtitude="22.72659",
            direction_id=2).save()
    BusStop(mpk_street="Felin 02", latitude="51.220867", longtitude="22.629455", direction_id=1).save()
    BusStop(mpk_street="Park Bronowice 01", latitude="51.23686", longtitude="22.57772", direction_id=1).save()
    BusStop(mpk_street="Fabryka Wag 01", latitude="51.24044", longtitude="22.58551", direction_id=1).save()
    BusStop(mpk_street="Przyjaźni 01", latitude="51.24197", longtitude="22.58886", direction_id=1).save()
    BusStop(mpk_street="Dworzec Północny 01", latitude="51.24272", longtitude="22.5973", direction_id=1).save()
    BusStop(mpk_street="Kresowa 01", latitude="51.24543", longtitude="22.60065", direction_id=1).save()
    BusStop(mpk_street="Kalinowszczyzna 02", latitude="51.25342", longtitude="22.59413", direction_id=1).save()
    BusStop(mpk_street="Kleeberga 02", latitude="51.25718", longtitude="22.59067", direction_id=1).save()
    BusStop(mpk_street="Rondo Berbeckiego 02", latitude="51.25759", longtitude="22.58386", direction_id=1).save()
    BusStop(mpk_street="Krzemieniecka 02", latitude="51.25553", longtitude="22.57985", direction_id=1).save()
    BusStop(mpk_street="Plac Singera 02", latitude="51.25327", longtitude="22.57646", direction_id=1).save()
    BusStop(mpk_street="KUL 03", latitude="51.24909", longtitude="22.54126", direction_id=1).save()
    BusStop(mpk_street="UMCS 01", latitude="51.24636", longtitude="22.53913", direction_id=1).save()
    BusStop(mpk_street="Park Akademicki 03", latitude="51.24401", longtitude="22.53497", direction_id=1).save()
    BusStop(mpk_street="Pana Tadeusza 01", latitude="51.24464", longtitude="22.53147", direction_id=1).save()
    BusStop(mpk_street="Os. Słowackiego 01", latitude="51.24301", longtitude="22.52021", direction_id=1).save()
    BusStop(mpk_street="Zana Leclerc 01", latitude="51.24069", longtitude="22.51779", direction_id=1).save()
    BusStop(mpk_street="Skrzetuskiego 01", latitude="51.23955", longtitude="22.51291", direction_id=1).save()
    BusStop(mpk_street="Irydiona 01", latitude="51.2415", longtitude="22.50878", direction_id=1).save()
    BusStop(mpk_street="Poczekajka 01", latitude="51.24236", longtitude="22.50604", direction_id=1).save()
    BusStop(mpk_street="Szpital Wojewódzki 01", latitude="51.23936", longtitude="22.49935", direction_id=1).save()
    BusStop(mpk_street="Zwycięska 01", latitude="51.23757", longtitude="22.49538", direction_id=1).save()
    BusStop(mpk_street="Rzemieślnicza 03", latitude="51.23416", longtitude="22.48988", direction_id=1).save()
    BusStop(mpk_street="Poznańska 02", latitude="51.23336", longtitude="22.498", direction_id=1).save()
    BusStop(mpk_street="Wiklinowa 02", latitude="51.23243", longtitude="22.50582", direction_id=1).save()
    BusStop(mpk_street="Jutrzenki 01", latitude="51.2301", longtitude="22.5129", direction_id=1).save()
    BusStop(mpk_street="Bociania 01", latitude="51.22777", longtitude="22.51197", direction_id=1).save()
    BusStop(mpk_street="Perłowa 01", latitude="51.22508", longtitude="22.50402", direction_id=1).save()
    BusStop(mpk_street="Perłowa 02", latitude="51.22531", longtitude="22.50549", direction_id=2).save()
    BusStop(mpk_street="Bociania 02", latitude="51.22728", longtitude="22.51129", direction_id=2).save()
    BusStop(mpk_street="Jutrzenki 02", latitude="51.23007", longtitude="22.51341", direction_id=2).save()
    BusStop(mpk_street="Wiklinowa 01", latitude="51.23246", longtitude="22.50698", direction_id=2).save()
    BusStop(mpk_street="Poznańska 01", latitude="51.2335", longtitude="22.49923", direction_id=2).save()
    BusStop(mpk_street="Rzemieślnicza 02", latitude="51.23511", longtitude="22.4905", direction_id=2).save()
    BusStop(mpk_street="Zwycięska 02", latitude="51.23808", longtitude="22.49718", direction_id=2).save()
    BusStop(mpk_street="Szpital Wojewódzki 02", latitude="51.23994", longtitude="22.50128", direction_id=2).save()
    BusStop(mpk_street="Poczekajka 04", latitude="51.24201", longtitude="22.50772", direction_id=2).save()
    BusStop(mpk_street="Skrzetuskiego 02", latitude="51.23967", longtitude="22.51526", direction_id=2).save()
    BusStop(mpk_street="Os. Słowackiego 02", latitude="51.24336", longtitude="22.52156", direction_id=2).save()
    BusStop(mpk_street="Pana Tadeusza 02", latitude="51.24421", longtitude="22.53221", direction_id=2).save()
    BusStop(mpk_street="UMCS 02", latitude="51.24552", longtitude="22.53949", direction_id=2).save()
    BusStop(mpk_street="KUL 02", latitude="51.24866", longtitude="22.54274", direction_id=2).save()
    BusStop(mpk_street="Plac Singera 01", latitude="51.25301", longtitude="22.57686", direction_id=2).save()
    BusStop(mpk_street="Krzemieniecka 01", latitude="51.25562", longtitude="22.58087", direction_id=2).save()
    BusStop(mpk_street="Rondo Berbeckiego 01", latitude="51.25743", longtitude="22.58409", direction_id=2).save()
    BusStop(mpk_street="Kleeberga 01", latitude="51.25757", longtitude="22.58899", direction_id=2).save()
    BusStop(mpk_street="Kalinowszczyzna 03", latitude="51.25347", longtitude="22.59372", direction_id=2).save()
    BusStop(mpk_street="Kresowa 02", latitude="51.24588", longtitude="22.6009", direction_id=2).save()
    BusStop(mpk_street="Dworzec Północny 02", latitude="51.24284", longtitude="22.59698", direction_id=2).save()
    BusStop(mpk_street="Przyjaźni 02", latitude="51.2428", longtitude="22.59034", direction_id=2).save()
    BusStop(mpk_street="Fabryka Wag 02", latitude="51.24054", longtitude="22.58527", direction_id=2).save()
    BusStop(mpk_street="Składowa 02", latitude="51.23897", longtitude="22.58182", direction_id=2).save()
    BusStop(mpk_street="Doświadczalna 03", latitude="51.220867", longtitude="22.629455", direction_id=2).save()
    BusStop(mpk_street="Grygowej 03", latitude="51.22878", longtitude="22.62033", direction_id=1).save()
    BusStop(mpk_street="Pancerniaków 01", latitude="51.23019", longtitude="22.62195", direction_id=1).save()
    Course(departure="04:50:00", course_type="D", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:23:00", course_type="D", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:46:00", course_type="D", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:05:00", course_type="D", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:27:00", course_type="D", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:42:00", course_type="D", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:57:00", course_type="D", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:12:00", course_type="D", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:27:00", course_type="D", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:43:00", course_type="D", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:57:00", course_type="D", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:12:00", course_type="D", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:27:00", course_type="D", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:51:00", course_type="D", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:11:00", course_type="D", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:42:00", course_type="D", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:11:00", course_type="D", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:41:00", course_type="D", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:11:00", course_type="D", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:46:00", course_type="D", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:11:00", course_type="D", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:46:00", course_type="D", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:11:00", course_type="D", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:31:00", course_type="D", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:47:00", course_type="D", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:00:00", course_type="D", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:15:00", course_type="D", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:33:00", course_type="D", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:48:00", course_type="D", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:04:00", course_type="D", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:18:00", course_type="D", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:35:00", course_type="D", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:48:00", course_type="D", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:03:00", course_type="D", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:18:00", course_type="D", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:38:00", course_type="D", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:48:00", course_type="D", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:05:00", course_type="D", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:18:00", course_type="D", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:43:00", course_type="D", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:19:00", course_type="D", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:41:00", course_type="D", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:18:00", course_type="D", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:51:00", course_type="D", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:19:00", course_type="D", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:37:00", course_type="D", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:12:00", course_type="E", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:42:00", course_type="E", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:01:00", course_type="E", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:22:00", course_type="E", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:41:00", course_type="E", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:59:00", course_type="E", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:19:00", course_type="E", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:39:00", course_type="E", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:59:00", course_type="E", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:19:00", course_type="E", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:38:00", course_type="E", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:59:00", course_type="E", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:19:00", course_type="E", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:39:00", course_type="E", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:58:00", course_type="E", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:18:00", course_type="E", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:37:00", course_type="E", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:58:00", course_type="E", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:18:00", course_type="E", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:38:00", course_type="E", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:58:00", course_type="E", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:18:00", course_type="E", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:37:00", course_type="E", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:58:00", course_type="E", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:18:00", course_type="E", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:38:00", course_type="E", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:58:00", course_type="E", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:17:00", course_type="E", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:38:00", course_type="E", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:58:00", course_type="E", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:18:00", course_type="E", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:38:00", course_type="E", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:20:00", course_type="E", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:40:00", course_type="E", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:20:00", course_type="E", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:39:00", course_type="E", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:20:00", course_type="E", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:45:00", course_type="E", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:15:00", course_type="E", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:45:00", course_type="E", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:15:00", course_type="E", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:45:00", course_type="E", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:15:00", course_type="E", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:51:00", course_type="E", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:05:00", course_type="E", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:33:00", course_type="E", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:08:00", course_type="E7", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:38:00", course_type="E7", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:06:00", course_type="E7", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:36:00", course_type="E7", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:06:00", course_type="E7", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:36:00", course_type="E7", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:07:00", course_type="E7", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:37:00", course_type="E7", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:07:00", course_type="E7", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:37:00", course_type="E7", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:07:00", course_type="E7", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:37:00", course_type="E7", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:06:00", course_type="E7", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:36:00", course_type="E7", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:06:00", course_type="E7", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:36:00", course_type="E7", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:06:00", course_type="E7", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:36:00", course_type="E7", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:06:00", course_type="E7", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:36:00", course_type="E7", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:08:00", course_type="E7", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:08:00", course_type="E7", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:38:00", course_type="E7", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:05:00", course_type="E7", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:35:00", course_type="E7", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:05:00", course_type="E7", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:36:00", course_type="E7", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:05:00", course_type="E7", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:35:00", course_type="E7", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:13:00", course_type="E7", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:36:00", course_type="E7", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:05:00", course_type="E7", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:45:00", course_type="E7", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:28:00", course_type="E7", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:05:00", course_type="E7", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:35:00", course_type="E7", bus_stop_id=37, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:18:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=37, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="07:18:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=37, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="08:18:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=37, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="09:18:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=37, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="10:18:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=37, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="11:18:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=37, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="12:18:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=37, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="13:26:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=37, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="14:18:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=37, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="15:18:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=37, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="16:18:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=37, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="17:18:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=37, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="18:18:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=37, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="19:24:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=37, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="20:18:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=37, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="21:18:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=37, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="04:50:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=37,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:17:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=37,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:47:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=37,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:10:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=37,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:29:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=37,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:50:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=37,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:11:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=37,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:31:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=37,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:51:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=37,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:12:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=37,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:32:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=37,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:51:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=37,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:22:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=37,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:02:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=37,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:42:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=37,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:21:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=37,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:01:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=37,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:42:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=37,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:21:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=37,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:52:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=37,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:10:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=37,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:31:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=37,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:52:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=37,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:11:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=37,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:34:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=37,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:54:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=37,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:14:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=37,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:34:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=37,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:58:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=37,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:27:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=37,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:57:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=37,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:26:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=37,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:58:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=37,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:29:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=37,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:58:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=37,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:28:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=37,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:58:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=37,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:28:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=37,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:01:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=37,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:18:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=37,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:37:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=37,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="04:52:00", course_type="D", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:25:00", course_type="D", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:48:00", course_type="D", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:07:00", course_type="D", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:29:00", course_type="D", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:45:00", course_type="D", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:15:00", course_type="D", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:30:00", course_type="D", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:46:00", course_type="D", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:15:00", course_type="D", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:30:00", course_type="D", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:53:00", course_type="D", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:13:00", course_type="D", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:44:00", course_type="D", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:13:00", course_type="D", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:43:00", course_type="D", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:13:00", course_type="D", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:48:00", course_type="D", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:13:00", course_type="D", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:48:00", course_type="D", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:13:00", course_type="D", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:33:00", course_type="D", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:49:00", course_type="D", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:02:00", course_type="D", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:17:00", course_type="D", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:35:00", course_type="D", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:50:00", course_type="D", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:07:00", course_type="D", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:21:00", course_type="D", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:38:00", course_type="D", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:51:00", course_type="D", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:06:00", course_type="D", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:21:00", course_type="D", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:41:00", course_type="D", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:51:00", course_type="D", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:08:00", course_type="D", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:21:00", course_type="D", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:45:00", course_type="D", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:21:00", course_type="D", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:43:00", course_type="D", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:20:00", course_type="D", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:53:00", course_type="D", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:21:00", course_type="D", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:39:00", course_type="D", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:14:00", course_type="E", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:44:00", course_type="E", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:03:00", course_type="E", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:24:00", course_type="E", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:43:00", course_type="E", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:01:00", course_type="E", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:21:00", course_type="E", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:41:00", course_type="E", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:01:00", course_type="E", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:21:00", course_type="E", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:40:00", course_type="E", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:01:00", course_type="E", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:21:00", course_type="E", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:41:00", course_type="E", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:20:00", course_type="E", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:39:00", course_type="E", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:20:00", course_type="E", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:40:00", course_type="E", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:20:00", course_type="E", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:39:00", course_type="E", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:20:00", course_type="E", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:40:00", course_type="E", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:19:00", course_type="E", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:40:00", course_type="E", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:20:00", course_type="E", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:40:00", course_type="E", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:02:00", course_type="E", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:22:00", course_type="E", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:42:00", course_type="E", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:02:00", course_type="E", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:22:00", course_type="E", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:41:00", course_type="E", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:02:00", course_type="E", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:22:00", course_type="E", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:47:00", course_type="E", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:17:00", course_type="E", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:47:00", course_type="E", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:17:00", course_type="E", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:47:00", course_type="E", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:17:00", course_type="E", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:53:00", course_type="E", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:07:00", course_type="E", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:35:00", course_type="E", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:10:00", course_type="E7", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:40:00", course_type="E7", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:08:00", course_type="E7", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:38:00", course_type="E7", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:08:00", course_type="E7", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:38:00", course_type="E7", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:09:00", course_type="E7", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:39:00", course_type="E7", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:09:00", course_type="E7", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:39:00", course_type="E7", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:09:00", course_type="E7", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:39:00", course_type="E7", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:08:00", course_type="E7", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:38:00", course_type="E7", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:08:00", course_type="E7", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:38:00", course_type="E7", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:08:00", course_type="E7", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:38:00", course_type="E7", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:08:00", course_type="E7", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:38:00", course_type="E7", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:10:00", course_type="E7", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:10:00", course_type="E7", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:40:00", course_type="E7", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:07:00", course_type="E7", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:37:00", course_type="E7", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:07:00", course_type="E7", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:38:00", course_type="E7", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:07:00", course_type="E7", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:37:00", course_type="E7", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:15:00", course_type="E7", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:38:00", course_type="E7", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:07:00", course_type="E7", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:47:00", course_type="E7", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:30:00", course_type="E7", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:07:00", course_type="E7", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:37:00", course_type="E7", bus_stop_id=15, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:20:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=15, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="07:20:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=15, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="08:20:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=15, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="09:20:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=15, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="10:20:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=15, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="11:20:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=15, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="12:20:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=15, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="13:28:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=15, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="14:20:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=15, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="15:20:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=15, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="16:20:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=15, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="17:20:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=15, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="18:20:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=15, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="19:26:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=15, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="20:20:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=15, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="21:20:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=15, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="04:52:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=15,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:19:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=15,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:49:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=15,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:12:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=15,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:31:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=15,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:52:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=15,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:13:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=15,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:33:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=15,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:53:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=15,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:14:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=15,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:34:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=15,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:53:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=15,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:24:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=15,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:04:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=15,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:44:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=15,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:23:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=15,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:03:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=15,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:44:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=15,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:23:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=15,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:54:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=15,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:12:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=15,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:33:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=15,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:54:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=15,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:13:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=15,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:36:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=15,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:56:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=15,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:16:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=15,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:36:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=15,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:29:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=15,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:59:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=15,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:28:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=15,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:31:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=15,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:30:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=15,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:30:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=15,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:03:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=15,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:20:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=15,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:39:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=15,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="04:54:00", course_type="D", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:27:00", course_type="D", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:50:00", course_type="D", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:11:00", course_type="D", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:31:00", course_type="D", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:47:00", course_type="D", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:02:00", course_type="D", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:17:00", course_type="D", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:32:00", course_type="D", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:48:00", course_type="D", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:02:00", course_type="D", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:17:00", course_type="D", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:32:00", course_type="D", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:55:00", course_type="D", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:15:00", course_type="D", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:46:00", course_type="D", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:15:00", course_type="D", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:45:00", course_type="D", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:15:00", course_type="D", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:50:00", course_type="D", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:15:00", course_type="D", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:50:00", course_type="D", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:15:00", course_type="D", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:35:00", course_type="D", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:51:00", course_type="D", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:06:00", course_type="D", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:21:00", course_type="D", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:37:00", course_type="D", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:52:00", course_type="D", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:09:00", course_type="D", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:25:00", course_type="D", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:40:00", course_type="D", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:53:00", course_type="D", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:08:00", course_type="D", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:23:00", course_type="D", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:43:00", course_type="D", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:53:00", course_type="D", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:10:00", course_type="D", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:23:00", course_type="D", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:47:00", course_type="D", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:23:00", course_type="D", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:45:00", course_type="D", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:22:00", course_type="D", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:55:00", course_type="D", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:23:00", course_type="D", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:41:00", course_type="D", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:16:00", course_type="E", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:46:00", course_type="E", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:05:00", course_type="E", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:26:00", course_type="E", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:45:00", course_type="E", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:03:00", course_type="E", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:23:00", course_type="E", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:43:00", course_type="E", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:03:00", course_type="E", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:23:00", course_type="E", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:42:00", course_type="E", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:03:00", course_type="E", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:23:00", course_type="E", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:43:00", course_type="E", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:02:00", course_type="E", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:22:00", course_type="E", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:41:00", course_type="E", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:02:00", course_type="E", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:22:00", course_type="E", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:42:00", course_type="E", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:02:00", course_type="E", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:22:00", course_type="E", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:41:00", course_type="E", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:02:00", course_type="E", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:22:00", course_type="E", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:42:00", course_type="E", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:02:00", course_type="E", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:21:00", course_type="E", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:42:00", course_type="E", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:02:00", course_type="E", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:22:00", course_type="E", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:42:00", course_type="E", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:04:00", course_type="E", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:24:00", course_type="E", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:44:00", course_type="E", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:04:00", course_type="E", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:24:00", course_type="E", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:43:00", course_type="E", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:04:00", course_type="E", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:24:00", course_type="E", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:49:00", course_type="E", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:19:00", course_type="E", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:49:00", course_type="E", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:19:00", course_type="E", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:49:00", course_type="E", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:19:00", course_type="E", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:55:00", course_type="E", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:11:00", course_type="E", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:37:00", course_type="E", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:12:00", course_type="E7", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:42:00", course_type="E7", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:10:00", course_type="E7", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:40:00", course_type="E7", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:10:00", course_type="E7", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:40:00", course_type="E7", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:11:00", course_type="E7", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:41:00", course_type="E7", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:11:00", course_type="E7", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:41:00", course_type="E7", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:11:00", course_type="E7", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:41:00", course_type="E7", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:10:00", course_type="E7", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:40:00", course_type="E7", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:10:00", course_type="E7", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:40:00", course_type="E7", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:10:00", course_type="E7", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:40:00", course_type="E7", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:10:00", course_type="E7", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:40:00", course_type="E7", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:12:00", course_type="E7", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:12:00", course_type="E7", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:42:00", course_type="E7", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:09:00", course_type="E7", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:39:00", course_type="E7", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:09:00", course_type="E7", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:40:00", course_type="E7", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:09:00", course_type="E7", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:39:00", course_type="E7", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:17:00", course_type="E7", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:40:00", course_type="E7", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:09:00", course_type="E7", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:49:00", course_type="E7", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:32:00", course_type="E7", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:09:00", course_type="E7", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:39:00", course_type="E7", bus_stop_id=16, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:22:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=16, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="07:22:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=16, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="08:22:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=16, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="09:22:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=16, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="10:22:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=16, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="11:22:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=16, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="12:22:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=16, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="13:30:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=16, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="14:22:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=16, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="15:22:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=16, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="16:22:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=16, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="17:22:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=16, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="18:22:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=16, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="19:28:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=16, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="20:22:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=16, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="21:22:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=16, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="04:54:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=16,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:21:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=16,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:51:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=16,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:16:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=16,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:33:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=16,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:54:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=16,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:15:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=16,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:35:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=16,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:55:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=16,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:16:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=16,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:36:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=16,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:55:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=16,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:26:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=16,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:06:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=16,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:46:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=16,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:25:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=16,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:05:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=16,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:46:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=16,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:25:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=16,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:56:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=16,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:16:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=16,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:35:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=16,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:56:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=16,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:17:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=16,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:38:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=16,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:58:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=16,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:18:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=16,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:38:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=16,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:02:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=16,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:31:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=16,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:01:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=16,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:30:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=16,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:02:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=16,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:33:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=16,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:02:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=16,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:32:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=16,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:02:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=16,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:32:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=16,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:07:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=16,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:22:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=16,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:41:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=16,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="04:55:00", course_type="D", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:28:00", course_type="D", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:51:00", course_type="D", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:12:00", course_type="D", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:32:00", course_type="D", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:48:00", course_type="D", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:03:00", course_type="D", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:18:00", course_type="D", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:33:00", course_type="D", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:49:00", course_type="D", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:03:00", course_type="D", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:18:00", course_type="D", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:33:00", course_type="D", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:56:00", course_type="D", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:16:00", course_type="D", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:47:00", course_type="D", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:16:00", course_type="D", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:46:00", course_type="D", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:16:00", course_type="D", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:51:00", course_type="D", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:16:00", course_type="D", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:51:00", course_type="D", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:16:00", course_type="D", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:36:00", course_type="D", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:52:00", course_type="D", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:07:00", course_type="D", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:22:00", course_type="D", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:38:00", course_type="D", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:53:00", course_type="D", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:10:00", course_type="D", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:26:00", course_type="D", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:41:00", course_type="D", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:54:00", course_type="D", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:09:00", course_type="D", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:24:00", course_type="D", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:44:00", course_type="D", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:54:00", course_type="D", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:11:00", course_type="D", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:24:00", course_type="D", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:48:00", course_type="D", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:24:00", course_type="D", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:46:00", course_type="D", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:23:00", course_type="D", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:56:00", course_type="D", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:24:00", course_type="D", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:42:00", course_type="D", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:17:00", course_type="E", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:47:00", course_type="E", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:06:00", course_type="E", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:27:00", course_type="E", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:46:00", course_type="E", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:04:00", course_type="E", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:24:00", course_type="E", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:44:00", course_type="E", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:04:00", course_type="E", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:24:00", course_type="E", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:43:00", course_type="E", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:04:00", course_type="E", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:24:00", course_type="E", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:44:00", course_type="E", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:03:00", course_type="E", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:23:00", course_type="E", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:42:00", course_type="E", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:03:00", course_type="E", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:23:00", course_type="E", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:43:00", course_type="E", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:03:00", course_type="E", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:23:00", course_type="E", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:42:00", course_type="E", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:03:00", course_type="E", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:23:00", course_type="E", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:43:00", course_type="E", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:03:00", course_type="E", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:22:00", course_type="E", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:43:00", course_type="E", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:03:00", course_type="E", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:23:00", course_type="E", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:43:00", course_type="E", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:05:00", course_type="E", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:25:00", course_type="E", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:45:00", course_type="E", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:05:00", course_type="E", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:25:00", course_type="E", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:44:00", course_type="E", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:05:00", course_type="E", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:25:00", course_type="E", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:50:00", course_type="E", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:20:00", course_type="E", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:50:00", course_type="E", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:20:00", course_type="E", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:50:00", course_type="E", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:20:00", course_type="E", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:56:00", course_type="E", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:12:00", course_type="E", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:38:00", course_type="E", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:13:00", course_type="E7", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:43:00", course_type="E7", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:11:00", course_type="E7", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:41:00", course_type="E7", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:11:00", course_type="E7", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:41:00", course_type="E7", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:12:00", course_type="E7", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:42:00", course_type="E7", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:12:00", course_type="E7", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:42:00", course_type="E7", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:12:00", course_type="E7", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:42:00", course_type="E7", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:11:00", course_type="E7", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:41:00", course_type="E7", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:11:00", course_type="E7", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:41:00", course_type="E7", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:11:00", course_type="E7", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:41:00", course_type="E7", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:11:00", course_type="E7", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:41:00", course_type="E7", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:13:00", course_type="E7", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:13:00", course_type="E7", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:43:00", course_type="E7", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:10:00", course_type="E7", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:40:00", course_type="E7", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:10:00", course_type="E7", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:41:00", course_type="E7", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:10:00", course_type="E7", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:40:00", course_type="E7", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:18:00", course_type="E7", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:41:00", course_type="E7", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:10:00", course_type="E7", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:50:00", course_type="E7", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:33:00", course_type="E7", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:10:00", course_type="E7", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:40:00", course_type="E7", bus_stop_id=38, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:23:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=38, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="07:23:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=38, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="08:23:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=38, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="09:23:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=38, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="10:23:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=38, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="11:23:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=38, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="12:23:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=38, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="13:31:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=38, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="14:23:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=38, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="15:23:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=38, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="16:23:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=38, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="17:23:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=38, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="18:23:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=38, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="19:29:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=38, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="20:23:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=38, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="21:23:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=38, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="04:55:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=38,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:22:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=38,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:52:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=38,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:17:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=38,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:34:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=38,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:55:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=38,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:16:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=38,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:36:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=38,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:56:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=38,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:17:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=38,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:37:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=38,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:56:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=38,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:27:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=38,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:07:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=38,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:47:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=38,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:26:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=38,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:06:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=38,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:47:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=38,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:26:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=38,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:57:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=38,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:17:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=38,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:36:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=38,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:57:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=38,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:18:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=38,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:39:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=38,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:59:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=38,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:19:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=38,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:39:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=38,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:03:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=38,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:32:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=38,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:02:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=38,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:31:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=38,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:03:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=38,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:34:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=38,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:03:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=38,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:33:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=38,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:03:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=38,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:33:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=38,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:08:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=38,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:23:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=38,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:42:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=38,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="04:56:00", course_type="D", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:29:00", course_type="D", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:52:00", course_type="D", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:13:00", course_type="D", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:33:00", course_type="D", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:49:00", course_type="D", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:04:00", course_type="D", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:19:00", course_type="D", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:34:00", course_type="D", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:50:00", course_type="D", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:04:00", course_type="D", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:19:00", course_type="D", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:34:00", course_type="D", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:57:00", course_type="D", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:17:00", course_type="D", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:48:00", course_type="D", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:17:00", course_type="D", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:47:00", course_type="D", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:17:00", course_type="D", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:52:00", course_type="D", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:17:00", course_type="D", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:52:00", course_type="D", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:17:00", course_type="D", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:37:00", course_type="D", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:53:00", course_type="D", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:08:00", course_type="D", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:23:00", course_type="D", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:39:00", course_type="D", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:54:00", course_type="D", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:11:00", course_type="D", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:27:00", course_type="D", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:42:00", course_type="D", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:55:00", course_type="D", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:10:00", course_type="D", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:25:00", course_type="D", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:45:00", course_type="D", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:55:00", course_type="D", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:12:00", course_type="D", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:25:00", course_type="D", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:49:00", course_type="D", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:25:00", course_type="D", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:47:00", course_type="D", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:24:00", course_type="D", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:57:00", course_type="D", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:25:00", course_type="D", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:43:00", course_type="D", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:18:00", course_type="E", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:48:00", course_type="E", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:07:00", course_type="E", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:28:00", course_type="E", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:47:00", course_type="E", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:05:00", course_type="E", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:25:00", course_type="E", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:45:00", course_type="E", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:05:00", course_type="E", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:25:00", course_type="E", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:44:00", course_type="E", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:05:00", course_type="E", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:25:00", course_type="E", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:45:00", course_type="E", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:04:00", course_type="E", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:24:00", course_type="E", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:43:00", course_type="E", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:04:00", course_type="E", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:24:00", course_type="E", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:44:00", course_type="E", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:04:00", course_type="E", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:24:00", course_type="E", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:43:00", course_type="E", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:04:00", course_type="E", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:24:00", course_type="E", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:44:00", course_type="E", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:04:00", course_type="E", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:23:00", course_type="E", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:44:00", course_type="E", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:04:00", course_type="E", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:24:00", course_type="E", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:44:00", course_type="E", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:06:00", course_type="E", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:26:00", course_type="E", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:46:00", course_type="E", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:06:00", course_type="E", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:26:00", course_type="E", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:45:00", course_type="E", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:06:00", course_type="E", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:26:00", course_type="E", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:51:00", course_type="E", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:21:00", course_type="E", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:51:00", course_type="E", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:21:00", course_type="E", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:51:00", course_type="E", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:21:00", course_type="E", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:57:00", course_type="E", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:13:00", course_type="E", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:39:00", course_type="E", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:14:00", course_type="E7", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:44:00", course_type="E7", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:12:00", course_type="E7", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:42:00", course_type="E7", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:12:00", course_type="E7", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:42:00", course_type="E7", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:13:00", course_type="E7", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:43:00", course_type="E7", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:13:00", course_type="E7", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:43:00", course_type="E7", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:13:00", course_type="E7", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:43:00", course_type="E7", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:12:00", course_type="E7", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:42:00", course_type="E7", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:12:00", course_type="E7", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:42:00", course_type="E7", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:12:00", course_type="E7", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:42:00", course_type="E7", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:12:00", course_type="E7", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:42:00", course_type="E7", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:14:00", course_type="E7", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:14:00", course_type="E7", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:44:00", course_type="E7", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:11:00", course_type="E7", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:41:00", course_type="E7", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:11:00", course_type="E7", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:42:00", course_type="E7", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:11:00", course_type="E7", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:41:00", course_type="E7", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:19:00", course_type="E7", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:42:00", course_type="E7", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:11:00", course_type="E7", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:51:00", course_type="E7", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:34:00", course_type="E7", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:11:00", course_type="E7", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:41:00", course_type="E7", bus_stop_id=17, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:24:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=17, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="07:24:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=17, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="08:24:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=17, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="09:24:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=17, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="10:24:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=17, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="11:24:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=17, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="12:24:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=17, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="13:32:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=17, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="14:24:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=17, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="15:24:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=17, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="16:24:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=17, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="17:24:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=17, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="18:24:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=17, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="19:30:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=17, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="20:24:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=17, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="21:24:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=17, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="04:56:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=17,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:23:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=17,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:53:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=17,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:18:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=17,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:35:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=17,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:56:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=17,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:17:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=17,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:37:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=17,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:57:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=17,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:18:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=17,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:38:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=17,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:57:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=17,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:28:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=17,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:08:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=17,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:48:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=17,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:27:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=17,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:07:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=17,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:48:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=17,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:27:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=17,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:58:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=17,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:18:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=17,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:37:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=17,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:58:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=17,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:19:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=17,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:40:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=17,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:20:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=17,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:40:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=17,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:04:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=17,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:33:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=17,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:03:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=17,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:32:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=17,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:04:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=17,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:35:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=17,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:04:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=17,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:34:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=17,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:04:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=17,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:34:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=17,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:09:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=17,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:24:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=17,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:43:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=17,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="04:57:00", course_type="D", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:30:00", course_type="D", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:53:00", course_type="D", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:14:00", course_type="D", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:34:00", course_type="D", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:50:00", course_type="D", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:05:00", course_type="D", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:20:00", course_type="D", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:35:00", course_type="D", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:51:00", course_type="D", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:05:00", course_type="D", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:20:00", course_type="D", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:35:00", course_type="D", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:58:00", course_type="D", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:18:00", course_type="D", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:49:00", course_type="D", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:18:00", course_type="D", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:48:00", course_type="D", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:18:00", course_type="D", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:53:00", course_type="D", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:18:00", course_type="D", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:53:00", course_type="D", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:18:00", course_type="D", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:38:00", course_type="D", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:54:00", course_type="D", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:09:00", course_type="D", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:24:00", course_type="D", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:40:00", course_type="D", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:55:00", course_type="D", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:12:00", course_type="D", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:28:00", course_type="D", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:43:00", course_type="D", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:56:00", course_type="D", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:11:00", course_type="D", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:26:00", course_type="D", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:46:00", course_type="D", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:56:00", course_type="D", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:13:00", course_type="D", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:26:00", course_type="D", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:50:00", course_type="D", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:26:00", course_type="D", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:48:00", course_type="D", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:25:00", course_type="D", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:58:00", course_type="D", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:26:00", course_type="D", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:44:00", course_type="D", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:19:00", course_type="E", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:49:00", course_type="E", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:08:00", course_type="E", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:29:00", course_type="E", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:48:00", course_type="E", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:06:00", course_type="E", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:26:00", course_type="E", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:46:00", course_type="E", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:06:00", course_type="E", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:26:00", course_type="E", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:45:00", course_type="E", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:06:00", course_type="E", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:26:00", course_type="E", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:46:00", course_type="E", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:05:00", course_type="E", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:25:00", course_type="E", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:44:00", course_type="E", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:05:00", course_type="E", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:25:00", course_type="E", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:45:00", course_type="E", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:05:00", course_type="E", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:25:00", course_type="E", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:44:00", course_type="E", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:05:00", course_type="E", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:25:00", course_type="E", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:45:00", course_type="E", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:05:00", course_type="E", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:24:00", course_type="E", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:45:00", course_type="E", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:05:00", course_type="E", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:25:00", course_type="E", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:45:00", course_type="E", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:07:00", course_type="E", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:27:00", course_type="E", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:47:00", course_type="E", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:07:00", course_type="E", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:27:00", course_type="E", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:46:00", course_type="E", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:07:00", course_type="E", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:27:00", course_type="E", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:52:00", course_type="E", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:22:00", course_type="E", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:52:00", course_type="E", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:22:00", course_type="E", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:52:00", course_type="E", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:22:00", course_type="E", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:58:00", course_type="E", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:14:00", course_type="E", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:40:00", course_type="E", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:15:00", course_type="E7", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:45:00", course_type="E7", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:13:00", course_type="E7", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:43:00", course_type="E7", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:13:00", course_type="E7", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:43:00", course_type="E7", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:14:00", course_type="E7", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:44:00", course_type="E7", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:14:00", course_type="E7", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:44:00", course_type="E7", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:14:00", course_type="E7", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:44:00", course_type="E7", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:13:00", course_type="E7", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:43:00", course_type="E7", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:13:00", course_type="E7", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:43:00", course_type="E7", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:13:00", course_type="E7", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:43:00", course_type="E7", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:13:00", course_type="E7", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:43:00", course_type="E7", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:15:00", course_type="E7", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:15:00", course_type="E7", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:45:00", course_type="E7", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:12:00", course_type="E7", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:42:00", course_type="E7", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:12:00", course_type="E7", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:43:00", course_type="E7", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:12:00", course_type="E7", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:42:00", course_type="E7", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:20:00", course_type="E7", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:43:00", course_type="E7", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:12:00", course_type="E7", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:52:00", course_type="E7", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:35:00", course_type="E7", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:12:00", course_type="E7", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:42:00", course_type="E7", bus_stop_id=39, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:25:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=39, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="07:25:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=39, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="08:25:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=39, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="09:25:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=39, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="10:25:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=39, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="11:25:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=39, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="12:25:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=39, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="13:33:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=39, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="14:25:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=39, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="15:25:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=39, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="16:25:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=39, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="17:25:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=39, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="18:25:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=39, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="19:31:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=39, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="20:25:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=39, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="21:25:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=39, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="04:57:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=39,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:24:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=39,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:54:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=39,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:19:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=39,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:36:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=39,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:57:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=39,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:18:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=39,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:38:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=39,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:58:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=39,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:19:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=39,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:39:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=39,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:58:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=39,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:29:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=39,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:09:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=39,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:49:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=39,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:28:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=39,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:08:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=39,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:49:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=39,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:28:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=39,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:59:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=39,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:19:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=39,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:38:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=39,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:59:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=39,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:20:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=39,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:41:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=39,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:01:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=39,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:21:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=39,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:41:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=39,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:05:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=39,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:34:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=39,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:04:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=39,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:33:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=39,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:05:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=39,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:36:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=39,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:05:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=39,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:35:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=39,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:05:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=39,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:35:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=39,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:10:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=39,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:25:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=39,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:44:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=39,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="04:58:00", course_type="D", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:31:00", course_type="D", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:54:00", course_type="D", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:16:00", course_type="D", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:36:00", course_type="D", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:52:00", course_type="D", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:07:00", course_type="D", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:22:00", course_type="D", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:37:00", course_type="D", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:53:00", course_type="D", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:07:00", course_type="D", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:22:00", course_type="D", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:37:00", course_type="D", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:20:00", course_type="D", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:51:00", course_type="D", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:20:00", course_type="D", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:50:00", course_type="D", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:20:00", course_type="D", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:55:00", course_type="D", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:20:00", course_type="D", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:55:00", course_type="D", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:20:00", course_type="D", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:40:00", course_type="D", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:56:00", course_type="D", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:11:00", course_type="D", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:26:00", course_type="D", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:42:00", course_type="D", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:57:00", course_type="D", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:15:00", course_type="D", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:31:00", course_type="D", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:46:00", course_type="D", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:59:00", course_type="D", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:14:00", course_type="D", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:29:00", course_type="D", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:49:00", course_type="D", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:59:00", course_type="D", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:16:00", course_type="D", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:29:00", course_type="D", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:52:00", course_type="D", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:28:00", course_type="D", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:50:00", course_type="D", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:27:00", course_type="D", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:28:00", course_type="D", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:46:00", course_type="D", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:20:00", course_type="E", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:50:00", course_type="E", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:09:00", course_type="E", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:30:00", course_type="E", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:49:00", course_type="E", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:08:00", course_type="E", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:28:00", course_type="E", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:48:00", course_type="E", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:08:00", course_type="E", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:28:00", course_type="E", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:47:00", course_type="E", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:08:00", course_type="E", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:28:00", course_type="E", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:48:00", course_type="E", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:07:00", course_type="E", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:27:00", course_type="E", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:46:00", course_type="E", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:07:00", course_type="E", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:27:00", course_type="E", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:47:00", course_type="E", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:07:00", course_type="E", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:27:00", course_type="E", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:46:00", course_type="E", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:07:00", course_type="E", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:27:00", course_type="E", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:47:00", course_type="E", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:07:00", course_type="E", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:26:00", course_type="E", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:47:00", course_type="E", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:07:00", course_type="E", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:27:00", course_type="E", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:47:00", course_type="E", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:09:00", course_type="E", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:29:00", course_type="E", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:49:00", course_type="E", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:09:00", course_type="E", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:29:00", course_type="E", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:48:00", course_type="E", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:09:00", course_type="E", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:29:00", course_type="E", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:54:00", course_type="E", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:24:00", course_type="E", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:54:00", course_type="E", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:24:00", course_type="E", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:54:00", course_type="E", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:24:00", course_type="E", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:16:00", course_type="E", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:42:00", course_type="E", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:16:00", course_type="E7", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:46:00", course_type="E7", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:14:00", course_type="E7", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:44:00", course_type="E7", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:14:00", course_type="E7", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:44:00", course_type="E7", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:16:00", course_type="E7", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:46:00", course_type="E7", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:16:00", course_type="E7", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:46:00", course_type="E7", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:16:00", course_type="E7", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:46:00", course_type="E7", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:15:00", course_type="E7", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:45:00", course_type="E7", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:15:00", course_type="E7", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:45:00", course_type="E7", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:15:00", course_type="E7", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:45:00", course_type="E7", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:15:00", course_type="E7", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:45:00", course_type="E7", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:17:00", course_type="E7", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:17:00", course_type="E7", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:47:00", course_type="E7", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:14:00", course_type="E7", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:44:00", course_type="E7", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:14:00", course_type="E7", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:45:00", course_type="E7", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:14:00", course_type="E7", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:44:00", course_type="E7", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:22:00", course_type="E7", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:45:00", course_type="E7", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:14:00", course_type="E7", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:54:00", course_type="E7", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:37:00", course_type="E7", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:14:00", course_type="E7", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:44:00", course_type="E7", bus_stop_id=40, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:26:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=40, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="07:26:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=40, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="08:27:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=40, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="09:27:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=40, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="10:27:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=40, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="11:27:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=40, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="12:27:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=40, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="13:35:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=40, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="14:27:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=40, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="15:27:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=40, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="16:27:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=40, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="17:27:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=40, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="18:27:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=40, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="19:33:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=40, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="20:27:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=40, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="21:27:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=40, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="04:58:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=40,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:25:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=40,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:55:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=40,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:20:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=40,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:38:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=40,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:59:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=40,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:20:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=40,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:40:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=40,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:21:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=40,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:41:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=40,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:31:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=40,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:11:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=40,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:51:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=40,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:30:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=40,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:10:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=40,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:51:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=40,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:30:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=40,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:01:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=40,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:21:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=40,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:40:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=40,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:01:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=40,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:22:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=40,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:43:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=40,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:03:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=40,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:23:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=40,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:43:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=40,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:07:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=40,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:36:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=40,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:06:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=40,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:35:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=40,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:07:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=40,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:38:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=40,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:07:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=40,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:37:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=40,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:07:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=40,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:37:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=40,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:12:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=40,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:27:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=40,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:46:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=40,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="04:59:00", course_type="D", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:32:00", course_type="D", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:55:00", course_type="D", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:17:00", course_type="D", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:37:00", course_type="D", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:53:00", course_type="D", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:09:00", course_type="D", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:24:00", course_type="D", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:39:00", course_type="D", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:55:00", course_type="D", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:09:00", course_type="D", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:24:00", course_type="D", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:38:00", course_type="D", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:01:00", course_type="D", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:21:00", course_type="D", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:52:00", course_type="D", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:21:00", course_type="D", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:51:00", course_type="D", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:21:00", course_type="D", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:56:00", course_type="D", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:21:00", course_type="D", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:56:00", course_type="D", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:21:00", course_type="D", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:41:00", course_type="D", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:57:00", course_type="D", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:12:00", course_type="D", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:27:00", course_type="D", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:43:00", course_type="D", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:58:00", course_type="D", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:17:00", course_type="D", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:33:00", course_type="D", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:48:00", course_type="D", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:01:00", course_type="D", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:16:00", course_type="D", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:31:00", course_type="D", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:51:00", course_type="D", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:01:00", course_type="D", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:18:00", course_type="D", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:31:00", course_type="D", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:53:00", course_type="D", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:29:00", course_type="D", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:51:00", course_type="D", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:28:00", course_type="D", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:01:00", course_type="D", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:29:00", course_type="D", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:47:00", course_type="D", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:21:00", course_type="E", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:51:00", course_type="E", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:10:00", course_type="E", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:31:00", course_type="E", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:50:00", course_type="E", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:09:00", course_type="E", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:29:00", course_type="E", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:49:00", course_type="E", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:09:00", course_type="E", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:29:00", course_type="E", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:48:00", course_type="E", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:09:00", course_type="E", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:29:00", course_type="E", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:49:00", course_type="E", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:08:00", course_type="E", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:28:00", course_type="E", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:47:00", course_type="E", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:08:00", course_type="E", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:28:00", course_type="E", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:48:00", course_type="E", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:08:00", course_type="E", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:28:00", course_type="E", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:47:00", course_type="E", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:08:00", course_type="E", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:28:00", course_type="E", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:48:00", course_type="E", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:08:00", course_type="E", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:27:00", course_type="E", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:48:00", course_type="E", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:08:00", course_type="E", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:28:00", course_type="E", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:48:00", course_type="E", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:10:00", course_type="E", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:30:00", course_type="E", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:50:00", course_type="E", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:10:00", course_type="E", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:30:00", course_type="E", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:49:00", course_type="E", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:10:00", course_type="E", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:30:00", course_type="E", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:55:00", course_type="E", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:25:00", course_type="E", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:55:00", course_type="E", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:25:00", course_type="E", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:55:00", course_type="E", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:25:00", course_type="E", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:01:00", course_type="E", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:17:00", course_type="E", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:43:00", course_type="E", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:17:00", course_type="E7", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:47:00", course_type="E7", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:15:00", course_type="E7", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:45:00", course_type="E7", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:15:00", course_type="E7", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:45:00", course_type="E7", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:17:00", course_type="E7", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:47:00", course_type="E7", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:17:00", course_type="E7", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:47:00", course_type="E7", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:17:00", course_type="E7", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:47:00", course_type="E7", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:16:00", course_type="E7", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:46:00", course_type="E7", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:16:00", course_type="E7", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:46:00", course_type="E7", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:16:00", course_type="E7", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:46:00", course_type="E7", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:16:00", course_type="E7", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:46:00", course_type="E7", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:18:00", course_type="E7", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:18:00", course_type="E7", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:48:00", course_type="E7", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:15:00", course_type="E7", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:45:00", course_type="E7", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:15:00", course_type="E7", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:46:00", course_type="E7", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:15:00", course_type="E7", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:45:00", course_type="E7", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:23:00", course_type="E7", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:46:00", course_type="E7", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:15:00", course_type="E7", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:55:00", course_type="E7", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:38:00", course_type="E7", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:15:00", course_type="E7", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:45:00", course_type="E7", bus_stop_id=41, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:27:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=41, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="07:27:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=41, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="08:28:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=41, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="09:28:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=41, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="10:28:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=41, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="11:28:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=41, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="12:28:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=41, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="13:36:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=41, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="14:28:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=41, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="15:28:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=41, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="16:28:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=41, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="17:28:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=41, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="18:28:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=41, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="19:34:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=41, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="20:28:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=41, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="21:28:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=41, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="04:59:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=41,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:26:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=41,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:56:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=41,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:21:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=41,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:40:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=41,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:01:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=41,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:22:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=41,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:42:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=41,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:02:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=41,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:23:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=41,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:42:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=41,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:01:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=41,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:32:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=41,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:12:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=41,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:52:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=41,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:31:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=41,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:11:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=41,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:52:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=41,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:31:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=41,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:02:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=41,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:22:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=41,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:41:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=41,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:03:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=41,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:24:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=41,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:45:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=41,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:05:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=41,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:25:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=41,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:45:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=41,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:09:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=41,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:37:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=41,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:07:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=41,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:36:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=41,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:08:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=41,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:39:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=41,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:08:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=41,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:38:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=41,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:08:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=41,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:38:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=41,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:13:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=41,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:28:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=41,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:47:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=41,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:34:00", course_type="D", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:57:00", course_type="D", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:19:00", course_type="D", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:39:00", course_type="D", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:55:00", course_type="D", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:11:00", course_type="D", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:26:00", course_type="D", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:41:00", course_type="D", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:57:00", course_type="D", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:11:00", course_type="D", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:26:00", course_type="D", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:40:00", course_type="D", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:03:00", course_type="D", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:23:00", course_type="D", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:54:00", course_type="D", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:23:00", course_type="D", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:53:00", course_type="D", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:23:00", course_type="D", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:58:00", course_type="D", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:23:00", course_type="D", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:58:00", course_type="D", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:23:00", course_type="D", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:43:00", course_type="D", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:59:00", course_type="D", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:14:00", course_type="D", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:29:00", course_type="D", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:45:00", course_type="D", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:19:00", course_type="D", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:35:00", course_type="D", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:50:00", course_type="D", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:03:00", course_type="D", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:18:00", course_type="D", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:33:00", course_type="D", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:53:00", course_type="D", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:03:00", course_type="D", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:20:00", course_type="D", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:33:00", course_type="D", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:55:00", course_type="D", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:31:00", course_type="D", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:53:00", course_type="D", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:30:00", course_type="D", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:03:00", course_type="D", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:31:00", course_type="D", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:49:00", course_type="D", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:23:00", course_type="E", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:53:00", course_type="E", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:12:00", course_type="E", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:33:00", course_type="E", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:52:00", course_type="E", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:11:00", course_type="E", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:31:00", course_type="E", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:51:00", course_type="E", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:11:00", course_type="E", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:31:00", course_type="E", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:50:00", course_type="E", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:11:00", course_type="E", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:31:00", course_type="E", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:51:00", course_type="E", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:10:00", course_type="E", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:30:00", course_type="E", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:49:00", course_type="E", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:10:00", course_type="E", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:30:00", course_type="E", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:50:00", course_type="E", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:10:00", course_type="E", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:30:00", course_type="E", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:49:00", course_type="E", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:10:00", course_type="E", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:30:00", course_type="E", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:50:00", course_type="E", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:10:00", course_type="E", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:29:00", course_type="E", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:50:00", course_type="E", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:10:00", course_type="E", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:30:00", course_type="E", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:50:00", course_type="E", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:12:00", course_type="E", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:32:00", course_type="E", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:52:00", course_type="E", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:12:00", course_type="E", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:32:00", course_type="E", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:51:00", course_type="E", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:12:00", course_type="E", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:32:00", course_type="E", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:57:00", course_type="E", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:27:00", course_type="E", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:57:00", course_type="E", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:27:00", course_type="E", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:57:00", course_type="E", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:27:00", course_type="E", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:03:00", course_type="E", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:19:00", course_type="E", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:45:00", course_type="E", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:19:00", course_type="E7", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:49:00", course_type="E7", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:17:00", course_type="E7", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:47:00", course_type="E7", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:17:00", course_type="E7", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:47:00", course_type="E7", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:19:00", course_type="E7", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:49:00", course_type="E7", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:19:00", course_type="E7", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:49:00", course_type="E7", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:19:00", course_type="E7", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:49:00", course_type="E7", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:18:00", course_type="E7", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:48:00", course_type="E7", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:18:00", course_type="E7", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:48:00", course_type="E7", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:18:00", course_type="E7", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:48:00", course_type="E7", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:18:00", course_type="E7", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:48:00", course_type="E7", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:20:00", course_type="E7", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:20:00", course_type="E7", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:50:00", course_type="E7", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:17:00", course_type="E7", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:47:00", course_type="E7", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:17:00", course_type="E7", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:48:00", course_type="E7", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:17:00", course_type="E7", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:47:00", course_type="E7", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:25:00", course_type="E7", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:48:00", course_type="E7", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:17:00", course_type="E7", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:57:00", course_type="E7", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:40:00", course_type="E7", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:17:00", course_type="E7", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:47:00", course_type="E7", bus_stop_id=42, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:29:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=42, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="07:29:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=42, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="08:30:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=42, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="09:30:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=42, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="10:30:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=42, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="11:30:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=42, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="12:30:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=42, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="13:38:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=42, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="14:30:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=42, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="15:30:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=42, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="16:30:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=42, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="17:30:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=42, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="18:30:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=42, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="19:36:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=42, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="20:30:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=42, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="21:30:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=42, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="05:28:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=42,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:58:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=42,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:23:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=42,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:42:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=42,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:03:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=42,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:24:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=42,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:44:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=42,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:04:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=42,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:25:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=42,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:44:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=42,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:03:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=42,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:34:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=42,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:14:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=42,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:54:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=42,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:33:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=42,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:13:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=42,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:54:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=42,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:33:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=42,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:04:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=42,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:24:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=42,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:43:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=42,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:05:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=42,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:26:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=42,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:47:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=42,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:07:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=42,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:27:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=42,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:47:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=42,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:11:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=42,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:39:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=42,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:09:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=42,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:38:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=42,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:10:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=42,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:41:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=42,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:10:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=42,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:40:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=42,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:10:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=42,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:40:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=42,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:15:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=42,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:30:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=42,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:49:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=42,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:08:00", course_type="D", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:42:00", course_type="D", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:05:00", course_type="D", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:27:00", course_type="D", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:49:00", course_type="D", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:05:00", course_type="D", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:22:00", course_type="D", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:37:00", course_type="D", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:52:00", course_type="D", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:08:00", course_type="D", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:22:00", course_type="D", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:37:00", course_type="D", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:50:00", course_type="D", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:13:00", course_type="D", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:33:00", course_type="D", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:04:00", course_type="D", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:33:00", course_type="D", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:03:00", course_type="D", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:33:00", course_type="D", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:08:00", course_type="D", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:33:00", course_type="D", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:08:00", course_type="D", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:33:00", course_type="D", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:53:00", course_type="D", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:09:00", course_type="D", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:24:00", course_type="D", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:39:00", course_type="D", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:55:00", course_type="D", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:13:00", course_type="D", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:32:00", course_type="D", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:48:00", course_type="D", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:03:00", course_type="D", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:16:00", course_type="D", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:31:00", course_type="D", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:46:00", course_type="D", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:06:00", course_type="D", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:16:00", course_type="D", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:33:00", course_type="D", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:43:00", course_type="D", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:05:00", course_type="D", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:41:00", course_type="D", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:01:00", course_type="D", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:39:00", course_type="D", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:12:00", course_type="D", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:40:00", course_type="D", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:58:00", course_type="D", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:31:00", course_type="E", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:01:00", course_type="E", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:20:00", course_type="E", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:41:00", course_type="E", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:20:00", course_type="E", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:40:00", course_type="E", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:20:00", course_type="E", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:40:00", course_type="E", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:59:00", course_type="E", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:20:00", course_type="E", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:40:00", course_type="E", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:20:00", course_type="E", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:40:00", course_type="E", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:59:00", course_type="E", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:20:00", course_type="E", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:40:00", course_type="E", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:20:00", course_type="E", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:40:00", course_type="E", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:59:00", course_type="E", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:20:00", course_type="E", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:40:00", course_type="E", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:20:00", course_type="E", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:39:00", course_type="E", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:20:00", course_type="E", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:40:00", course_type="E", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:21:00", course_type="E", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:41:00", course_type="E", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:01:00", course_type="E", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:21:00", course_type="E", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:41:00", course_type="E", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:21:00", course_type="E", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:41:00", course_type="E", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:06:00", course_type="E", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:36:00", course_type="E", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:06:00", course_type="E", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:36:00", course_type="E", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:06:00", course_type="E", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:36:00", course_type="E", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:12:00", course_type="E", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:28:00", course_type="E", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:54:00", course_type="E", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:27:00", course_type="E7", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:57:00", course_type="E7", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:25:00", course_type="E7", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:55:00", course_type="E7", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:25:00", course_type="E7", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:55:00", course_type="E7", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:28:00", course_type="E7", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:58:00", course_type="E7", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:28:00", course_type="E7", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:58:00", course_type="E7", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:28:00", course_type="E7", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:58:00", course_type="E7", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:27:00", course_type="E7", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:57:00", course_type="E7", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:27:00", course_type="E7", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:57:00", course_type="E7", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:27:00", course_type="E7", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:57:00", course_type="E7", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:27:00", course_type="E7", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:57:00", course_type="E7", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:29:00", course_type="E7", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:29:00", course_type="E7", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:59:00", course_type="E7", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:26:00", course_type="E7", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:56:00", course_type="E7", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:26:00", course_type="E7", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:57:00", course_type="E7", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:26:00", course_type="E7", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:56:00", course_type="E7", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:34:00", course_type="E7", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:57:00", course_type="E7", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:26:00", course_type="E7", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:06:00", course_type="E7", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:49:00", course_type="E7", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:26:00", course_type="E7", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:56:00", course_type="E7", bus_stop_id=44, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:37:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=44, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="07:37:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=44, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="08:39:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=44, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="09:39:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=44, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="10:39:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=44, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="11:39:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=44, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="12:39:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=44, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="13:47:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=44, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="14:39:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=44, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="15:39:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=44, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="16:39:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=44, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="17:39:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=44, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="18:39:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=44, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="19:45:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=44, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="20:39:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=44, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="21:39:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=44, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="05:08:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=44,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:36:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=44,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:06:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=44,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:31:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=44,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:52:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=44,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:13:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=44,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:34:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=44,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:54:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=44,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:14:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=44,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:35:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=44,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:54:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=44,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:13:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=44,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:44:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=44,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:24:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=44,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:04:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=44,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:43:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=44,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:23:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=44,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:04:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=44,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:43:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=44,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:14:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=44,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:34:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=44,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:53:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=44,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:15:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=44,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:36:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=44,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:57:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=44,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:17:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=44,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:37:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=44,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:57:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=44,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:21:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=44,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:49:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=44,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:19:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=44,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:48:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=44,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:20:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=44,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:51:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=44,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:19:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=44,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:49:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=44,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:19:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=44,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:49:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=44,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:24:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=44,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:39:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=44,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:58:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=44,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:10:00", course_type="D", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:44:00", course_type="D", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:07:00", course_type="D", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:29:00", course_type="D", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:51:00", course_type="D", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:07:00", course_type="D", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:24:00", course_type="D", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:39:00", course_type="D", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:54:00", course_type="D", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:10:00", course_type="D", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:24:00", course_type="D", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:39:00", course_type="D", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:52:00", course_type="D", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:15:00", course_type="D", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:35:00", course_type="D", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:06:00", course_type="D", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:35:00", course_type="D", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:05:00", course_type="D", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:35:00", course_type="D", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:10:00", course_type="D", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:35:00", course_type="D", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:10:00", course_type="D", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:35:00", course_type="D", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:55:00", course_type="D", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:11:00", course_type="D", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:26:00", course_type="D", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:41:00", course_type="D", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:57:00", course_type="D", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:15:00", course_type="D", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:34:00", course_type="D", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:50:00", course_type="D", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:05:00", course_type="D", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:18:00", course_type="D", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:33:00", course_type="D", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:48:00", course_type="D", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:08:00", course_type="D", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:18:00", course_type="D", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:35:00", course_type="D", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:45:00", course_type="D", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:07:00", course_type="D", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:43:00", course_type="D", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:03:00", course_type="D", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:41:00", course_type="D", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:14:00", course_type="D", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:42:00", course_type="D", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="23:00:00", course_type="D", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:33:00", course_type="E", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:03:00", course_type="E", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:22:00", course_type="E", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:43:00", course_type="E", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:02:00", course_type="E", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:22:00", course_type="E", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:42:00", course_type="E", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:02:00", course_type="E", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:22:00", course_type="E", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:42:00", course_type="E", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:01:00", course_type="E", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:22:00", course_type="E", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:42:00", course_type="E", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:02:00", course_type="E", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:22:00", course_type="E", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:42:00", course_type="E", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:01:00", course_type="E", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:22:00", course_type="E", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:42:00", course_type="E", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:02:00", course_type="E", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:22:00", course_type="E", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:42:00", course_type="E", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:01:00", course_type="E", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:22:00", course_type="E", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:42:00", course_type="E", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:02:00", course_type="E", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:22:00", course_type="E", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:41:00", course_type="E", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:02:00", course_type="E", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:22:00", course_type="E", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:42:00", course_type="E", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:02:00", course_type="E", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:23:00", course_type="E", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:43:00", course_type="E", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:03:00", course_type="E", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:23:00", course_type="E", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:43:00", course_type="E", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:02:00", course_type="E", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:23:00", course_type="E", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:43:00", course_type="E", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:08:00", course_type="E", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:38:00", course_type="E", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:08:00", course_type="E", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:38:00", course_type="E", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:08:00", course_type="E", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:38:00", course_type="E", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:14:00", course_type="E", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:30:00", course_type="E", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:56:00", course_type="E", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:29:00", course_type="E7", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:59:00", course_type="E7", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:27:00", course_type="E7", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:57:00", course_type="E7", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:27:00", course_type="E7", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:57:00", course_type="E7", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:30:00", course_type="E7", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:30:00", course_type="E7", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:30:00", course_type="E7", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:29:00", course_type="E7", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:59:00", course_type="E7", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:29:00", course_type="E7", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:59:00", course_type="E7", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:29:00", course_type="E7", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:59:00", course_type="E7", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:29:00", course_type="E7", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:59:00", course_type="E7", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:59:00", course_type="E7", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:31:00", course_type="E7", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:01:00", course_type="E7", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:28:00", course_type="E7", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:58:00", course_type="E7", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:28:00", course_type="E7", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:59:00", course_type="E7", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:28:00", course_type="E7", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:58:00", course_type="E7", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:36:00", course_type="E7", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:59:00", course_type="E7", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:28:00", course_type="E7", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:08:00", course_type="E7", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:51:00", course_type="E7", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:28:00", course_type="E7", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:58:00", course_type="E7", bus_stop_id=45, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:39:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=45, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="07:39:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=45, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="08:41:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=45, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="09:41:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=45, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="10:41:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=45, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="11:41:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=45, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="12:41:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=45, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="13:49:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=45, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="14:41:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=45, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="15:41:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=45, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="16:41:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=45, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="17:41:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=45, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="18:41:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=45, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="19:47:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=45, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="20:41:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=45, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="21:41:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=45, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="05:10:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=45,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:38:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=45,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:08:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=45,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:33:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=45,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:54:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=45,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:15:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=45,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:36:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=45,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:56:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=45,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:16:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=45,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:37:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=45,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:56:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=45,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:15:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=45,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:46:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=45,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:26:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=45,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:06:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=45,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:45:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=45,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:25:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=45,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:06:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=45,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:45:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=45,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:16:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=45,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:36:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=45,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:55:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=45,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:17:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=45,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:38:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=45,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:59:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=45,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:19:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=45,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:39:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=45,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:59:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=45,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:23:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=45,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:51:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=45,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:21:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=45,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:50:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=45,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:22:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=45,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:53:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=45,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:21:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=45,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:51:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=45,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:21:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=45,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:51:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=45,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:26:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=45,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:41:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=45,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="23:00:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=45,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:12:00", course_type="D", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:46:00", course_type="D", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:09:00", course_type="D", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:31:00", course_type="D", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:53:00", course_type="D", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:09:00", course_type="D", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:26:00", course_type="D", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:41:00", course_type="D", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:56:00", course_type="D", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:12:00", course_type="D", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:26:00", course_type="D", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:41:00", course_type="D", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:54:00", course_type="D", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:17:00", course_type="D", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:37:00", course_type="D", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:08:00", course_type="D", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:37:00", course_type="D", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:07:00", course_type="D", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:37:00", course_type="D", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:12:00", course_type="D", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:37:00", course_type="D", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:12:00", course_type="D", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:37:00", course_type="D", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:57:00", course_type="D", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:13:00", course_type="D", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:28:00", course_type="D", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:43:00", course_type="D", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:59:00", course_type="D", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:18:00", course_type="D", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:37:00", course_type="D", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:53:00", course_type="D", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:08:00", course_type="D", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:21:00", course_type="D", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:36:00", course_type="D", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:51:00", course_type="D", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:11:00", course_type="D", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:21:00", course_type="D", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:37:00", course_type="D", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:47:00", course_type="D", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:09:00", course_type="D", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:45:00", course_type="D", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:05:00", course_type="D", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:43:00", course_type="D", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:16:00", course_type="D", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:44:00", course_type="D", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="23:01:00", course_type="D", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:35:00", course_type="E", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:05:00", course_type="E", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:24:00", course_type="E", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:45:00", course_type="E", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:04:00", course_type="E", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:24:00", course_type="E", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:44:00", course_type="E", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:04:00", course_type="E", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:24:00", course_type="E", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:44:00", course_type="E", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:03:00", course_type="E", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:24:00", course_type="E", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:44:00", course_type="E", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:04:00", course_type="E", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:24:00", course_type="E", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:44:00", course_type="E", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:03:00", course_type="E", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:24:00", course_type="E", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:44:00", course_type="E", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:04:00", course_type="E", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:24:00", course_type="E", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:44:00", course_type="E", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:03:00", course_type="E", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:24:00", course_type="E", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:44:00", course_type="E", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:04:00", course_type="E", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:24:00", course_type="E", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:43:00", course_type="E", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:04:00", course_type="E", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:24:00", course_type="E", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:44:00", course_type="E", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:04:00", course_type="E", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:25:00", course_type="E", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:45:00", course_type="E", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:05:00", course_type="E", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:25:00", course_type="E", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:45:00", course_type="E", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:04:00", course_type="E", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:25:00", course_type="E", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:45:00", course_type="E", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:10:00", course_type="E", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:40:00", course_type="E", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:10:00", course_type="E", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:40:00", course_type="E", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:10:00", course_type="E", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:40:00", course_type="E", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:16:00", course_type="E", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:32:00", course_type="E", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:58:00", course_type="E", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:31:00", course_type="E7", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:01:00", course_type="E7", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:29:00", course_type="E7", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:59:00", course_type="E7", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:29:00", course_type="E7", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:59:00", course_type="E7", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:32:00", course_type="E7", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:02:00", course_type="E7", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:32:00", course_type="E7", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:02:00", course_type="E7", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:32:00", course_type="E7", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:02:00", course_type="E7", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:31:00", course_type="E7", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:01:00", course_type="E7", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:31:00", course_type="E7", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:01:00", course_type="E7", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:31:00", course_type="E7", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:01:00", course_type="E7", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:31:00", course_type="E7", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:01:00", course_type="E7", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:01:00", course_type="E7", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:33:00", course_type="E7", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:03:00", course_type="E7", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:30:00", course_type="E7", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:30:00", course_type="E7", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:01:00", course_type="E7", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:30:00", course_type="E7", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:38:00", course_type="E7", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:01:00", course_type="E7", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:30:00", course_type="E7", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:10:00", course_type="E7", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:53:00", course_type="E7", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:30:00", course_type="E7", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="23:00:00", course_type="E7", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:41:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=46, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="07:41:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=46, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="08:43:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=46, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="09:43:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=46, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="10:43:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=46, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="11:43:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=46, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="12:43:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=46, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="13:51:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=46, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="14:43:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=46, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="15:43:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=46, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="16:43:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=46, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="17:43:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=46, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="18:43:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=46, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="19:49:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=46, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="20:43:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=46, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="21:43:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=46, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="05:12:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=46,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:40:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=46,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:10:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=46,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:36:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=46,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:57:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=46,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:18:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=46,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:39:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=46,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:59:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=46,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:19:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=46,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:40:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=46,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:59:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=46,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:18:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=46,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:49:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=46,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:29:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=46,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:09:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=46,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:48:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=46,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:28:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=46,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:09:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=46,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:48:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=46,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:19:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=46,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:39:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=46,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:58:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=46,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:20:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=46,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:41:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=46,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:02:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=46,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:22:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=46,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:42:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=46,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:02:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=46,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:26:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=46,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:53:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=46,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:23:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=46,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:52:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=46,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:24:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=46,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:55:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=46,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:23:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=46,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:53:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=46,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:23:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=46,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:53:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=46,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:28:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=46,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:43:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=46,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="23:01:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=46,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:14:00", course_type="D", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:48:00", course_type="D", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:11:00", course_type="D", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:35:00", course_type="D", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:57:00", course_type="D", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:13:00", course_type="D", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:30:00", course_type="D", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:45:00", course_type="D", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:16:00", course_type="D", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:30:00", course_type="D", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:45:00", course_type="D", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:58:00", course_type="D", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:21:00", course_type="D", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:41:00", course_type="D", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:12:00", course_type="D", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:41:00", course_type="D", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:11:00", course_type="D", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:41:00", course_type="D", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:16:00", course_type="D", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:41:00", course_type="D", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:16:00", course_type="D", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:41:00", course_type="D", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:01:00", course_type="D", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:17:00", course_type="D", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:32:00", course_type="D", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:47:00", course_type="D", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:03:00", course_type="D", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:22:00", course_type="D", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:41:00", course_type="D", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:57:00", course_type="D", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:12:00", course_type="D", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:25:00", course_type="D", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:40:00", course_type="D", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:55:00", course_type="D", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:14:00", course_type="D", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:24:00", course_type="D", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:40:00", course_type="D", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:50:00", course_type="D", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:12:00", course_type="D", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:48:00", course_type="D", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:07:00", course_type="D", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:45:00", course_type="D", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:18:00", course_type="D", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:46:00", course_type="D", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="23:03:00", course_type="D", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:37:00", course_type="E", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:07:00", course_type="E", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:26:00", course_type="E", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:47:00", course_type="E", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:07:00", course_type="E", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:27:00", course_type="E", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:47:00", course_type="E", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:07:00", course_type="E", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:27:00", course_type="E", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:47:00", course_type="E", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:06:00", course_type="E", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:27:00", course_type="E", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:47:00", course_type="E", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:08:00", course_type="E", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:28:00", course_type="E", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:48:00", course_type="E", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:07:00", course_type="E", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:28:00", course_type="E", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:48:00", course_type="E", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:08:00", course_type="E", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:28:00", course_type="E", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:48:00", course_type="E", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:07:00", course_type="E", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:28:00", course_type="E", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:48:00", course_type="E", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:08:00", course_type="E", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:28:00", course_type="E", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:47:00", course_type="E", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:08:00", course_type="E", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:28:00", course_type="E", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:48:00", course_type="E", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:07:00", course_type="E", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:28:00", course_type="E", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:48:00", course_type="E", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:08:00", course_type="E", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:28:00", course_type="E", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:48:00", course_type="E", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:07:00", course_type="E", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:28:00", course_type="E", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:48:00", course_type="E", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:13:00", course_type="E", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:43:00", course_type="E", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:12:00", course_type="E", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:42:00", course_type="E", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:12:00", course_type="E", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:42:00", course_type="E", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:18:00", course_type="E", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:34:00", course_type="E", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="23:00:00", course_type="E", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:33:00", course_type="E7", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:03:00", course_type="E7", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:31:00", course_type="E7", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:01:00", course_type="E7", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:31:00", course_type="E7", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:01:00", course_type="E7", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:35:00", course_type="E7", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:05:00", course_type="E7", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:35:00", course_type="E7", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:05:00", course_type="E7", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:35:00", course_type="E7", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:05:00", course_type="E7", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:34:00", course_type="E7", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:04:00", course_type="E7", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:34:00", course_type="E7", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:04:00", course_type="E7", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:34:00", course_type="E7", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:04:00", course_type="E7", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:34:00", course_type="E7", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:04:00", course_type="E7", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:04:00", course_type="E7", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:36:00", course_type="E7", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:06:00", course_type="E7", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:33:00", course_type="E7", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:03:00", course_type="E7", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:33:00", course_type="E7", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:04:00", course_type="E7", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:33:00", course_type="E7", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:03:00", course_type="E7", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:41:00", course_type="E7", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:03:00", course_type="E7", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:32:00", course_type="E7", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:12:00", course_type="E7", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:55:00", course_type="E7", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:32:00", course_type="E7", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="23:02:00", course_type="E7", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:43:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=47, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="07:43:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=47, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="08:46:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=47, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="09:46:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=47, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="10:46:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=47, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="11:46:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=47, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="12:46:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=47, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="13:54:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=47, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="14:46:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=47, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="15:46:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=47, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="16:46:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=47, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="17:46:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=47, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="18:46:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=47, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="19:52:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=47, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="20:45:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=47, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="21:45:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=47, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="05:14:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=47,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:42:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=47,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:12:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=47,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:39:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=47,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:21:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=47,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:42:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=47,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:02:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=47,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:22:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=47,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:43:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=47,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:02:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=47,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:21:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=47,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:52:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=47,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:32:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=47,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:12:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=47,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:51:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=47,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:31:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=47,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:12:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=47,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:51:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=47,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:22:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=47,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:42:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=47,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:01:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=47,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:23:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=47,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:44:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=47,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:05:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=47,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:25:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=47,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:45:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=47,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:05:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=47,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:29:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=47,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:56:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=47,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:26:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=47,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:55:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=47,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:27:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=47,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:58:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=47,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:25:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=47,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:55:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=47,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:25:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=47,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:55:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=47,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:30:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=47,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:45:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=47,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="23:03:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=47,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:16:00", course_type="D", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:50:00", course_type="D", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:13:00", course_type="D", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:37:00", course_type="D", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:59:00", course_type="D", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:15:00", course_type="D", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:32:00", course_type="D", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:47:00", course_type="D", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:02:00", course_type="D", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:18:00", course_type="D", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:32:00", course_type="D", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:47:00", course_type="D", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:23:00", course_type="D", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:43:00", course_type="D", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:14:00", course_type="D", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:43:00", course_type="D", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:13:00", course_type="D", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:43:00", course_type="D", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:18:00", course_type="D", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:43:00", course_type="D", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:18:00", course_type="D", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:43:00", course_type="D", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:04:00", course_type="D", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:20:00", course_type="D", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:35:00", course_type="D", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:50:00", course_type="D", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:06:00", course_type="D", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:25:00", course_type="D", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:44:00", course_type="D", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:15:00", course_type="D", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:28:00", course_type="D", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:43:00", course_type="D", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:58:00", course_type="D", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:17:00", course_type="D", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:27:00", course_type="D", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:42:00", course_type="D", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:52:00", course_type="D", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:14:00", course_type="D", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:50:00", course_type="D", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:09:00", course_type="D", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:47:00", course_type="D", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:20:00", course_type="D", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:48:00", course_type="D", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="23:05:00", course_type="D", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:39:00", course_type="E", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:09:00", course_type="E", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:28:00", course_type="E", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:49:00", course_type="E", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:09:00", course_type="E", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:29:00", course_type="E", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:49:00", course_type="E", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:09:00", course_type="E", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:29:00", course_type="E", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:49:00", course_type="E", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:08:00", course_type="E", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:29:00", course_type="E", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:49:00", course_type="E", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:10:00", course_type="E", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:30:00", course_type="E", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:50:00", course_type="E", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:09:00", course_type="E", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:30:00", course_type="E", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:50:00", course_type="E", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:10:00", course_type="E", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:30:00", course_type="E", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:50:00", course_type="E", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:09:00", course_type="E", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:30:00", course_type="E", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:50:00", course_type="E", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:10:00", course_type="E", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:30:00", course_type="E", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:49:00", course_type="E", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:10:00", course_type="E", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:30:00", course_type="E", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:50:00", course_type="E", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:09:00", course_type="E", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:30:00", course_type="E", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:50:00", course_type="E", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:10:00", course_type="E", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:30:00", course_type="E", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:50:00", course_type="E", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:09:00", course_type="E", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:30:00", course_type="E", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:50:00", course_type="E", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:15:00", course_type="E", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:45:00", course_type="E", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:14:00", course_type="E", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:44:00", course_type="E", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:14:00", course_type="E", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:44:00", course_type="E", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:20:00", course_type="E", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:36:00", course_type="E", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="23:02:00", course_type="E", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:35:00", course_type="E7", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:05:00", course_type="E7", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:33:00", course_type="E7", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:03:00", course_type="E7", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:33:00", course_type="E7", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:03:00", course_type="E7", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:37:00", course_type="E7", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:07:00", course_type="E7", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:37:00", course_type="E7", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:07:00", course_type="E7", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:37:00", course_type="E7", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:07:00", course_type="E7", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:36:00", course_type="E7", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:06:00", course_type="E7", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:36:00", course_type="E7", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:06:00", course_type="E7", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:36:00", course_type="E7", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:06:00", course_type="E7", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:36:00", course_type="E7", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:06:00", course_type="E7", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:06:00", course_type="E7", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:38:00", course_type="E7", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:08:00", course_type="E7", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:35:00", course_type="E7", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:05:00", course_type="E7", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:35:00", course_type="E7", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:06:00", course_type="E7", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:35:00", course_type="E7", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:05:00", course_type="E7", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:43:00", course_type="E7", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:05:00", course_type="E7", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:34:00", course_type="E7", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:14:00", course_type="E7", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:57:00", course_type="E7", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:34:00", course_type="E7", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="23:04:00", course_type="E7", bus_stop_id=48, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:45:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=48, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="07:45:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=48, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="08:48:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=48, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="09:48:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=48, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="10:48:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=48, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="11:48:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=48, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="12:48:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=48, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="13:56:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=48, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="14:48:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=48, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="15:48:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=48, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="16:48:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=48, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="17:48:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=48, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="18:48:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=48, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="19:54:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=48, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="20:47:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=48, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="21:47:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=48, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="05:16:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=48,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:44:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=48,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:14:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=48,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:41:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=48,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:02:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=48,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:23:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=48,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:44:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=48,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:04:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=48,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:24:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=48,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:45:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=48,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:04:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=48,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:23:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=48,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:54:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=48,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:34:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=48,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:14:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=48,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:53:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=48,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:33:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=48,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:14:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=48,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:53:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=48,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:24:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=48,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:44:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=48,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:04:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=48,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:26:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=48,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:47:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=48,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:08:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=48,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:28:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=48,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:48:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=48,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:08:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=48,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:32:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=48,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:58:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=48,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:28:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=48,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:57:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=48,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:29:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=48,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:27:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=48,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:57:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=48,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:27:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=48,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:57:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=48,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:32:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=48,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:47:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=48,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="23:05:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=48,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:39:00", course_type="D", bus_stop_id=145, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:09:00", course_type="D", bus_stop_id=145, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:32:00", course_type="D", bus_stop_id=145, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:39:00", course_type="D", bus_stop_id=145, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:04:00", course_type="D", bus_stop_id=145, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:19:00", course_type="D", bus_stop_id=145, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:02:00", course_type="D", bus_stop_id=145, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:23:00", course_type="D", bus_stop_id=145, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:03:00", course_type="D", bus_stop_id=145, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:08:00", course_type="D", bus_stop_id=145, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:39:00", course_type="E", bus_stop_id=145, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:18:00", course_type="E", bus_stop_id=145, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:09:00", course_type="E", bus_stop_id=145, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:39:00", course_type="E7", bus_stop_id=145, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:39:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=145,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:59:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=145,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:14:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=145,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:32:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=145,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:52:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=145,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:14:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=145,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:15:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=145,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:47:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=145,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:05:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=145,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:10:00", course_type="D", bus_stop_id=146, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:05:00", course_type="D", bus_stop_id=146, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:20:00", course_type="D", bus_stop_id=146, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:24:00", course_type="D", bus_stop_id=146, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:10:00", course_type="E", bus_stop_id=146, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:15:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=146,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:15:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=146,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:16:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=146,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="22:06:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=146,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="04:34:00", course_type="D", bus_stop_id=26, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:48:00", course_type="D", bus_stop_id=26, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:40:00", course_type="D", bus_stop_id=26, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:55:00", course_type="D", bus_stop_id=26, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:10:00", course_type="D", bus_stop_id=26, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:26:00", course_type="D", bus_stop_id=26, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:55:00", course_type="D", bus_stop_id=26, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:34:00", course_type="D", bus_stop_id=26, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:25:00", course_type="D", bus_stop_id=26, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:24:00", course_type="D", bus_stop_id=26, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:29:00", course_type="D", bus_stop_id=26, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:29:00", course_type="D", bus_stop_id=26, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:30:00", course_type="D", bus_stop_id=26, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:47:00", course_type="D", bus_stop_id=26, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:14:00", course_type="D", bus_stop_id=26, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:46:00", course_type="D", bus_stop_id=26, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:17:00", course_type="D", bus_stop_id=26, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:48:00", course_type="D", bus_stop_id=26, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:02:00", course_type="D", bus_stop_id=26, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:26:00", course_type="D", bus_stop_id=26, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:24:00", course_type="D", bus_stop_id=26, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:35:00", course_type="D", bus_stop_id=26, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:45:00", course_type="E", bus_stop_id=26, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:21:00", course_type="E", bus_stop_id=26, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:20:00", course_type="E", bus_stop_id=26, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:20:00", course_type="E", bus_stop_id=26, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:00:00", course_type="E", bus_stop_id=26, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:21:00", course_type="E", bus_stop_id=26, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:22:00", course_type="E", bus_stop_id=26, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:49:00", course_type="E", bus_stop_id=26, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:51:00", course_type="E7", bus_stop_id=26, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:21:00", course_type="E7", bus_stop_id=26, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:19:00", course_type="E7", bus_stop_id=26, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:21:00", course_type="E7", bus_stop_id=26, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:20:00", course_type="E7", bus_stop_id=26, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:20:00", course_type="E7", bus_stop_id=26, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:12:00", course_type="E7", bus_stop_id=26, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:09:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=26, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="19:08:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=26, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="04:34:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=26,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:54:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=26,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:33:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=26,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:54:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=26,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:14:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=26,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:34:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=26,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:34:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=26,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:45:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=26,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:04:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=26,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:44:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=26,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:04:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=26,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:35:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=26,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:13:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=26,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:37:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=26,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:57:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=26,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:13:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=26,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:41:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=26,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:10:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=26,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:09:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=26,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:12:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=26,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:12:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=26,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:45:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=26,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="04:35:00", course_type="D", bus_stop_id=28, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:49:00", course_type="D", bus_stop_id=28, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:41:00", course_type="D", bus_stop_id=28, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:56:00", course_type="D", bus_stop_id=28, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:11:00", course_type="D", bus_stop_id=28, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:27:00", course_type="D", bus_stop_id=28, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:56:00", course_type="D", bus_stop_id=28, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:35:00", course_type="D", bus_stop_id=28, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:26:00", course_type="D", bus_stop_id=28, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:25:00", course_type="D", bus_stop_id=28, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:30:00", course_type="D", bus_stop_id=28, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:30:00", course_type="D", bus_stop_id=28, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:31:00", course_type="D", bus_stop_id=28, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:48:00", course_type="D", bus_stop_id=28, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:15:00", course_type="D", bus_stop_id=28, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:47:00", course_type="D", bus_stop_id=28, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:18:00", course_type="D", bus_stop_id=28, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:49:00", course_type="D", bus_stop_id=28, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:03:00", course_type="D", bus_stop_id=28, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:27:00", course_type="D", bus_stop_id=28, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:25:00", course_type="D", bus_stop_id=28, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:36:00", course_type="D", bus_stop_id=28, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:46:00", course_type="E", bus_stop_id=28, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:22:00", course_type="E", bus_stop_id=28, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:21:00", course_type="E", bus_stop_id=28, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:21:00", course_type="E", bus_stop_id=28, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:01:00", course_type="E", bus_stop_id=28, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:22:00", course_type="E", bus_stop_id=28, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:23:00", course_type="E", bus_stop_id=28, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:50:00", course_type="E", bus_stop_id=28, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:52:00", course_type="E7", bus_stop_id=28, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:22:00", course_type="E7", bus_stop_id=28, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:20:00", course_type="E7", bus_stop_id=28, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:22:00", course_type="E7", bus_stop_id=28, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:21:00", course_type="E7", bus_stop_id=28, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:21:00", course_type="E7", bus_stop_id=28, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:13:00", course_type="E7", bus_stop_id=28, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:10:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=28, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="19:09:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=28, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="04:35:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=28,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:55:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=28,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:34:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=28,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:55:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=28,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:15:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=28,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:35:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=28,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:35:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=28,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:46:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=28,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:05:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=28,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:45:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=28,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:05:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=28,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:36:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=28,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:14:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=28,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:38:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=28,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:58:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=28,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:14:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=28,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:42:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=28,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:11:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=28,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:10:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=28,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:13:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=28,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:13:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=28,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:46:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=28,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="04:38:00", course_type="D", bus_stop_id=33, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:52:00", course_type="D", bus_stop_id=33, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:44:00", course_type="D", bus_stop_id=33, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:59:00", course_type="D", bus_stop_id=33, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:14:00", course_type="D", bus_stop_id=33, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:30:00", course_type="D", bus_stop_id=33, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:59:00", course_type="D", bus_stop_id=33, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:38:00", course_type="D", bus_stop_id=33, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:29:00", course_type="D", bus_stop_id=33, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:28:00", course_type="D", bus_stop_id=33, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:33:00", course_type="D", bus_stop_id=33, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:33:00", course_type="D", bus_stop_id=33, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:34:00", course_type="D", bus_stop_id=33, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:51:00", course_type="D", bus_stop_id=33, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:22:00", course_type="D", bus_stop_id=33, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:50:00", course_type="D", bus_stop_id=33, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:25:00", course_type="D", bus_stop_id=33, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:52:00", course_type="D", bus_stop_id=33, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:06:00", course_type="D", bus_stop_id=33, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:30:00", course_type="D", bus_stop_id=33, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:28:00", course_type="D", bus_stop_id=33, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:39:00", course_type="D", bus_stop_id=33, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:49:00", course_type="E", bus_stop_id=33, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:25:00", course_type="E", bus_stop_id=33, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:24:00", course_type="E", bus_stop_id=33, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:24:00", course_type="E", bus_stop_id=33, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:04:00", course_type="E", bus_stop_id=33, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:25:00", course_type="E", bus_stop_id=33, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:26:00", course_type="E", bus_stop_id=33, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:53:00", course_type="E", bus_stop_id=33, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:55:00", course_type="E7", bus_stop_id=33, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:25:00", course_type="E7", bus_stop_id=33, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:23:00", course_type="E7", bus_stop_id=33, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:25:00", course_type="E7", bus_stop_id=33, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:24:00", course_type="E7", bus_stop_id=33, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:24:00", course_type="E7", bus_stop_id=33, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:16:00", course_type="E7", bus_stop_id=33, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:13:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=33, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="19:12:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=33, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="04:38:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=33,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:58:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=33,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:37:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=33,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:58:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=33,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:18:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=33,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:38:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=33,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:38:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=33,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:49:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=33,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:08:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=33,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:48:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=33,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:08:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=33,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:39:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=33,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:21:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=33,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:41:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=33,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:01:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=33,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:21:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=33,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:45:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=33,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:14:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=33,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:13:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=33,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:16:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=33,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:16:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=33,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:49:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=33,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="04:39:00", course_type="D", bus_stop_id=35, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:53:00", course_type="D", bus_stop_id=35, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:45:00", course_type="D", bus_stop_id=35, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:15:00", course_type="D", bus_stop_id=35, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:31:00", course_type="D", bus_stop_id=35, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:39:00", course_type="D", bus_stop_id=35, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:30:00", course_type="D", bus_stop_id=35, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:29:00", course_type="D", bus_stop_id=35, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:34:00", course_type="D", bus_stop_id=35, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:34:00", course_type="D", bus_stop_id=35, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:35:00", course_type="D", bus_stop_id=35, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:52:00", course_type="D", bus_stop_id=35, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:23:00", course_type="D", bus_stop_id=35, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:51:00", course_type="D", bus_stop_id=35, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:26:00", course_type="D", bus_stop_id=35, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:53:00", course_type="D", bus_stop_id=35, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:07:00", course_type="D", bus_stop_id=35, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:31:00", course_type="D", bus_stop_id=35, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:29:00", course_type="D", bus_stop_id=35, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:40:00", course_type="D", bus_stop_id=35, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:50:00", course_type="E", bus_stop_id=35, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:26:00", course_type="E", bus_stop_id=35, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:25:00", course_type="E", bus_stop_id=35, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:25:00", course_type="E", bus_stop_id=35, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:05:00", course_type="E", bus_stop_id=35, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:26:00", course_type="E", bus_stop_id=35, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:27:00", course_type="E", bus_stop_id=35, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:54:00", course_type="E", bus_stop_id=35, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:56:00", course_type="E7", bus_stop_id=35, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:26:00", course_type="E7", bus_stop_id=35, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:24:00", course_type="E7", bus_stop_id=35, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:26:00", course_type="E7", bus_stop_id=35, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:25:00", course_type="E7", bus_stop_id=35, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:25:00", course_type="E7", bus_stop_id=35, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:17:00", course_type="E7", bus_stop_id=35, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:14:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=35, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="19:13:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=35, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="04:39:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=35,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:59:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=35,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:38:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=35,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:59:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=35,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:19:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=35,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:39:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=35,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:39:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=35,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:50:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=35,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:09:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=35,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:49:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=35,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:09:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=35,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:40:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=35,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:22:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=35,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:42:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=35,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:02:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=35,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:22:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=35,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:46:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=35,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:15:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=35,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:14:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=35,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:17:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=35,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:17:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=35,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:50:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=35,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="04:41:00", course_type="D", bus_stop_id=5, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:55:00", course_type="D", bus_stop_id=5, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:47:00", course_type="D", bus_stop_id=5, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:02:00", course_type="D", bus_stop_id=5, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:17:00", course_type="D", bus_stop_id=5, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:33:00", course_type="D", bus_stop_id=5, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:02:00", course_type="D", bus_stop_id=5, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:41:00", course_type="D", bus_stop_id=5, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:32:00", course_type="D", bus_stop_id=5, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:31:00", course_type="D", bus_stop_id=5, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:36:00", course_type="D", bus_stop_id=5, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:36:00", course_type="D", bus_stop_id=5, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:37:00", course_type="D", bus_stop_id=5, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:54:00", course_type="D", bus_stop_id=5, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:25:00", course_type="D", bus_stop_id=5, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:53:00", course_type="D", bus_stop_id=5, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:28:00", course_type="D", bus_stop_id=5, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:55:00", course_type="D", bus_stop_id=5, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:09:00", course_type="D", bus_stop_id=5, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:33:00", course_type="D", bus_stop_id=5, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:31:00", course_type="D", bus_stop_id=5, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:42:00", course_type="D", bus_stop_id=5, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:52:00", course_type="E", bus_stop_id=5, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:28:00", course_type="E", bus_stop_id=5, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:27:00", course_type="E", bus_stop_id=5, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:27:00", course_type="E", bus_stop_id=5, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:07:00", course_type="E", bus_stop_id=5, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:28:00", course_type="E", bus_stop_id=5, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:29:00", course_type="E", bus_stop_id=5, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:56:00", course_type="E", bus_stop_id=5, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:58:00", course_type="E7", bus_stop_id=5, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:28:00", course_type="E7", bus_stop_id=5, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:26:00", course_type="E7", bus_stop_id=5, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:28:00", course_type="E7", bus_stop_id=5, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:27:00", course_type="E7", bus_stop_id=5, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:27:00", course_type="E7", bus_stop_id=5, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:19:00", course_type="E7", bus_stop_id=5, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:16:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=5, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="19:15:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=5, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="04:41:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=5,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:01:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=5,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:40:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=5,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:01:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=5,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:21:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=5,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:41:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=5,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:41:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=5,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:52:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=5,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:11:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=5,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:51:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=5,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:11:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=5,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:42:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=5,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:24:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=5,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:44:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=5,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:04:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=5,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:24:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=5,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:48:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=5,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:17:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=5,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:16:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=5,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:19:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=5,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:19:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=5,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:52:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=5,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="04:42:00", course_type="D", bus_stop_id=7, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:57:00", course_type="D", bus_stop_id=7, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:49:00", course_type="D", bus_stop_id=7, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:04:00", course_type="D", bus_stop_id=7, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:19:00", course_type="D", bus_stop_id=7, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:35:00", course_type="D", bus_stop_id=7, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:04:00", course_type="D", bus_stop_id=7, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:43:00", course_type="D", bus_stop_id=7, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:34:00", course_type="D", bus_stop_id=7, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:33:00", course_type="D", bus_stop_id=7, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:38:00", course_type="D", bus_stop_id=7, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:38:00", course_type="D", bus_stop_id=7, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:39:00", course_type="D", bus_stop_id=7, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:56:00", course_type="D", bus_stop_id=7, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:27:00", course_type="D", bus_stop_id=7, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:55:00", course_type="D", bus_stop_id=7, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:30:00", course_type="D", bus_stop_id=7, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:57:00", course_type="D", bus_stop_id=7, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:11:00", course_type="D", bus_stop_id=7, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:35:00", course_type="D", bus_stop_id=7, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:32:00", course_type="D", bus_stop_id=7, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:43:00", course_type="D", bus_stop_id=7, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:53:00", course_type="E", bus_stop_id=7, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:30:00", course_type="E", bus_stop_id=7, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:29:00", course_type="E", bus_stop_id=7, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:29:00", course_type="E", bus_stop_id=7, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:09:00", course_type="E", bus_stop_id=7, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:30:00", course_type="E", bus_stop_id=7, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:31:00", course_type="E", bus_stop_id=7, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:57:00", course_type="E", bus_stop_id=7, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:59:00", course_type="E7", bus_stop_id=7, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:29:00", course_type="E7", bus_stop_id=7, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:28:00", course_type="E7", bus_stop_id=7, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:30:00", course_type="E7", bus_stop_id=7, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:28:00", course_type="E7", bus_stop_id=7, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:28:00", course_type="E7", bus_stop_id=7, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:20:00", course_type="E7", bus_stop_id=7, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:18:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=7, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="19:16:00", course_type="WIELKANOC: 21 i 22 KWIETNIA 2019", bus_stop_id=7, carrier_id=2,
           direction_id=1, line_id=1).save()
    Course(departure="04:42:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=7,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:02:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=7,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:42:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=7,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:03:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=7,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:23:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=7,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:43:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=7,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:43:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=7,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:54:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=7,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:13:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=7,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:53:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=7,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:13:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=7,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:44:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=7,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:26:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=7,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="15:46:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=7,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:06:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=7,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:26:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=7,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="16:50:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=7,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="17:19:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=7,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="18:18:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=7,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="19:21:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=7,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="20:20:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=7,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="21:53:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=7,
           carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="04:44:00", course_type="D", bus_stop_id=2, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="05:59:00", course_type="D", bus_stop_id=2, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="06:51:00", course_type="D", bus_stop_id=2, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:06:00", course_type="D", bus_stop_id=2, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:21:00", course_type="D", bus_stop_id=2, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="07:37:00", course_type="D", bus_stop_id=2, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:06:00", course_type="D", bus_stop_id=2, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="08:45:00", course_type="D", bus_stop_id=2, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="09:36:00", course_type="D", bus_stop_id=2, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="10:35:00", course_type="D", bus_stop_id=2, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="11:40:00", course_type="D", bus_stop_id=2, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="12:40:00", course_type="D", bus_stop_id=2, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="13:41:00", course_type="D", bus_stop_id=2, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="14:58:00", course_type="D", bus_stop_id=2, carrier_id=2, direction_id=1, line_id=1).save()
    Course(departure="01:01:00", course_type="DE7", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="01:31:00", course_type="DE7", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="02:01:00", course_type="DE7", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="02:31:00", course_type="DE7", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="03:31:00", course_type="DE7", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="04:31:00", course_type="DE7", bus_stop_id=46, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="23:03:00", course_type="DE7", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="23:33:00", course_type="DE7", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="00:03:00", course_type="DE7", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="00:33:00", course_type="DE7", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="01:03:00", course_type="DE7", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="01:33:00", course_type="DE7", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="02:03:00", course_type="DE7", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="02:33:00", course_type="DE7", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="03:33:00", course_type="DE7", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="04:33:00", course_type="DE7", bus_stop_id=47, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="23:05:00", course_type="DE7", bus_stop_id=103, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="23:35:00", course_type="DE7", bus_stop_id=103, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="00:05:00", course_type="DE7", bus_stop_id=103, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="00:35:00", course_type="DE7", bus_stop_id=103, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="01:05:00", course_type="DE7", bus_stop_id=103, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="01:35:00", course_type="DE7", bus_stop_id=103, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="02:05:00", course_type="DE7", bus_stop_id=103, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="02:35:00", course_type="DE7", bus_stop_id=103, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="03:35:00", course_type="DE7", bus_stop_id=103, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="04:35:00", course_type="DE7", bus_stop_id=103, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="23:06:00", course_type="DE7", bus_stop_id=104, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="23:36:00", course_type="DE7", bus_stop_id=104, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="00:06:00", course_type="DE7", bus_stop_id=104, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="00:36:00", course_type="DE7", bus_stop_id=104, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="01:06:00", course_type="DE7", bus_stop_id=104, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="01:36:00", course_type="DE7", bus_stop_id=104, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="02:06:00", course_type="DE7", bus_stop_id=104, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="02:36:00", course_type="DE7", bus_stop_id=104, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="03:36:00", course_type="DE7", bus_stop_id=104, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="04:36:00", course_type="DE7", bus_stop_id=104, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="23:08:00", course_type="DE7", bus_stop_id=105, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="23:38:00", course_type="DE7", bus_stop_id=105, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="00:08:00", course_type="DE7", bus_stop_id=105, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="00:38:00", course_type="DE7", bus_stop_id=105, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="01:08:00", course_type="DE7", bus_stop_id=105, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="01:38:00", course_type="DE7", bus_stop_id=105, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="02:08:00", course_type="DE7", bus_stop_id=105, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="02:38:00", course_type="DE7", bus_stop_id=105, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="03:38:00", course_type="DE7", bus_stop_id=105, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="04:38:00", course_type="DE7", bus_stop_id=105, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="23:09:00", course_type="DE7", bus_stop_id=106, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="23:39:00", course_type="DE7", bus_stop_id=106, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="00:09:00", course_type="DE7", bus_stop_id=106, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="00:39:00", course_type="DE7", bus_stop_id=106, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="01:09:00", course_type="DE7", bus_stop_id=106, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="01:39:00", course_type="DE7", bus_stop_id=106, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="02:09:00", course_type="DE7", bus_stop_id=106, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="02:39:00", course_type="DE7", bus_stop_id=106, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="03:39:00", course_type="DE7", bus_stop_id=106, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="04:39:00", course_type="DE7", bus_stop_id=106, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="23:10:00", course_type="DE7", bus_stop_id=107, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="23:40:00", course_type="DE7", bus_stop_id=107, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="00:10:00", course_type="DE7", bus_stop_id=107, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="00:40:00", course_type="DE7", bus_stop_id=107, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="01:10:00", course_type="DE7", bus_stop_id=107, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="01:40:00", course_type="DE7", bus_stop_id=107, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="02:10:00", course_type="DE7", bus_stop_id=107, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="02:40:00", course_type="DE7", bus_stop_id=107, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="03:40:00", course_type="DE7", bus_stop_id=107, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="04:40:00", course_type="DE7", bus_stop_id=107, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="23:11:00", course_type="DE7", bus_stop_id=108, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="23:41:00", course_type="DE7", bus_stop_id=108, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="00:11:00", course_type="DE7", bus_stop_id=108, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="00:41:00", course_type="DE7", bus_stop_id=108, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="01:11:00", course_type="DE7", bus_stop_id=108, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="01:41:00", course_type="DE7", bus_stop_id=108, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="02:11:00", course_type="DE7", bus_stop_id=108, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="02:41:00", course_type="DE7", bus_stop_id=108, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="03:41:00", course_type="DE7", bus_stop_id=108, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="04:41:00", course_type="DE7", bus_stop_id=108, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="23:12:00", course_type="DE7", bus_stop_id=109, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="23:42:00", course_type="DE7", bus_stop_id=109, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="00:12:00", course_type="DE7", bus_stop_id=109, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="00:42:00", course_type="DE7", bus_stop_id=109, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="01:12:00", course_type="DE7", bus_stop_id=109, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="01:42:00", course_type="DE7", bus_stop_id=109, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="02:12:00", course_type="DE7", bus_stop_id=109, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="02:42:00", course_type="DE7", bus_stop_id=109, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="03:42:00", course_type="DE7", bus_stop_id=109, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="04:42:00", course_type="DE7", bus_stop_id=109, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="23:13:00", course_type="DE7", bus_stop_id=110, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="23:43:00", course_type="DE7", bus_stop_id=110, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="00:13:00", course_type="DE7", bus_stop_id=110, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="00:43:00", course_type="DE7", bus_stop_id=110, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="01:13:00", course_type="DE7", bus_stop_id=110, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="01:43:00", course_type="DE7", bus_stop_id=110, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="02:13:00", course_type="DE7", bus_stop_id=110, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="02:43:00", course_type="DE7", bus_stop_id=110, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="03:43:00", course_type="DE7", bus_stop_id=110, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="04:43:00", course_type="DE7", bus_stop_id=110, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="23:14:00", course_type="DE7", bus_stop_id=111, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="23:44:00", course_type="DE7", bus_stop_id=111, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="00:14:00", course_type="DE7", bus_stop_id=111, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="00:44:00", course_type="DE7", bus_stop_id=111, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="01:14:00", course_type="DE7", bus_stop_id=111, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="01:44:00", course_type="DE7", bus_stop_id=111, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="02:14:00", course_type="DE7", bus_stop_id=111, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="02:44:00", course_type="DE7", bus_stop_id=111, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="03:44:00", course_type="DE7", bus_stop_id=111, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="04:44:00", course_type="DE7", bus_stop_id=111, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="23:15:00", course_type="DE7", bus_stop_id=112, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="23:45:00", course_type="DE7", bus_stop_id=112, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="00:15:00", course_type="DE7", bus_stop_id=112, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="00:45:00", course_type="DE7", bus_stop_id=112, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="01:15:00", course_type="DE7", bus_stop_id=112, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="01:45:00", course_type="DE7", bus_stop_id=112, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="02:15:00", course_type="DE7", bus_stop_id=112, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="02:45:00", course_type="DE7", bus_stop_id=112, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="03:45:00", course_type="DE7", bus_stop_id=112, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="04:45:00", course_type="DE7", bus_stop_id=112, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="23:16:00", course_type="DE7", bus_stop_id=113, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="23:46:00", course_type="DE7", bus_stop_id=113, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="00:16:00", course_type="DE7", bus_stop_id=113, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="00:46:00", course_type="DE7", bus_stop_id=113, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="01:16:00", course_type="DE7", bus_stop_id=113, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="01:46:00", course_type="DE7", bus_stop_id=113, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="02:16:00", course_type="DE7", bus_stop_id=113, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="02:46:00", course_type="DE7", bus_stop_id=113, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="03:46:00", course_type="DE7", bus_stop_id=113, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="04:46:00", course_type="DE7", bus_stop_id=113, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="23:18:00", course_type="DE7", bus_stop_id=114, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="23:48:00", course_type="DE7", bus_stop_id=114, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="00:18:00", course_type="DE7", bus_stop_id=114, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="00:48:00", course_type="DE7", bus_stop_id=114, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="01:18:00", course_type="DE7", bus_stop_id=114, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="01:48:00", course_type="DE7", bus_stop_id=114, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="02:18:00", course_type="DE7", bus_stop_id=114, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="02:48:00", course_type="DE7", bus_stop_id=114, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="03:48:00", course_type="DE7", bus_stop_id=114, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="04:48:00", course_type="DE7", bus_stop_id=114, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="23:19:00", course_type="DE7", bus_stop_id=115, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="23:49:00", course_type="DE7", bus_stop_id=115, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="00:19:00", course_type="DE7", bus_stop_id=115, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="00:49:00", course_type="DE7", bus_stop_id=115, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="01:19:00", course_type="DE7", bus_stop_id=115, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="01:49:00", course_type="DE7", bus_stop_id=115, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="02:19:00", course_type="DE7", bus_stop_id=115, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="02:49:00", course_type="DE7", bus_stop_id=115, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="03:49:00", course_type="DE7", bus_stop_id=115, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="04:49:00", course_type="DE7", bus_stop_id=115, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="23:20:00", course_type="DE7", bus_stop_id=116, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="23:50:00", course_type="DE7", bus_stop_id=116, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="00:20:00", course_type="DE7", bus_stop_id=116, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="00:50:00", course_type="DE7", bus_stop_id=116, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="01:20:00", course_type="DE7", bus_stop_id=116, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="01:50:00", course_type="DE7", bus_stop_id=116, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="02:20:00", course_type="DE7", bus_stop_id=116, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="02:50:00", course_type="DE7", bus_stop_id=116, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="03:50:00", course_type="DE7", bus_stop_id=116, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="04:50:00", course_type="DE7", bus_stop_id=116, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="23:21:00", course_type="DE7", bus_stop_id=117, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="23:51:00", course_type="DE7", bus_stop_id=117, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="00:21:00", course_type="DE7", bus_stop_id=117, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="00:51:00", course_type="DE7", bus_stop_id=117, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="01:21:00", course_type="DE7", bus_stop_id=117, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="01:51:00", course_type="DE7", bus_stop_id=117, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="02:21:00", course_type="DE7", bus_stop_id=117, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="02:51:00", course_type="DE7", bus_stop_id=117, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="03:51:00", course_type="DE7", bus_stop_id=117, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="04:51:00", course_type="DE7", bus_stop_id=117, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="23:22:00", course_type="DE7", bus_stop_id=118, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="23:52:00", course_type="DE7", bus_stop_id=118, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="00:22:00", course_type="DE7", bus_stop_id=118, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="00:52:00", course_type="DE7", bus_stop_id=118, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="01:22:00", course_type="DE7", bus_stop_id=118, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="01:52:00", course_type="DE7", bus_stop_id=118, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="02:22:00", course_type="DE7", bus_stop_id=118, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="02:52:00", course_type="DE7", bus_stop_id=118, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="03:52:00", course_type="DE7", bus_stop_id=118, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="04:52:00", course_type="DE7", bus_stop_id=118, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="23:23:00", course_type="DE7", bus_stop_id=119, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="23:53:00", course_type="DE7", bus_stop_id=119, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="00:23:00", course_type="DE7", bus_stop_id=119, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="00:53:00", course_type="DE7", bus_stop_id=119, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="01:23:00", course_type="DE7", bus_stop_id=119, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="01:53:00", course_type="DE7", bus_stop_id=119, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="02:23:00", course_type="DE7", bus_stop_id=119, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="02:53:00", course_type="DE7", bus_stop_id=119, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="03:53:00", course_type="DE7", bus_stop_id=119, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="04:53:00", course_type="DE7", bus_stop_id=119, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="01:48:00", course_type="DE7", bus_stop_id=2, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="03:48:00", course_type="DE7", bus_stop_id=2, carrier_id=2, direction_id=1, line_id=2).save()
    Course(departure="05:57:00", course_type="D", bus_stop_id=11, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="06:57:00", course_type="D", bus_stop_id=11, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="07:57:00", course_type="D", bus_stop_id=11, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="09:17:00", course_type="D", bus_stop_id=11, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="12:37:00", course_type="D", bus_stop_id=11, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="14:42:00", course_type="D", bus_stop_id=11, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="15:57:00", course_type="D", bus_stop_id=11, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="16:57:00", course_type="D", bus_stop_id=11, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="18:01:00", course_type="D", bus_stop_id=11, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="19:01:00", course_type="D", bus_stop_id=11, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="11:36:00", course_type="E", bus_stop_id=11, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="14:06:00", course_type="E", bus_stop_id=11, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="17:16:00", course_type="E", bus_stop_id=11, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="11:36:00", course_type="E7", bus_stop_id=11, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="14:06:00", course_type="E7", bus_stop_id=11, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="17:16:00", course_type="E7", bus_stop_id=11, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="05:57:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=11,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="06:57:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=11,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="07:57:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=11,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="09:17:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=11,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="12:37:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=11,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="14:42:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=11,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="15:57:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=11,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="16:57:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=11,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="18:01:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=11,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="19:01:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=11,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="05:58:00", course_type="D", bus_stop_id=35, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="06:58:00", course_type="D", bus_stop_id=35, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="07:58:00", course_type="D", bus_stop_id=35, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="09:18:00", course_type="D", bus_stop_id=35, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="12:38:00", course_type="D", bus_stop_id=35, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="14:43:00", course_type="D", bus_stop_id=35, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="15:58:00", course_type="D", bus_stop_id=35, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="16:58:00", course_type="D", bus_stop_id=35, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="18:02:00", course_type="D", bus_stop_id=35, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="19:02:00", course_type="D", bus_stop_id=35, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="11:37:00", course_type="E", bus_stop_id=35, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="14:07:00", course_type="E", bus_stop_id=35, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="17:17:00", course_type="E", bus_stop_id=35, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="11:37:00", course_type="E7", bus_stop_id=35, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="14:07:00", course_type="E7", bus_stop_id=35, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="17:17:00", course_type="E7", bus_stop_id=35, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="05:58:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=35,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="06:58:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=35,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="07:58:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=35,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="09:18:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=35,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="12:38:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=35,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="14:43:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=35,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="15:58:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=35,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="16:58:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=35,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="18:02:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=35,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="19:02:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=35,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="06:00:00", course_type="D", bus_stop_id=5, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="07:00:00", course_type="D", bus_stop_id=5, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="08:00:00", course_type="D", bus_stop_id=5, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="09:20:00", course_type="D", bus_stop_id=5, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="12:40:00", course_type="D", bus_stop_id=5, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="14:45:00", course_type="D", bus_stop_id=5, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="16:00:00", course_type="D", bus_stop_id=5, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="17:00:00", course_type="D", bus_stop_id=5, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="18:04:00", course_type="D", bus_stop_id=5, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="19:04:00", course_type="D", bus_stop_id=5, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="11:39:00", course_type="E", bus_stop_id=5, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="14:09:00", course_type="E", bus_stop_id=5, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="17:19:00", course_type="E", bus_stop_id=5, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="11:39:00", course_type="E7", bus_stop_id=5, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="14:09:00", course_type="E7", bus_stop_id=5, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="17:19:00", course_type="E7", bus_stop_id=5, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="06:00:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=5,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="07:00:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=5,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="08:00:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=5,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="09:20:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=5,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="12:40:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=5,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="14:45:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=5,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="16:00:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=5,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="17:00:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=5,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="18:04:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=5,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="19:04:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=5,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="06:02:00", course_type="D", bus_stop_id=7, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="07:02:00", course_type="D", bus_stop_id=7, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="08:02:00", course_type="D", bus_stop_id=7, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="09:22:00", course_type="D", bus_stop_id=7, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="12:42:00", course_type="D", bus_stop_id=7, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="14:47:00", course_type="D", bus_stop_id=7, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="16:02:00", course_type="D", bus_stop_id=7, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="17:02:00", course_type="D", bus_stop_id=7, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="18:06:00", course_type="D", bus_stop_id=7, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="19:06:00", course_type="D", bus_stop_id=7, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="11:41:00", course_type="E", bus_stop_id=7, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="14:11:00", course_type="E", bus_stop_id=7, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="17:21:00", course_type="E", bus_stop_id=7, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="11:41:00", course_type="E7", bus_stop_id=7, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="14:11:00", course_type="E7", bus_stop_id=7, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="17:20:00", course_type="E7", bus_stop_id=7, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="06:01:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=7,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="07:02:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=7,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="08:02:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=7,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="09:22:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=7,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="12:42:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=7,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="14:47:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=7,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="16:02:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=7,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="17:02:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=7,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="18:06:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=7,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="19:06:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=7,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="06:03:00", course_type="D", bus_stop_id=26, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="07:03:00", course_type="D", bus_stop_id=26, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="08:03:00", course_type="D", bus_stop_id=26, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="09:23:00", course_type="D", bus_stop_id=26, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="12:43:00", course_type="D", bus_stop_id=26, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="14:48:00", course_type="D", bus_stop_id=26, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="16:03:00", course_type="D", bus_stop_id=26, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="17:03:00", course_type="D", bus_stop_id=26, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="18:07:00", course_type="D", bus_stop_id=26, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="19:07:00", course_type="D", bus_stop_id=26, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="11:42:00", course_type="E", bus_stop_id=26, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="14:12:00", course_type="E", bus_stop_id=26, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="17:22:00", course_type="E", bus_stop_id=26, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="11:42:00", course_type="E7", bus_stop_id=26, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="14:12:00", course_type="E7", bus_stop_id=26, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="17:21:00", course_type="E7", bus_stop_id=26, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="06:02:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=26,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="07:03:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=26,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="08:03:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=26,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="09:23:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=26,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="12:43:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=26,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="14:48:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=26,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="16:03:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=26,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="17:03:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=26,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="18:07:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=26,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="19:07:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=26,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="06:04:00", course_type="D", bus_stop_id=28, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="07:04:00", course_type="D", bus_stop_id=28, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="08:04:00", course_type="D", bus_stop_id=28, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="09:24:00", course_type="D", bus_stop_id=28, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="12:44:00", course_type="D", bus_stop_id=28, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="14:49:00", course_type="D", bus_stop_id=28, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="16:04:00", course_type="D", bus_stop_id=28, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="17:04:00", course_type="D", bus_stop_id=28, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="18:08:00", course_type="D", bus_stop_id=28, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="19:08:00", course_type="D", bus_stop_id=28, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="11:43:00", course_type="E", bus_stop_id=28, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="14:13:00", course_type="E", bus_stop_id=28, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="17:23:00", course_type="E", bus_stop_id=28, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="11:43:00", course_type="E7", bus_stop_id=28, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="14:13:00", course_type="E7", bus_stop_id=28, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="17:22:00", course_type="E7", bus_stop_id=28, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="06:03:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=28,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="07:04:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=28,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="08:04:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=28,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="09:24:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=28,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="12:44:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=28,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="14:49:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=28,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="16:04:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=28,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="17:04:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=28,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="18:08:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=28,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="19:08:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=28,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="06:06:00", course_type="D", bus_stop_id=62, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="07:06:00", course_type="D", bus_stop_id=62, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="08:06:00", course_type="D", bus_stop_id=62, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="09:26:00", course_type="D", bus_stop_id=62, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="12:46:00", course_type="D", bus_stop_id=62, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="14:51:00", course_type="D", bus_stop_id=62, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="16:06:00", course_type="D", bus_stop_id=62, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="17:06:00", course_type="D", bus_stop_id=62, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="18:10:00", course_type="D", bus_stop_id=62, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="19:10:00", course_type="D", bus_stop_id=62, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="11:45:00", course_type="E", bus_stop_id=62, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="14:15:00", course_type="E", bus_stop_id=62, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="17:25:00", course_type="E", bus_stop_id=62, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="11:45:00", course_type="E7", bus_stop_id=62, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="14:15:00", course_type="E7", bus_stop_id=62, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="17:24:00", course_type="E7", bus_stop_id=62, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="06:05:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=62,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="07:06:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=62,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="08:06:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=62,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="09:26:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=62,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="12:46:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=62,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="14:51:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=62,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="16:06:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=62,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="17:06:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=62,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="18:10:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=62,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="19:10:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=62,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="06:17:00", course_type="D", bus_stop_id=68, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="07:18:00", course_type="D", bus_stop_id=68, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="08:18:00", course_type="D", bus_stop_id=68, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="09:38:00", course_type="D", bus_stop_id=68, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="12:58:00", course_type="D", bus_stop_id=68, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="15:03:00", course_type="D", bus_stop_id=68, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="16:18:00", course_type="D", bus_stop_id=68, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="17:18:00", course_type="D", bus_stop_id=68, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="18:21:00", course_type="D", bus_stop_id=68, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="19:21:00", course_type="D", bus_stop_id=68, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="11:56:00", course_type="E", bus_stop_id=68, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="14:26:00", course_type="E", bus_stop_id=68, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="17:36:00", course_type="E", bus_stop_id=68, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="11:56:00", course_type="E7", bus_stop_id=68, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="14:26:00", course_type="E7", bus_stop_id=68, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="17:35:00", course_type="E7", bus_stop_id=68, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="06:16:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=68,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="07:18:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=68,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="08:18:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=68,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="09:38:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=68,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="12:58:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=68,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="15:03:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=68,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="16:18:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=68,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="17:18:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=68,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="18:21:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=68,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="19:21:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=68,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="06:19:00", course_type="D", bus_stop_id=70, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="07:21:00", course_type="D", bus_stop_id=70, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="08:21:00", course_type="D", bus_stop_id=70, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="09:41:00", course_type="D", bus_stop_id=70, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="13:01:00", course_type="D", bus_stop_id=70, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="15:06:00", course_type="D", bus_stop_id=70, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="16:21:00", course_type="D", bus_stop_id=70, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="17:21:00", course_type="D", bus_stop_id=70, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="18:23:00", course_type="D", bus_stop_id=70, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="19:23:00", course_type="D", bus_stop_id=70, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="11:58:00", course_type="E", bus_stop_id=70, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="14:28:00", course_type="E", bus_stop_id=70, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="17:38:00", course_type="E", bus_stop_id=70, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="11:58:00", course_type="E7", bus_stop_id=70, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="14:28:00", course_type="E7", bus_stop_id=70, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="17:37:00", course_type="E7", bus_stop_id=70, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="06:18:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=70,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="07:21:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=70,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="08:21:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=70,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="09:41:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=70,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="13:01:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=70,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="15:06:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=70,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="16:21:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=70,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="17:21:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=70,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="18:23:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=70,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="19:23:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=70,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="06:21:00", course_type="D", bus_stop_id=71, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="07:23:00", course_type="D", bus_stop_id=71, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="08:23:00", course_type="D", bus_stop_id=71, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="09:43:00", course_type="D", bus_stop_id=71, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="13:03:00", course_type="D", bus_stop_id=71, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="15:08:00", course_type="D", bus_stop_id=71, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="16:23:00", course_type="D", bus_stop_id=71, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="17:23:00", course_type="D", bus_stop_id=71, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="18:25:00", course_type="D", bus_stop_id=71, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="19:25:00", course_type="D", bus_stop_id=71, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="12:00:00", course_type="E", bus_stop_id=71, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="14:30:00", course_type="E", bus_stop_id=71, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="17:40:00", course_type="E", bus_stop_id=71, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="12:00:00", course_type="E7", bus_stop_id=71, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="14:30:00", course_type="E7", bus_stop_id=71, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="17:39:00", course_type="E7", bus_stop_id=71, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="06:20:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=71,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="07:23:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=71,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="08:23:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=71,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="09:43:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=71,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="13:03:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=71,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="15:08:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=71,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="16:23:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=71,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="17:23:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=71,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="18:25:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=71,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="19:25:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=71,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="06:27:00", course_type="D", bus_stop_id=72, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="07:29:00", course_type="D", bus_stop_id=72, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="08:29:00", course_type="D", bus_stop_id=72, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="09:49:00", course_type="D", bus_stop_id=72, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="13:09:00", course_type="D", bus_stop_id=72, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="15:14:00", course_type="D", bus_stop_id=72, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="16:29:00", course_type="D", bus_stop_id=72, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="17:27:00", course_type="D", bus_stop_id=72, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="18:29:00", course_type="D", bus_stop_id=72, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="19:29:00", course_type="D", bus_stop_id=72, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="12:04:00", course_type="E", bus_stop_id=72, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="14:34:00", course_type="E", bus_stop_id=72, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="17:44:00", course_type="E", bus_stop_id=72, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="12:04:00", course_type="E7", bus_stop_id=72, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="14:34:00", course_type="E7", bus_stop_id=72, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="17:43:00", course_type="E7", bus_stop_id=72, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="06:26:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=72,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="07:29:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=72,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="08:29:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=72,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="09:48:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=72,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="13:08:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=72,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="15:14:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=72,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="16:29:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=72,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="17:27:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=72,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="18:29:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=72,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="19:29:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=72,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="06:29:00", course_type="D", bus_stop_id=73, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="07:32:00", course_type="D", bus_stop_id=73, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="08:32:00", course_type="D", bus_stop_id=73, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="09:51:00", course_type="D", bus_stop_id=73, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="13:11:00", course_type="D", bus_stop_id=73, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="15:16:00", course_type="D", bus_stop_id=73, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="16:31:00", course_type="D", bus_stop_id=73, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="17:30:00", course_type="D", bus_stop_id=73, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="18:31:00", course_type="D", bus_stop_id=73, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="19:31:00", course_type="D", bus_stop_id=73, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="12:06:00", course_type="E", bus_stop_id=73, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="14:36:00", course_type="E", bus_stop_id=73, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="17:46:00", course_type="E", bus_stop_id=73, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="12:06:00", course_type="E7", bus_stop_id=73, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="14:36:00", course_type="E7", bus_stop_id=73, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="17:45:00", course_type="E7", bus_stop_id=73, carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="06:28:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=73,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="07:32:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=73,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="08:32:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=73,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="09:50:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=73,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="13:10:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=73,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="15:16:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=73,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="16:31:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=73,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="17:30:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=73,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="18:31:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=73,
           carrier_id=2, direction_id=1, line_id=4).save()
    Course(departure="19:31:00", course_type="DZIEŃ SPECJALNY: 29, 30 KWIETNIA i 2 MAJA 2019", bus_stop_id=73,
           carrier_id=2, direction_id=1, line_id=4).save()


