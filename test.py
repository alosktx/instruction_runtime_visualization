import numpy as n
import argparse
from pyecharts import options as opts
from pyecharts.charts import Scatter
from pyecharts.commons.utils import JsCode
from pyecharts.globals import SymbolType
from pyecharts.types import ItemStyle
import csv
import re
import os

def pasing_data(file):
    f=open(file,'r')
    eachlines=f.read().splitlines()
    for i in range(len(eachlines)):
        if('IT'==eachlines[i].split()[2]):
            row=[eachlines[i].split()[4],eachlines[i+1].split()[1].split('-')[0],eachlines[i+1].split()[1].split('-')[1],eachlines[i].split(':')[2]]
            with open(file+'_parsed.csv', 'a+') as file_handler:
                csv.writer(file_handler).writerow(row)

def gen_ary(file,x=13947,y=20093):
    cmd_list=[]
    clk_time_end=[]
    color_list=[]
    data_pair=[]
    offset_list=[[0, '-0%'],]

    with open(file,'r') as f:
        eachline=csv.reader(f)
        for num,item in enumerate(eachline):
                if(num>=x and num<=y):
                    cmd_list.append(item[3])
                    clk_time_end.append(int(item[2]))  
 
    
    for item in cmd_list:
        if('LDR' == item.split()[0] or 'STR' == item.split()[0]):
            color_list.append("red")
        elif(None!=re.match('^B',item.split()[0])):
            color_list.append("blue")
        elif('MSR'== item.split()[0] or 'MRS'==item.split()[0]):
            color_list.append("black")
        else:
            color_list.append("green")

    offset_flag=0
    # offset_list.append[[0, '-10%'],]
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
        
    return cmd_list,clk_time_end,color_list,offset_list,data_pair

def draw_chart(data_pair,str_name) -> Scatter:
    b=[' ']
    c = (
        Scatter(
            init_opts=opts.InitOpts(bg_color='rgba(255,255,255,0.2)',
                                    width='2000px',
                                    height='500px',
                                    theme="white"
                                    ),
        )
        .add_xaxis(b)
        .add_yaxis(
            series_name='s',
            y_axis=data_pair,
            # symbol='pin',
            # xaxis_index=0,
            # symbol_rotate=180,
            # symbol_size=[20,20],
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
                # offset=1000,

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
                # trigger="item",
                # axis_pointer_type="cross",
                formatter=JsCode(                    
                    """function(params){  
                        if ('name' in params) {
                            var s1=params.name+'<br/>';
                        }
                        if ('dataIndex' in params) {
                            var s2=params.dataIndex+'<br/>';
                        }
                        if ('value' in params) {
                            var s3=params.value+'<br/>';
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
        .render(str_name+'.html')
    )
   
    # return c

def sub_char(str_name):
    f=open(str_name,'r')
    alllines=f.readlines()
    f.close()
    f=open(str_name,'w+')
    for eachline in alllines:
        a=re.sub('https://assets.pyecharts.org/assets/echarts.min.js','echarts.min.js',eachline)
        f.writelines(a)
    f.close()    


if __name__ == "__main__":
    my_arg = argparse.ArgumentParser('My argument parser')
    my_arg.add_argument('--file','-f',default='trace.simple',type=str,help='Read file')
    my_arg.add_argument('--start','-s',default=1,type=int,help='Start position index')
    my_arg.add_argument('--length','-l',default=1000,type=int,help='Display length')
    test_args = my_arg.parse_args()

    pasing_data(test_args.file)
    file_parsed=test_args.file+'_parsed.csv'
    file_sub=test_args.file+'.html'
    cmd_list,clk_time_end,color_list,offset_list,data_pair=gen_ary(file_parsed,test_args.start,test_args.start+test_args.length)
    draw_chart(data_pair,test_args.file)

    sub_char(file_sub)
    
    os.system('firefox '+file_sub)

