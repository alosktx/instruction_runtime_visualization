## 程序运行指令结束时间可视化
本程序用于对每条指令结束时间进行可视化,将所有指令及其运行时间排列画在一条直线上,直观地反映每条指令执行时间时间之间的差距,从而有针对性地对程序进行优化.
### 一 获取程序命令运行时间
代码所使用的原文件来自于系统xxx验证环境的tarmac记录模块,进入xxx验证环境config目录下打开配置文件tarmac_sw开关,就能在程序跑完后在,对应目录下找到的生成的记录文件trace.simple
### 二 数据可视化
为了直观地反映指令的执行时间,以及各条指令执行的时间差,将上述提取到的log文件,进行可视化作图.使用python的pyecharts库,将指令的结束时间绘制在一条线上,如在同一个cycle执行了多条指令,则将其按照执行顺序由左下向右上分列显示.Echarts是一个由JavaScript实现的开源的数据可视化库,可以流畅的运行在 PC 和移动设备上,具有良好的交互性和精巧的图表设计,而pyechart则通过python代码调用Echarts来实现数据的可视化.pyechart官网地址为[https://pyecharts.org/](https://pyecharts.org/)
#### 数据格式化 
为了保证数据可视化绘制代码的稳定性,将程序命令运行时间的trace.simple文件,提取数据并进行格式化处理,保证绘制代码输入数据的一致性.使用python脚本提取数据到csv表格中,将每条指令的pc值填入第一列,指令执行开始时间填入第二列,指令结束时间填入第三列,指令名称填入第四列.具体代码如下所示:
```py
import csv
def pasing_data(file):
    f=open(file,'r')
    eachlines=f.read().splitlines()
    for i in range(len(eachlines)):
        if('IT'==eachlines[i].split()[2]):
            row=[eachlines[i].split()[4],eachlines[i+1].split()[1].split('-')[0],eachlines[i+1].split()[1].split('-')[1],eachlines[i].split(':')[2]]
            with open('2d.csv', 'a+') as file_handler:
                csv.writer(file_handler).writerow(row)
if __name__ == "__main__":
    file='trace_2d.simple'
    pasing_data(file)
```
#### 作图
作图代码分为两部分,第一部分为函数gen_ary,用来生成画图所需要的组合数据列表,首先是将csv文件的数据的第4列和第3列提取出来,添加为指令列表cmd_list和结束时间列表clk_time_end.如下代码所示:
```py
with open(file,'r') as f:
    eachline=csv.reader(f)
    for num,item in enumerate(eachline):
            if(num>=x and num<=y):
                cmd_list.append(item[3])
                clk_time_end.append(int(item[2]))  
```
再根据不同的指令分类添加不同的颜色代码到颜色列表color_list,将STR类和LDR类操作内存的指令用红色表示;将B类跳转指令用蓝色表示;将MRS和MSR等ARM系列特有指令用黑色表示;将其他指令用绿色表示.以此在图中更直观明显地区分不同类别的指令.具体代码如下所示:
```py
for item in cmd_list:
    if('LDR' == item.split()[0] or 'STR' == item.split()[0]):
        color_list.append("red")
    elif('B'== item.split()[0] or 'B.GT' == item.split()[0]):
        color_list.append("blue")
    elif('MSR'== item.split()[0] or 'MRS'==item.split()[0]):
        color_list.append("black")
    else:
        color_list.append("green")
```
由于一个cycle最多同时会执行4条指令,如果不作处理,这些指令将会在绘制图中重合显示,为了以示区分,添加一个表示各个指令结束时间点相对于位置偏移量的列表offset_list(位置偏移显示,横坐标不变),通过遍历指令列表cmd_list,对于同一时间点结束的四条指令,第二个结束时间点的指令,将其向上偏移400%像素点,向右偏移5个像素点显示;第三个结束时间点的指令,将其向上偏移800%的像素点,向右偏移10个像素点来显示;第四个重合结束时间点的指令,将其向上偏移1200%像素点,向右偏移15个像素点来显示.具体代码如下所示:
```py
for i in range(1,len(clk_time_end)):
    if(clk_time_end[i]==clk_time_end[i-1] and offset_flag==0):
        offset_flag+=1
        offset_list.append([5,'-400%'])
    elif(clk_time_end[i]==clk_time_end[i-1] and offset_flag==1):
        offset_flag+=1
        offset_list.append([10,'-800%'])
    elif(clk_time_end[i]==clk_time_end[i-1] and offset_flag==2):
        offset_flag+=1
        offset_list.append([15,'-1200%'])
    else:
        offset_flag=0
        offset_list.append([0,'-0%'])
```
最后将cmd_list,clk_time_end,color_list,offset_list四个列表,通过pyecharts库的ScatterItem类添加至data_pair列表中,并设置显示为指令首字符.具体代码如下:
```py
for k,v,c,f in zip(cmd_list,clk_time_end,color_list,offset_list): 
    data_pair.append(
        opts.ScatterItem(
            name=k,
            value=v,
            itemstyle_opts=opts.ItemStyleOpts(color=c),
            symbol_offset=f,
            label_opts=opts.LabelOpts(
            position='top', 
            formatter=JsCode(                      
                """function(params){  
                    var t=params.name.indexOf(',');
                    if(-1==t){
                        t=8;
                    }
                    return params.name.substring(0,t-3);                      
                }"""
                ),
            ),
        )
    )
```
第二部分代码是绘图函数draw_chart,接受两个参数,一个是数据参数,用于绘图,另一个是名称参数,用于命名.选定散点图为绘制图,散点图属于直角坐标系图表.必须添加X轴数据和Y轴数据,为了将所有的点都绘制在一条直线上,将只有一个元素的列表设置为X轴的数据,Y轴数据使用上述ScatterItem的data_pair列表;为了更好地与程序运行行为一致,使用reversal_axis()函数将X轴和Y轴的数据进行翻转,从而横向显示.之后就是一些优化显示的配置项,主要是使用DataZoomOpts区域缩放配置项来控制数据的缩放;使用TooltipOpts提示框配置项,来显示鼠标移动可查看完整指令名称的效果;通过AxisOpts坐标轴配置项来配置X轴上的分割,名称等.具体代码如下所示:
```py
def draw_chart(data_pair,str_name) -> Scatter:
    b=[' ']
    c = (
        Scatter(
            init_opts=opts.InitOpts(bg_color='rgba(255,255,255,0.2)',
                                    width='3100px',
                                    height='500px',
                                    theme="white"
                                    ),
        )
        .add_xaxis(b)
        .add_yaxis(
            series_name='s',
            y_axis=data_pair,
        )
        .reversal_axis()
        .set_global_opts(
            title_opts=opts.TitleOpts(title=str_name),
            xaxis_opts=opts.AxisOpts(
                type_="value",
                is_scale=True,
                name_gap=50,
                min_interval=1,
                min_='dataMin',
                name="clk-cycle/次",
                boundary_gap=False,
                split_number=200,
                axisline_opts=opts.AxisLineOpts(
                    is_on_zero=False,
                    symbol=['none', 'arrow'],
                ),
                axistick_opts=opts.AxisTickOpts(
                    is_show=True,
                    is_align_with_label=True,
                ),
                splitline_opts=opts.SplitLineOpts(
                    is_show=True,
                    linestyle_opts=opts.LineStyleOpts(
                    ),
                ),
                axislabel_opts=opts.LabelOpts(
                    is_show=True
                ),
            ),

            tooltip_opts=opts.TooltipOpts(
                formatter=JsCode(                    
                    """function(params){  
                        if ('name' in params) {
                            var s1=params.name+'<br/>';
                        }
                        return s1;
                    }"""
                    ),
            ),

            datazoom_opts=[ 
                opts.DataZoomOpts(
                    is_show=False,
                    type_="inside",
                ),
                opts.DataZoomOpts(
                    is_show=True,
                    type_="slider",
                ),
            ],

            legend_opts=opts.LegendOpts(is_show=False),
        )
        .render('test.html')
    )
```
通过调用此函数生成html文件,使用浏览器打开此html文件即可看到绘制的图表,具体效果如下图所示.
![示例图](./example.png)
此处注意打开此html文件需要联网,因为生成的html文件调用了在线网址[https://assets.pyecharts.org/assets/echarts.min.js]的资源,为了实现离线访问,将js代码下载下来,更改生成的html文件中调用js文件的路径即可.此步骤用python函数sub_char实现,代码具体如下:
```py
def sub_char(str_name):
    f=open(str_name,'r')
    alllines=f.readlines()
    f.close()
    f=open(str_name,'w+')
    for eachline in alllines:
        a=re.sub('https://assets.pyecharts.org/assets/echarts.min.js','echarts.min.js',eachline)
        f.writelines(a)
    f.close()  
```
为了提升网页的利用效率,将两个主要的不同程序数据同时绘制在一个网页里面,方便进行对比.使用组合图表中的page顺序多图,将两张图表顺序显示,只需要在上述绘制函数draw_chart后面加一个返回值,并将其按顺序添加进page.add()的参数列表中即可.具体代码如下所示:
```py
def page_default_layout():
    page = Page()
    page.add(
        bar_datazoom_slider(),
        line_markpoint(),
        pie_rosetype(),
        grid_mutil_yaxis(),
        liquid_data_precision(),
        table_base(),
    )
    page.render("page_default_layout.html")
```
至此指令运行数据的可视化工作已经全部完成.
### 附录
### 程序使用
直接在命令行调用python程序并添加所需要的三个参数即可,file参数表示需要打开的文件,即要进行可视化的文件;start参数表示画图的起始指令的位置,即指令在格式化文件中出现的行数;length表示需要对多少条指令进行可视化.调用代码如下所示,调用之后程序会在当前目录生成一个*.csv的指令格式化文件,一个*.html的指令可视化网页文件,并自动调用firefox浏览器打开此网页绘图,如用户没有安装firefox,也可使用其他浏览器手动打开此网页文件.
```py
python3 test.py -f file -s start -l length
```
### pyecharts库的安装
pip 安装
安装 v1 以上版本
```shell
pip install pyecharts -U
```
如果需要安装 0.5.11 版本的开发者，可以使用
```shell
$ pip install pyecharts==0.5.11
```
源码安装
安装 v1 以上版本
```shell
git clone https://github.com/pyecharts/pyecharts.git
```
如果需要安装 0.5.11 版本，请使用 
```shell
git clone https://github.com/pyecharts/pyecharts.git -b v05x
cd pyecharts
pip install -r requirements.txt
python setup.py install
```