import django
django.setup()
from apps.bushelper.custom.graph import Graph
from apps.bushelper.custom.scrapers import FremiksScraper
from apps.bushelper.models import Line, BusStop


def get_fremiks_connections(graph, direction_name):
    f_scrapper = FremiksScraper(Line.objects.get(name__iexact=direction_name).url)
    table = f_scrapper.get_table()
    src, dst = None, None
    for scrapped_bus_stop in table[0][0][1:]:
        if src is not None and dst is not None:
            print(src, dst)
            graph.push_edge(src, dst)
            src = dst
            dst = None
        for query_bus_stop in BusStop.objects.filter(fremiks_alias__isnull=False, direction__direction__iexact=direction_name):
            if str(query_bus_stop.fremiks_alias).lower().replace(' ', '') in scrapped_bus_stop.lower().replace(u'\xa0', u' ').replace(' ', ''):
                if src is None:
                    src = query_bus_stop
                else:
                    dst = query_bus_stop
                break
    if src is not None and dst is not None:
        print(src, dst)
        graph.push_edge(src, dst)
    return graph


if __name__ == '__main__':
    lsw_graph = Graph()
    lbn_graph = Graph()
    lsw_graph = get_fremiks_connections(lsw_graph, 'lbn')
    lbn_graph = get_fremiks_connections(lbn_graph, 'lsw')

