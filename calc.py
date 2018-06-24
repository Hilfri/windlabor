import pandas as pd
import datetime
import plotly.plotly as py
import numpy as np
import os
import plotly.graph_objs as go
from plotly.offline import plot
import myConfig


def indexes(y, thres=0.3, min_dist=1):
    #copied from peakutils (to prevent issues with pyinstaller for windows)
    """Peak detection routine.

    Finds the numeric index of the peaks in *y* by taking its first order difference. By using
    *thres* and *min_dist* parameters, it is possible to reduce the number of
    detected peaks. *y* must be signed.

    Parameters
    ----------
    y : ndarray (signed)
        1D amplitude data to search for peaks.
    thres : float between [0., 1.]
        Normalized threshold. Only the peaks with amplitude higher than the
        threshold will be detected.
    min_dist : int
        Minimum distance between each detected peak. The peak with the highest
        amplitude is preferred to satisfy this constraint.

    Returns
    -------
    ndarray
        Array containing the numeric indexes of the peaks that were detected
    """
    if isinstance(y, np.ndarray) and np.issubdtype(y.dtype, np.unsignedinteger):
        raise ValueError("y must be signed")

    thres = thres * (np.max(y) - np.min(y)) + np.min(y)
    min_dist = int(min_dist)

    # compute first order difference
    dy = np.diff(y)

    # propagate left and right values successively to fill all plateau pixels (0-value)
    zeros,=np.where(dy == 0)
    
    # check if the singal is totally flat
    if len(zeros) == len(y) - 1:
        return np.array([])
    
    while len(zeros):
        # add pixels 2 by 2 to propagate left and right value onto the zero-value pixel
        zerosr = np.hstack([dy[1:], 0.])
        zerosl = np.hstack([0., dy[:-1]])

        # replace 0 with right value if non zero
        dy[zeros]=zerosr[zeros]
        zeros,=np.where(dy == 0)

        # replace 0 with left value if non zero
        dy[zeros]=zerosl[zeros]
        zeros,=np.where(dy == 0)

    # find the peaks by using the first order difference
    peaks = np.where((np.hstack([dy, 0.]) < 0.)
                     & (np.hstack([0., dy]) > 0.)
                     & (y > thres))[0]

    # handle multiple peaks, respecting the minimum distance
    if peaks.size > 1 and min_dist > 1:
        highest = peaks[np.argsort(y[peaks])][::-1]
        rem = np.ones(y.size, dtype=bool)
        rem[peaks] = False

        for peak in highest:
            if not rem[peak]:
                sl = slice(max(0, peak - min_dist), peak + min_dist + 1)
                rem[sl] = True
                rem[peak] = False

        peaks = np.arange(y.size)[~rem]

    return peaks



class Calculator():

    def __init__(self):
        self.ac_v_factor = float(myConfig.get("ac_v_multi"))/float(myConfig.get("ac_v_divi"))
        self.ac_c_factor = float(myConfig.get("ac_c_multi"))/float(myConfig.get("ac_c_divi"))
        self.dc_v_factor = float(myConfig.get("dc_v_multi"))/float(myConfig.get("dc_v_divi"))
        self.dc_c_factor = float(myConfig.get("dc_c_multi"))/float(myConfig.get("dc_c_divi"))
        self.torque_factor = float(myConfig.get("torque_multi"))/float(myConfig.get("torque_divi"))
        self.headers = ['time', 
                        'current_1', 
                        'current_3', 
                        'voltage_1', 
                        'voltage_3', 
                        'frequency_2', 
                        'current_2',
                        'current_dc',
                        'voltage_2',
                        'voltage_dc',
                        'torque',
                        'frequency_1'
                        ]

    def calc_frequency(self,df, f1,f2, mps):
        multi = mps/200.0
        df[f1] = df[f1].apply(np.fix).diff().divide(5).abs().rolling(200).sum().multiply(multi).divide(360)
        df[f2] = df[f2].apply(np.fix).diff().divide(5).abs().rolling(200).sum().multiply(multi).divide(360)
        df.frequency = df[[f1,f2]].mean(axis=1)
        return df
    def calc_output(self, df):
        df['volt_sum'] = df[["eff_volt_1", "eff_volt_2", "eff_volt_3"]].mean(axis=1).multiply(3)
        df['curr_sum'] = df[["eff_curr_1", "eff_curr_2", "eff_curr_3"]].mean(axis=1)
        df.output=df.volt_sum*df.curr_sum
        return df.output
        
    def load_measurements(self,filename):
        data = pd.read_csv(filename,sep ='\t', header=0, skiprows=4)
        return data
    def fix_dots(self,df):
        for i in self.headers[1:]:#exclude time since its not a float value
            df[i] = df[i].str.replace(',', '.').astype(float)
        return df
    def change_header_names(self, df):
        count = len(df.columns)-len(self.headers)
        df.columns = self.headers+["Random {}".format(i) for i in range(count)]
        return df
    
    def apply_factors(self, df):
        for i in [1,2,3]:
            df['voltage_{}'.format(i)] = df['voltage_{}'.format(i)].multiply(self.ac_v_factor)
            df['current_{}'.format(i)] = df['current_{}'.format(i)].multiply(self.ac_c_factor)
        df['voltage_dc'] = df['voltage_dc'].multiply(self.dc_v_factor)
        df['current_dc'] = df['current_dc'].multiply(self.dc_c_factor)
        df['torque'] = df['torque'].multiply(self.torque_factor)
        return df

    def add_new_cols(self, df):
        for i in [1,2,3,'dc']:
            df['eff_volt_{}'.format(i)] = np.nan
            df['eff_curr_{}'.format(i)] = np.nan
        for i in ['frequency', 'rpm', 'input', 'output', 'efficiency']:
            df[i] = np.nan
        return df

    def split_at_gaps(self, df):
        blanks = df[df.isnull().all(1)].index
        gaps = df[df.time.diff()>pd.Timedelta(0.1,'ms')].index
        return np.split(df, np.sort(np.append(blanks,gaps)))

    def get_formatted_data(self, filename, mps):
        """
        load file-->change headers to be easier to identify-->add appropriate types (float, date)
        -->multiply with factors
        """
        df = self.load_measurements(filename)
        df = self.change_header_names(df)
        df['time']=pd.to_datetime(df['time'], format='%d.%m.%Y  %H:%M:%S,%f')
        df = self.fix_dots(df)
        df = self.apply_factors(df)
        df = self.add_new_cols(df)
        df_list = self.split_at_gaps(df)
        new_df = df[0:0]
        datas = [new_df,]
        ps_shapes = []
        ps_annos = []
        amp_shapes = []
        amp_annos = []
        for _df in df_list:
            _df.iloc[0]=np.nan
            _df = self.calc_frequency(_df, "frequency_1", "frequency_2", mps)
            _df.rpm = _df.frequency*60
            #_df['g_frequency']=_df['frequency']*NUMBER_OF_MAGNET_PAIRS
            # _df['period']= 1/_df.g_frequency

            ### Find zero-crossings
            zeros_v_1 = np.trim_zeros(np.where(np.diff(np.signbit(_df.voltage_1)))[0])
            zeros_v_2 = np.trim_zeros(np.where(np.diff(np.signbit(_df.voltage_2)))[0])
            zeros_v_3 = np.trim_zeros(np.where(np.diff(np.signbit(_df.voltage_3)))[0])
            """
            find zero-crossings of different phases and calculate the shift
            one cycle is the range between a zero crossing and the next next one
            the difference between the zero-crossings of different phases divided by 
            the cycle length * 360° defines the phase shift
            The looping is necessary, because its not always the first phase that has the 
            first zero_crossing
            """
            i=0
            j=0
            while True:
                i+=1
                try:
                    cycle_1 = zeros_v_1[i+1]-zeros_v_1[i-1]
                except:
                    pass
                try:
                    while zeros_v_2[j+1]<zeros_v_1[i]:
                        j+=1
                    time1= _df.time.iloc[zeros_v_1[i]]
                    time2= _df.time.iloc[zeros_v_2[j]]
                    ps_shapes.append(Plotter().make_vert_shape(time1,'blue', 'top'))
                    ps_shapes.append(Plotter().make_vert_shape(time2,'blue', 'top'))
                    ps_shapes.append(Plotter().make_hor_shape(time1,time2,'blue'))
                    diffe_12 = zeros_v_1[i]-zeros_v_2[j]
                    shift = 360*diffe_12/cycle_1
                    mid = np.floor(zeros_v_2[j]+diffe_12/2)
                    mid_time = _df.time.iloc[int(mid)]
                    ps_annos.append(Plotter().add_text_to_shape(mid_time, "{0:.2f}°".format(shift), 'blue', 'top'))
                except IndexError:
                    break
                except KeyError as e:
                    print(str(e))
                    continue
            i=0
            k=0
            while True:
                i+=1
                try:
                    cycle_1 = zeros_v_1[i+1]-zeros_v_1[i-1]
                except:
                    pass
                try:
                    while zeros_v_3[k]<zeros_v_1[i]:
                        k+=1
                    time1= _df.time.iloc[zeros_v_3[k]]
                    time2= _df.time.iloc[zeros_v_1[i]]
                    ps_shapes.append(Plotter().make_vert_shape(time1,'green', 'bottom'))
                    ps_shapes.append(Plotter().make_vert_shape(time2,'green', 'bottom'))
                    ps_shapes.append(Plotter().make_hor_shape(time1,time2,'green'))
                    diffe_13 = zeros_v_3[k]-zeros_v_1[i]
                    shift = 360*diffe_13/cycle_1
                    mid = np.floor(zeros_v_1[i]+diffe_13/2)
                    mid_time = _df.time.iloc[int(mid)]
                    ps_annos.append(Plotter().add_text_to_shape(mid_time, "{0:.2f}°".format(shift), 'green', 'bottom'))
                except IndexError:
                    break
                except KeyError as e:
                    print(str(e))
                    continue
            """
            Adding Lines to show the amplitude
            """



            """
            Calculation of the effective current and voltage is done with the 
            root mean square of one whole cycle. 
            """

            for i in range(len(zeros_v_1)-2):
                x= _df.voltage_1[zeros_v_1[i]:zeros_v_1[i+2]]
                _df.eff_volt_1.iloc[zeros_v_1[i]:zeros_v_1[i+2]] = np.sqrt(np.mean(np.square(x)))           
            for i in range(len(zeros_v_2)-2):
                x = _df.voltage_2[zeros_v_2[i]:zeros_v_2[i+2]]
                _df.eff_volt_2.iloc[zeros_v_2[i]:zeros_v_2[i+2]] = np.sqrt(np.mean(np.square(x)))   
            for i in range(len(zeros_v_3)-2):
                x= _df.voltage_3[zeros_v_3[i]:zeros_v_3[i+2]]
                _df.eff_volt_3.iloc[zeros_v_3[i]:zeros_v_3[i+2]] = np.sqrt(np.mean(np.square(x)))   
            _df.eff_volt_dc = _df.voltage_dc.mean()
            zeros_c_1 = np.trim_zeros(np.where(np.diff(np.signbit(_df.current_1)))[0])
            zeros_c_2 = np.trim_zeros(np.where(np.diff(np.signbit(_df.current_2)))[0])
            zeros_c_3 = np.trim_zeros(np.where(np.diff(np.signbit(_df.current_3)))[0])
            for i in range(len(zeros_c_1)-2):
                x= _df.current_1[zeros_c_1[i]:zeros_c_1[i+2]]
                _df.eff_curr_1.iloc[zeros_c_1[i]:zeros_c_1[i+2]] = np.sqrt(np.mean(np.square(x)))   
            for i in range(len(zeros_c_2)-2):
                x = _df.current_2[zeros_c_2[i]:zeros_c_2[i+2]]
                _df.eff_curr_2.iloc[zeros_c_2[i]:zeros_c_2[i+2]] = np.sqrt(np.mean(np.square(x)))   
            for i in range(len(zeros_c_3)-2):
                x= _df.current_3[zeros_c_3[i]:zeros_c_3[i+2]]
                _df.eff_curr_3.iloc[zeros_c_3[i]:zeros_c_3[i+2]] = np.sqrt(np.mean(np.square(x)))   
            _df.eff_curr_dc = _df.current_dc.mean()
            _df.output = self.calc_output(_df)#_df.eff_curr_1.multiply(_df.eff_volt_1).multiply(3)
            _df.input = _df.frequency*_df.torque*2*np.pi
            _df.efficiency = np.where(_df.output.isnull(), None, _df.output/_df.input)
            datas.append(_df)
        if myConfig.get("t_amp"):
            sh = int(np.floor(mps/200))
            max_1 = indexes(df.voltage_1, thres=0.95, min_dist=sh)
            min_1 = indexes(-df.voltage_1, thres=0.95, min_dist=sh)
            if myConfig.get("t_v_ac_1"):
                for i in max_1:
                    if i-sh<0:
                        mini=1
                    else:
                        mini = i-sh
                    maxi = i+sh
                    try:
                        time = df.time.iloc[i]
                        time1 = time + datetime.timedelta(milliseconds=sh*10)
                        time2 = time + datetime.timedelta(milliseconds=sh*10)
                        voltage = df.voltage_1.iloc[i]
                        amp_shapes.append(Plotter().make_hor_shape(time1,time2,'grey', y=voltage))
                        amp_annos.append(Plotter().add_text_to_shape(time, "{0:.2f} V".format(voltage),'grey', 'top',y=voltage))
                    except:
                        continue
                for i in min_1:
                    if i-sh<0:
                        mini=1
                    else:
                        mini = i-sh
                    maxi = i+sh
                    try:
                        time = df.time.iloc[i]
                        time1 = time + datetime.timedelta(milliseconds=sh*10)
                        time2 = time + datetime.timedelta(milliseconds=sh*10)
                        voltage = df.voltage_1.iloc[i]
                        amp_shapes.append(Plotter().make_hor_shape(time1,time2,'grey', y=voltage))
                        amp_annos.append(Plotter().add_text_to_shape(time, "{0:.2f} V".format(voltage),'grey', 'bottom',y=voltage))
                    except:
                        continue
            if myConfig.get("t_v_ac_2"):

                max_2 = indexes(df.voltage_2, thres=0.95, min_dist=sh)
                min_2 = indexes(-df.voltage_2, thres=0.95, min_dist=sh)
                for i in min_2:
                    if i-sh<0:
                        mini=1
                    else:
                        mini = i-sh
                    maxi = i+sh
                    try:
                        time = df.time.iloc[i]
                        time1 = time + datetime.timedelta(milliseconds=sh*10)
                        time2 = time + datetime.timedelta(milliseconds=sh*10)
                        voltage = df.voltage_2.iloc[i]
                        amp_shapes.append(Plotter().make_hor_shape(time1,time2,'grey', y=voltage))
                        amp_annos.append(Plotter().add_text_to_shape(time, "{0:.2f} V".format(voltage),'grey', 'bottom',y=voltage))
                    except:
                        continue

                for i in max_2:
                    if i-sh<0:
                        mini=1
                    else:
                        mini = i-sh
                    maxi = i+sh
                    try:
                        time = df.time.iloc[i]
                        time1 = time + datetime.timedelta(milliseconds=sh*10)
                        time2 = time + datetime.timedelta(milliseconds=sh*10)
                        voltage = df.voltage_2.iloc[i]
                        amp_shapes.append(Plotter().make_hor_shape(time1,time2,'grey', y=voltage))
                        amp_annos.append(Plotter().add_text_to_shape(time, "{0:.2f} V".format(voltage),'grey', 'top',y=voltage))
                    except:
                        continue
            if myConfig.get("t_v_ac_3"):

                max_3 = indexes(df.voltage_3, thres=0.95, min_dist=sh)
                min_3 = indexes(-df.voltage_3, thres=0.95, min_dist=sh)

                for i in max_3:
                    if i-sh<0:
                        mini=1
                    else:
                        mini = i-sh
                    maxi = i+sh
                    try:
                        time = df.time.iloc[i]
                        time1 = time + datetime.timedelta(milliseconds=sh*10)
                        time2 = time + datetime.timedelta(milliseconds=sh*10)
                        voltage = df.voltage_3.iloc[i]
                        amp_shapes.append(Plotter().make_hor_shape(time1,time2,'grey', y=voltage))
                        amp_annos.append(Plotter().add_text_to_shape(time, "{0:.2f} V".format(voltage),'grey', 'top',y=voltage))
                    except:
                        continue
                for i in min_3:
                    if i-sh<0:
                        mini=1
                    else:
                        mini = i-sh
                    maxi = i+sh
                    try:
                        time = df.time.iloc[i]
                        time1 = time + datetime.timedelta(milliseconds=sh*10)
                        time2 = time + datetime.timedelta(milliseconds=sh*10)
                        voltage = df.voltage_3.iloc[i]
                        amp_shapes.append(Plotter().make_hor_shape(time1,time2,'grey', y=voltage))
                        amp_annos.append(Plotter().add_text_to_shape(time, "{0:.2f} V".format(voltage),'grey', 'bottom',y=voltage))
                    except:
                        continue

        return datas, ps_shapes, ps_annos, amp_shapes, amp_annos


class Plotter():

    def make_vert_shape(self, time, color, position):
        if position=='bottom':
            y_fak = -1
        else:
            y_fak = 1
        return dict(
                type='line',
                x0=time,
                x1=time,
                y0=0,
                y1=0.0,
                line = dict(width=2, color=color)
                )
    def make_hor_shape(self, time1, time2, color,y=0):
        return dict(
                type='line',
                x0=time1,
                x1=time2,
                y0=y,
                y1=y,
                line = dict(width=2, color=color, dash='dot')
                )
    def add_text_to_shape(self, time, text, color, position, y=0):
        return dict(
                x=[time],
                y=[y],
                text=text,
                textposition=position,
                mode='text',
                legendgroup="Phaseshift",
                showlegend=False,
                hoverinfo='none',
                textfont=dict(
                    size=10,
                    color=color
                    )
                )
                

    def make_graph(self,df, x, y, postfix):
        return dict(
                    x=df[x],
                    y=df[y],
                    line=dict(width=2),
                    name=y+postfix,
                    connectgaps=False
                    )

    def plot_it(self, data, file_name, shapes, annotations):
        layout = go.Layout(showlegend=True, shapes=shapes)
        fig = go.Figure(data=data+annotations, layout=layout)
        return plot(fig, filename=file_name)            


