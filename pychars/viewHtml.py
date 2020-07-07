from django.http import HttpResponse
from pygal.style import Style
from django.shortcuts import render
import json, logging
import pygal
from pychars.views import get_base64
from wordcloud import WordCloud
import graphviz as gz

DEFAULT_TYPE = ['bar', 'line', 'pie', 'radar', 'dot', 'HBar','WordCloud','graph']


def get_photo_html(request):
    global b64, custom_style, other
    if request.method == 'GET':
        return render(request, "index.html")
    tp = request.POST.get("t")
    settings = json.loads(request.POST.get("settings"))
    data = json.loads(request.POST.get("data"))
    if tp not in DEFAULT_TYPE:
        return render(request, "index.html")
    if 'style' in settings.keys():
        custom_style = Style(**settings['style'])

    else:
        custom_style = Style(font_family='Microsoft YaHei',
                             label_font_size=20,
                             major_label_font_size=20,
                             value_font_size=26,
                             value_label_font_size=20,
                             tooltip_font_size=20,
                             title_font_size=30,
                             legend_font_size=20)
    default_other = {'fill': True, 'legend_at_bottom': True, 'print_values': True, 'show_legend': True}
    if 'others' in settings.keys():
        other = {**default_other, **settings['others']}
    else:
        other = default_other
    try:
        if tp == 'bar':
            bar_chart = pygal.Bar(title=settings['title'], width=settings['width'], height=settings['height'],
                                  **other, style=custom_style)
            bar_chart.title = settings['title']
            bar_chart.x_labels = data['labels']
            for k, v in data['data'].items():
                bar_chart.add(k, v)
            bar_chart.render_to_png("png/bar.png")
            b64 = get_base64("png/bar.png")
        elif tp == 'line':
            line_chart = pygal.Line(title=settings['title'], width=settings['width'], height=settings['height']
                                    , **other, style=custom_style)
            line_chart.title = settings['title']
            line_chart.x_labels = data['labels']
            for k, v in data['data'].items():
                line_chart.add(k, v)
            line_chart.render_to_png("png/line.png")
            b64 = get_base64("png/line.png")
        elif tp == 'pie':
            pie_chart = pygal.Pie(title=settings['title'], width=settings['width'], height=settings['height']
                                  , **other, style=custom_style)
            pie_chart.title = settings['title']
            for k, v in data['data'].items():
                pie_chart.add(k, v)
            pie_chart.render_to_png("png/pie.png")
            b64 = get_base64("png/pie.png")
        elif tp == 'radar':
            show_legend = False
            if len(data["data"].items()) > 1:
                show_legend = True
            radar_chart = pygal.Radar(title=settings['title'], width=settings['width'], height=settings['height'],
                                      **other, style=custom_style)
            radar_chart.title = settings['title']
            radar_chart.x_labels = data['labels']
            for k, v in data['data'].items():
                radar_chart.add(k, v)
            radar_chart.render_to_png("png/radar.png")
            b64 = get_base64("png/radar.png")
        elif tp == 'HBar':
            h_bar_chart = pygal.HorizontalBar(title=settings['title'], width=settings['width'],
                                              height=settings['height'],
                                              **other, style=custom_style)
            h_bar_chart.title = settings['title']
            # h_bar_chart.x_labels = data['data'].keys()
            for k, v in data['data'].items():
                h_bar_chart.add(k, v)
            h_bar_chart.render_to_png("png/h_bar.png")
            b64 = get_base64("png/h_bar.png")
        elif tp == 'dot':
            dot_chart = pygal.Dot(title=settings['title'], width=settings['width'], height=settings['height']
                                  , **other, style=custom_style)
            dot_chart.title = settings['title']
            dot_chart.x_labels = data['labels']
            for k, v in data['data'].items():
                dot_chart.add(k, v)
            dot_chart.render_to_png("png/dot.png")
            b64 = get_base64("png/dot.png")
        elif tp == 'WordCloud':
            style = settings["style"]
            wc = WordCloud(
                font_path='/Users/donggua/Library/Fonts/msyh.ttf',
                **style
            )

            a = {}
            for word in data['data']:
                name = word["name"]
                a[name] = word["value"]
            wc.generate_from_frequencies(a)
            wc.to_file(r"png/WordCloud.png")
            b64 = get_base64("png/WordCloud.png")
        elif tp == 'graph':
            datas = data["data"]
            data = datas["ControllerData"]["Paths"]
            CompanyName = datas["CompanyName"]
            # print(name1)
            KeyN = datas["KeyNo"]
            dot = gz.Digraph(format="png")
            node = settings.get("node", {})
            node["fontname"] = "Microsoft YaHei"
            edge = settings.get("edge", {})
            graph = settings.get("graph", {})
            dot.attr('node', **node)
            dot.attr('edge', **edge)
            dot.attr('graph', **graph)
            graph_data = set()
            for f in data:
                reverse_data = list(reversed(f))
                for i, re in enumerate(reverse_data):
                    name = re["Name"]
                    Percent = re["Percent"]
                    KeyNo = re["KeyNo"]
                    try:
                        name1 = reverse_data[i + 1]["Name"]
                        KeyNo1 = reverse_data[i + 1]["KeyNo"]
                    except Exception:
                        name1 = CompanyName
                        KeyNo1 = KeyN
                    dot.node(KeyNo, name)
                    dot.node(KeyNo1, name1)
                    graph_data.add(KeyNo + '|' + KeyNo1 + '|' + Percent)
            for i in graph_data:
                data = i.split('|')
                dot.edge(data[0], data[1], data[2])
            dot.render("png/relation")
            b64 = get_base64("png/relation.png")
    except Exception as e:
        logging.error(e)
    return HttpResponse(json.dumps(b64), content_type='application/json')
