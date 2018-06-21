import math
import json
import pandas as pd
import datetime
import plotly.plotly as py
import numpy as np
import os
import plotly.graph_objs as go
import plotly
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import peakutils
from scipy import integrate
from itertools import cycle

NUMBER_OF_MAGNET_PAIRS = 12
    
def calc_frequency(dataframe, mps):
    dataframe = dataframe.round(0).dropna().astype(int).diff().divide(5).abs()
    return dataframe.rolling(1000).sum().divide(360)*10

def calc_effective(dataframe, mps):
    amount = dataframe.size
    dataframe = dataframe**2
    dataframe = dataframe.rolling(mps).sum().divide(mps).apply(np.sqrt)
    return dataframe

def load_measurements(filename):
    data = pd.read_csv(filename,sep ='\t', header=0, skiprows=4)
    return data
def fix_dots(dataframe):
    return dataframe.str.replace(',', '.').astype(float)
def get_graph(df, x, y, second_y=False, legendgroup=None): 
        if not second_y:
            return go.Scatter(
                x=df[x],
                y=df[y],
                legendgroup=legendgroup,
                line=dict(width=2),
                name=y
                )
        return go.Scatter(
                x=df[x],
                y=df[y],
                yaxis='y2',
                line=dict(width=2),
                name=y
                )
                

def main():
    
    with open('settings.json') as json_file:
        settings = json.load(json_file)
    #btast = im dateinamen
    #airgap = im dateinamen
    time_data = []
    rpm_data = []
    for filename in os.listdir('measurements')[1:]:
        #mps=measurements per second
        #airgap, load, mps = filename.split(".")[0].split('_')
        mps= 10000
        df = load_measurements('messwerte/1406_1625.txt')
        df['time']=pd.to_datetime(df['time'], format='%d.%m.%Y  %H:%M:%S,%f')
        df['frequency_1'] = fix_dots(df['Dev0/Ai6'])
        df['frequency_2'] = fix_dots(df['Dev0/Ai14'])
        df['voltage_1'] = fix_dots(df['Dev0/Ai2'])*settings["voltage"]["AC"]["multiplyer"]
        df['voltage_2'] = fix_dots(df['Dev0/Ai10'])*settings["voltage"]["AC"]["multiplyer"]
        df['voltage_3'] = fix_dots(df['Dev0/Ai3'])*settings["voltage"]["AC"]["multiplyer"]
        df['current_1'] = fix_dots(df['Dev0/Ai0'])*settings["current"]["AC"]["multiplyer"]
        df['current_2'] = fix_dots(df['Dev0/Ai8'])*settings["current"]["AC"]["multiplyer"]
        df['current_3'] = fix_dots(df['Dev0/Ai1'])*settings["current"]["AC"]["multiplyer"]
        df['voltage_dc'] = fix_dots(df['Dev0/Ai11'])*settings["voltage"]["DC"]["multiplyer"]
        df['current_dc'] = fix_dots(df['Dev0/Ai9'])*settings["current"]["DC"]["multiplyer"]
        df['torque'] = fix_dots(df['Dev0/Ai13'])*settings["torque"]["multiplyer"]
        df['eff_volt_1'] = np.nan
        df['eff_volt_2'] = np.nan
        df['eff_volt_3'] = np.nan
        df['eff_volt_dc'] = np.nan
        df['eff_curr_1'] = np.nan
        df['eff_curr_2'] = np.nan
        df['eff_curr_3'] = np.nan
        df['eff_curr_dc'] = np.nan
        df['frequency'] = np.nan
        df['rpm'] = np.nan
        df['input'] = np.nan
        df['output'] = np.nan
        df['efficiency'] = np.nan
        """
        example_data = []
        for i in range (1,4):
            example_data.append(get_graph(df, "time", "current_{}".format(i)))
            example_data.append(get_graph(df, "time", "voltage_{}".format(i)))
        example_plot = plot(example_data, filename='example.html')
        """
        blanks = df[df.isnull().all(1)].index
        gaps = df[df.time.diff()>pd.Timedelta(0.1,'ms')].index
        df_list = np.split(df, np.sort(np.append(blanks,gaps)))
        new_df = df[0:0]
        datas = [new_df,]
        for _df in df_list:
            _df.dropna()
            _df.frequency_1=calc_frequency(_df.frequency_1, mps)
            _df.frequency_2=calc_frequency(_df.frequency_2, mps)
            _df.frequency = df[['frequency_1', 'frequency_2']].mean(axis=1)

            _df['rpm'] = _df.frequency*60
            
            #_df['g_frequency']=_df['frequency']*NUMBER_OF_MAGNET_PAIRS
            # _df['period']= 1/_df.g_frequency

    
            zeros_v_1 = np.where(np.diff(np.signbit(_df.voltage_1)))[0]
            zeros_v_2 = np.where(np.diff(np.signbit(_df.voltage_2)))[0]
            zeros_v_3 = np.where(np.diff(np.signbit(_df.voltage_3)))[0]
            zeros_v_dc =peakutils.peak.indexes(-_df.voltage_dc, thres=0.9)
            i=1
            j=0
            k=0
            while True:
                try:
                    cycle_1 = zeros_v_1[i+2]-zero_crossings_1[i]
                    print(cycle_1)
                    while zeros_v_2[j+1]<zero_crossings_1[i]:
                        j+=1
                    diffe_12 = zeros_v_1[i]-zero_crossings_2[j]
                    while zeros_v_3[k]<zero_crossings_1[i]:
                        k+=1
                    diffe_13 = zeros_v_3[k]-zero_crossings_1[i]
                    print(diffe_12,(diffe_12/cycle_1)*360)
                    print(diffe_13,(diffe_13/cycle_1)*360)
                except:
                    break
                i+=1
            for i in range(len(zeros_v_1)-1):
                x= _df.voltage_1[zeros_v_1[i]:zeros_v_1[i+1]]
                _df.eff_volt_1.iloc[zeros_v_1[i]:zeros_v_1[i+1]] = np.sqrt(np.mean(np.square(x)))   
            for i in range(len(zeros_v_2)-1):
                x = _df.voltage_2[zeros_v_2[i]:zeros_v_2[i+1]]
                _df.eff_volt_2.iloc[zeros_v_2[i]:zeros_v_2[i+1]] = np.sqrt(np.mean(np.square(x)))   
            for i in range(len(zeros_v_3)-1):
                x= _df.voltage_3[zeros_v_3[i]:zeros_v_3[i+1]]
                _df.eff_volt_3.iloc[zeros_v_3[i]:zeros_v_3[i+1]] = np.sqrt(np.mean(np.square(x)))   
            for i in range(len(zeros_v_dc)-1):
                x= _df.voltage_dc[zeros_v_dc[i]:zeros_v_dc[i+1]]
                _df.eff_volt_dc.iloc[zeros_v_dc[i]:zeros_v_dc[i+1]] = np.sqrt(np.mean(np.square(x)))   
            zeros_c_1 = np.where(np.diff(np.signbit(_df.current_1)))[0]
            zeros_c_2 = np.where(np.diff(np.signbit(_df.current_2)))[0]
            zeros_c_3 = np.where(np.diff(np.signbit(_df.current_3)))[0]
            zeros_c_dc = peakutils.peak.indexes(-_df.current_dc, thres=0.8)
            for i in range(len(zeros_c_1)-1):
                x= _df.current_1[zeros_c_1[i]:zeros_c_1[i+1]]
                _df.eff_curr_1.iloc[zeros_c_1[i]:zeros_c_1[i+1]] = np.sqrt(np.mean(np.square(x)))   
            for i in range(len(zeros_c_2)-1):
                x = _df.current_2[zeros_c_2[i]:zeros_c_2[i+1]]
                _df.eff_curr_2.iloc[zeros_c_2[i]:zeros_c_2[i+1]] = np.sqrt(np.mean(np.square(x)))   
            for i in range(len(zeros_c_3)-1):
                x= _df.current_3[zeros_c_3[i]:zeros_c_3[i+1]]
                _df.eff_curr_3.iloc[zeros_c_3[i]:zeros_c_3[i+1]] = np.sqrt(np.mean(np.square(x)))   
            for i in range(len(zeros_c_dc)-1):
                x= _df.current_dc[zeros_c_dc[i]:zeros_c_dc[i+1]]
                _df.eff_curr_dc.iloc[zeros_c_dc[i]:zeros_c_dc[i+1]] = np.sqrt(np.mean(np.square(x)))   
            

            _df.output = _df.eff_curr_1.multiply(_df.eff_volt_1).multiply(3)
            _df.input = _df.frequency*_df.torque*2*math.pi
            _df.efficiency = np.where(_df.output.isnull(), 0, _df.output/_df.input)
            datas.append(_df)
        new_df = pd.concat(datas)
        for i in [1,2,3,'dc']:
            time_data.append(
                get_graph(new_df, 'time', 'voltage_{}'.format(i), legendgroup="Phase {}".format(i))
                )
            time_data.append(
                get_graph(new_df, 'time', 'current_{}'.format(i),legendgroup="Phase {}".format(i))
                )
            time_data.append(
                get_graph(new_df, 'time', 'eff_volt_{}'.format(i),legendgroup="Phase {}".format(i))
                )
            time_data.append(
                get_graph(new_df, 'time', 'eff_curr_{}'.format(i),legendgroup="Phase {}".format(i))
                )
        time_data.append(
            get_graph(new_df, 'time', 'output'.format(i))
            )
        time_data.append(
            get_graph(new_df, 'time', 'input'.format(i))
            )
        time_data.append(
            get_graph(new_df, 'time', 'efficiency'.format(i))
            )
        
                

        time_data.append(get_graph(new_df, 'time', 'frequency'))
        rpm_data.append(get_graph(new_df, "rpm", "torque"))
        rpm_data.append(get_graph(new_df, "rpm" , "input"))
        rpm_data.append(get_graph(new_df, "rpm" , "output"))
        rpm_data.append(get_graph(new_df, "rpm" , "efficiency"))
        plot(time_data, filename='results/time.html')
    plot(rpm_data, filename='results/rpm.html')
    
       
if __name__ == "__main__":
    main()
