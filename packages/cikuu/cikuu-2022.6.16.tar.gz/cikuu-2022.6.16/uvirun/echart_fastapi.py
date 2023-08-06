#2022.7.24  https://gallery.pyecharts.org/#/Pie/doughnut_chart
from uvirun import *

@app.get('/echart/bar', tags=["echart"], response_class=HTMLResponse)
def echart_bar(xdata:str="衬衫,羊毛衫,雪纺衫,裤子,高跟鞋,袜子", ydata:str="商家A,5,20,36,10,75,90|商家B,5,20,36,10,75,95", width:int=600, height:int=600,title="", subtitle=""):
	''' 柱状图， assure 数组长度相同  '''
	import pyecharts.options as opts
	from pyecharts.charts import Bar
	bar = Bar(init_opts=opts.InitOpts(width=f"{width}px", height=f"{height}px")) #theme=ThemeType.LIGHT
	bar.add_xaxis(xdata.split(','))
	for y in ydata.strip().split("|"): #	values = json.loads(ydata) 
		arr = y.strip().split(',') 
		bar.add_yaxis(arr[0], [ float(f) for f in arr[1:] ]) #bar.add_yaxis("商家B", [5, 20, 36, 10, 75, 95])
	bar.set_global_opts(title_opts=opts.TitleOpts(title=title, subtitle=subtitle))
	return HTMLResponse(content=bar.render_embed() ) #bar.render()

@app.get('/echart/sibar', tags=["echart"], response_class=HTMLResponse)
def echart_sibar(si:str='[["gzjc", 2704.8349], ["clec", 3810.3077], ["dic", 3863.9423]]', width:int=600, height:int=600,title="", subtitle=""):
	''' [['gzjc', 2704.8349], ['clec', 3810.3077], ['dic', 3863.9423]] '''
	import pyecharts.options as opts
	from pyecharts.charts import Bar
	bar = Bar(init_opts=opts.InitOpts(width=f"{width}px", height=f"{height}px")) #theme=ThemeType.LIGHT
	si  = json.loads(si) 
	bar.add_xaxis([s for s,i in si])
	bar.add_yaxis('', [i for s,i in si])
	bar.set_global_opts(title_opts=opts.TitleOpts(title=title, subtitle=subtitle))
	return HTMLResponse(content=bar.render_embed() )

@app.get('/echart/hbar', tags=["echart"], response_class=HTMLResponse)
def echart_hbar(xdata:str="衬衫,羊毛衫,雪纺衫,裤子,高跟鞋,袜子", ydata:str="5, 20, 36, 10, 75, 90", title:str="", width:int=600, height:int=600):
	''' https://gallery.pyecharts.org/#/PictorialBar/pictorialbar_base '''
	from pyecharts import options as opts
	from pyecharts.charts import PictorialBar
	from pyecharts.globals import SymbolType

	bar = PictorialBar(init_opts=opts.InitOpts(width=f"{width}px", height=f"{height}px")) 
	bar.add_xaxis(xdata.split(','))
	bar.add_yaxis(
        "",
        [float(v) for v in ydata.split(',')],
        label_opts=opts.LabelOpts(is_show=False),
        symbol_size=18,
        symbol_repeat="fixed",
        symbol_offset=[0, 0],
        is_symbol_clip=True,
        symbol=SymbolType.ROUND_RECT,)
	bar.reversal_axis()
	bar.set_global_opts(
        title_opts=opts.TitleOpts(title=title),
        xaxis_opts=opts.AxisOpts(is_show=False),
        yaxis_opts=opts.AxisOpts(
            axistick_opts=opts.AxisTickOpts(is_show=False),
            axisline_opts=opts.AxisLineOpts(
                linestyle_opts=opts.LineStyleOpts(opacity=0)
            ),
        ),
    )
	return HTMLResponse(content=bar.render_embed() )

@app.get('/echart/donut', tags=["echart"], response_class=HTMLResponse)
def echart_donut(xdata:str="衬衫,羊毛衫,雪纺衫,裤子,高跟鞋,袜子", ydata:str="5, 20, 36, 10, 75, 90", title:str="", width:int=600, height:int=600):
	''' '''
	import pyecharts.options as opts
	from pyecharts.charts import Pie
	p = Pie(init_opts=opts.InitOpts(width=f"{width}px", height=f"{height}px"))
	p.add(series_name=title,
        data_pair=[list(z) for z in zip(xdata.split(','), [float(y) for y in ydata.strip().split(',')])],
        radius=["50%", "70%"],
        label_opts=opts.LabelOpts(is_show=False, position="center"),    )
	p.set_global_opts(legend_opts=opts.LegendOpts(pos_left="legft", orient="vertical"))
	p.set_series_opts(tooltip_opts=opts.TooltipOpts(trigger="item", formatter="{a} <br/>{b}: {c} ({d}%)"),)
	return HTMLResponse(content=p.render_embed() )

@app.get('/echart/gauge', tags=["echart"], response_class=HTMLResponse)
def echart_gauge(x:str="完成率", y:float=66.6, title:str="gauge", width:int=600, height:int=600):
	''' https://gallery.pyecharts.org/#/Gauge/gauge_base '''
	import pyecharts.options as opts
	from pyecharts.charts import Gauge
	g = Gauge(init_opts=opts.InitOpts(width=f"{width}px", height=f"{height}px"))
	g.add("", [(x, y)])
	g.set_global_opts(title_opts=opts.TitleOpts(title=title))
	return HTMLResponse(content=g.render_embed() )

@app.get('/echart/wordcloud', tags=["echart"], response_class=HTMLResponse)
def echart_wordcloud(labels:str="衬衫,羊毛衫,雪纺衫,裤子,高跟鞋,袜子", values:str="5,20,36,10,75,90",title:str="", width:int=600, height:int=600):
	''' '''
	import pyecharts.options as opts
	from pyecharts.charts import WordCloud
	html = WordCloud(init_opts=opts.InitOpts(width=f"{width}px", height=f"{height}px")).add(series_name=title, data_pair=[ (s, float(i)) for s,i in zip(labels.strip().split(','), values.strip().split(','))]
		, word_size_range=[6, 66]).set_global_opts( title_opts=opts.TitleOpts(title=title, title_textstyle_opts=opts.TextStyleOpts(font_size=23)),
        tooltip_opts=opts.TooltipOpts(is_show=True),
    ).render_embed()	
	return HTMLResponse(content=html )

if __name__ == '__main__':
	print (echart_sibar(), flush=True)
	uvicorn.run(app, host='0.0.0.0', port=80)

# <script type="text/javascript" src="https://assets.pyecharts.org/assets/echarts.min.js"></script>