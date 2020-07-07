from django.http import HttpResponse
from pygal.style import Style
import json, logging
import pygal
import base64,os
from wordcloud import WordCloud
import graphviz as gz

os.system('dot -Tpng png/relation -o png/relation.png')

DEFAULT_TYPE = ['bar', 'line', 'pie', 'radar', 'dot', 'HBar','WordCloud','graph']
DEFAULT_ERROR_LIST = {'ERROR_TYPE': {'code': 'E0001', 'message': '未知的类型'},
                      'ERROR_DATA': {'code': 'E0002'},
                      'SUCCESS': {'code': '00000'},
                      }


def get_base64(file_name):
    with open(file_name, "rb") as f:
        base64_data = base64.b64encode(f.read())
    return bytes.decode(base64_data)


"""

@api {post} /get_photo  
@apiName getPhoto
@apiGroup API
@apiVersion 1.0.1
@apiDescription 传参获取图片的base64

@apiParam {String} t  图片的类型
@apiParam {json} settings  图片的相关配置
@apiParam {String} data  图中展示的数字

@apiParamExample {json} 饼图：
{
	't': 'pie',
	"style": {
		"label_font_size": 20,
		"major_label_font_size": 20,
		"value_font_size": 20,
		"value_label_font_size": 20,
		"legend_font_size": 20
	},
	"other": {
		"fill": "True",
		"show_legend": "True"
	},
	'data': {
		'key1': 10,
		'key2': 20,
		'key3': 30
	}
}

@apiParamExample {json} 雷达图：
{
	't': 'radar',
	"style": {
		"label_font_size": 20,
		"major_label_font_size": 20,
		"value_font_size": 20,
		"value_label_font_size": 20,
		"legend_font_size": 20
	},
	"other": {
		"fill": "True",
		"show_legend": "True"
	},
	'data': {
		'data': {
			'key1': [30, 10, 10, 20, 60, 23],
			'key2': [90, 10, 30, 50, 10, 73],
			'key3': [50, 50, 50, 50, 50, 53]
		},
		'labels': ['工商', '财务', '舆情', '招标', '概要', '测试']
	}
}

@apiParamExample {json} 柱形图：
{
	't': 'bar',
	"style": {
		"label_font_size": 20,
		"major_label_font_size": 20,
		"value_font_size": 20,
		"value_label_font_size": 20,
		"legend_font_size": 20
	},
	"other": {
		"fill": "True",
		"show_legend": "True"
	},
	'data': {
		'data': {
			'key1': [30, 10, 10, 20, 60, 23],
			'key2': [90, 10, 30, 50, 10, 73],
			'key3': [50, 50, 50, 50, 50, 53]
		},
		'labels': ['工商', '财务', '舆情', '招标', '概要', '测试']
	}

}

@apiParamExample {json} 曲线图：
{
	't': 'line',
	"style": {
		"label_font_size": 20,
		"major_label_font_size": 20,
		"value_font_size": 20,
		"value_label_font_size": 20,
		"legend_font_size": 20
	},
	"other": {
		"fill": "True",
		"show_legend": "True"
	},
	'data': {
		'data': {
			'key1': [30, 10, 10, 20, 60, 23],
			'key2': [90, 10, 30, 50, 10, 73],
			'key3': [50, 50, 50, 50, 50, 53]
		},
		'labels': ['工商', '财务', '舆情', '招标', '概要', '测试']
	}
}

@apiParamExample {json} 曲线图：
{
	't': 'dot',
	"style": {
		"label_font_size": 20,
		"major_label_font_size": 20,
		"value_font_size": 20,
		"value_label_font_size": 20,
		"legend_font_size": 20
	},
	"other": {
		"fill": "True",
		"show_legend": "True"
	},
	'data': {
		'data': {
			'2017': [30, 10, 10, 20, 60, 23, 30, 10, 10, 20, 60, 23],
			'2018': [90, 10, 30, 50, 10, 73, 90, 10, 30, 50, 10, 73],
			'2019': [50, 50, 50, 50, 50, 53, 50, 50, 50, 50, 50, 53]
		},
		'labels': ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
	}
}


@apiParamExample {json} 柱形图（水平）：
{
	't': 'HBar',
	"style": {
		"label_font_size": 20,
		"major_label_font_size": 20,
		"value_font_size": 20,
		"value_label_font_size": 20,
		"legend_font_size": 20
	},
	"other": {
		"fill": "True",
		"show_legend": "True"
	},
	'data': {
		'key1': 10,
		'key2': 20,
		'key3': 30
	}
}
"""


def get_photo(request):
    global b64, custom_style, other
    tp = request.POST.get("t")
    settings = json.loads(request.POST.get("settings"))
    data = json.loads(request.POST.get("data"))
    if tp not in DEFAULT_TYPE:
        return HttpResponse(json.dumps(DEFAULT_ERROR_LIST['ERROR_TYPE']),
                            content_type="application/json,charset=utf-8")
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
                                              height=settings['height'], **other, style=custom_style)
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
                font_path='C:\windows\Fonts\simfang.ttf',
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
            graph = settings.get("edge", {})
            dot.attr('node', **node)
            dot.attr('edge', **edge)
            dot.attr('edge', **graph)
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
        else:
            return HttpResponse(json.dumps(DEFAULT_ERROR_LIST['ERROR_TYPE']),
                                content_type="application/json,charset=utf-8")
    except Exception as e:
        logging.error(e)
        error = DEFAULT_ERROR_LIST['ERROR_DATA']
        error['message'] = str(e)
        return HttpResponse(json.dumps(error, ensure_ascii=False), content_type="application/json,charset=utf-8")
    else:
        result = DEFAULT_ERROR_LIST['SUCCESS']
        result['base64'] = b64
        return HttpResponse(json.dumps(result, ensure_ascii=False), content_type="application/json,charset=utf-8")


"""

@api {post} /deploy  
@apiName Deploy
@apiGroup DeployServer
@apiVersion 1.0.0
@apiDescription 关于该项目如何部署的介绍

@apiParamExample {python} 安装组件：

pip install uwsgi #类似web服务器
pip install virtualenv #python的虚拟环境包(可选)


@apiParamExample {python} 测试环境：
#编写测试脚本
def application(env, start_response):
    start_response('200 OK', [('Content-Type','text/html')])
    return ["Hello World"]
#保存为test.py
#运行
uwsgi --http :8000 --wsgi-file test.py

@apiParamExample {json} 编写配置文件：

#编写uwsgi.ini文件。查看服务器文件。
#如使用virtualenv，需进入venv虚拟模式下(source venv/bin/activate) 运行
pip install -r req.txt 
#如不使用在当前模式下运行
pip install -r req.txt
 
@apiParamExample {json} 启动/停止服务：

#启动
uwsgi -i uwsgi.ini
#停止
uwsgi --stop uwsgi.pid

#启动之后查看 
tail -f info.log

@apiParamExample {json} 问题：
#测试web服务器失败可能问题
在wsgi文件中增加sys.path.append('项目绝对路径')。
app没有写入到配置文件。
参数设置错误

@apiParamExample {json} 重点：

在view.py中写路径，是项目的相对路径，不是view.py文件的相对路径
        style="font_family":"Microsoft YaHei"--字体
        "label_font_size":20--坐标字体大小 
        "major_label_font_size":20--轴线主字体大小
        "value_font_size":20--值字体大小
        "value_label_font_size":20--图中名字体大小
        "tooltip_font_size":20--字体大小
        "title_font_size":20--标题字体大小
        "legend_font_size":20--图例字体大小
        other="fill":"True"--是否填充颜色
        "legend_at_bottom":"True"--图例是否显示在底部
        "print_values":"True"--是否显示图中数值
        "show_legend":"True"--是否显示图例
        其他other参考：http://www.pygal.org/en/stable/documentation/configuration/chart.html#options
        其他style参考：http://www.pygal.org/en/stable/documentation/custom_styles.html


"""


def deploy_info():
    pass
