import tkinter as tk
import pandas as pd
import glob
from tkinter.filedialog import askopenfilenames
from PIL import Image, ImageTk
import myConfig
import os
import webbrowser as wb
from calc import Calculator, Plotter


class PlotTK(tk.Frame):
    #GUI APP
    def __init__(self, parent):
        super().__init__(parent, background="white")
        self.version = "Version 13.07.18"
        self.parent=parent
        self.build()

    def build(self):

        #Build Program Window
        self.parent.title("Wind-Laboratory - Measuring Campaign")
        self.pack(fill='both', expand=False)
        #Menu Bar
        menubar = tk.Menu(self.parent)
        self.parent.config(menu=menubar)
        sysMenu = tk.Menu(self.parent)
        sysMenu.add_command(label="Factors", command = self.settings)
        sysMenu.add_command(label="Data Choices", command = self.settings_2)
        menubar.add_cascade(label="Settings", menu=sysMenu)
        helpMenu = tk.Menu(self.parent)
        helpMenu.add_command(label="Help", command=self.help_me)
        menubar.add_cascade(label="Help", menu=helpMenu)

        for i in range(1,6):
            self.rowconfigure(i, pad=5)
        for i in range(1,3):
            self.columnconfigure(i, pad=5)
        #Tu-Logo
        logo = Image.open("gui/index.png")
        logoObj = ImageTk.PhotoImage(logo)
        logoLabel = tk.Label(self,image=logoObj, bg="white")
        logoLabel.image= logoObj
        logoLabel.grid(sticky='E', column=2, row=1, padx=3)
        #Quick description
        text1 = tk.Label(self, bg='white', text="Assistant for \nAnalysis and plotting", font=("Helvetica", 20))
        text1.grid(sticky='NW', column=1, row=1)
        #buttons to do stuff
        loadBtn = tk.Button(self,text="Choose measurements", command=self.load_data, height=2, width=25)
        loadBtn.grid(column=1, row=2)
        processBtn = tk.Button(self, text="Process selected measurements", command=self.process_data, height=2, width=25)
        processBtn.grid(column=2, row=2)

        scrollY = tk.Scrollbar(self, orient='vertical')
        dataBox = tk.Listbox(self, height=10, width = 60, selectmode='extended', yscrollcommand=scrollY.set)
        dataBox.insert('end', "<<No Files chosen>>")
        dataBox.grid(column=1, row=5, columnspan=2)
        self.guiListe = dataBox #external Reference
        scrollY.config(command=dataBox.yview)
        scrollY.grid(column=3, row=5)

        #Version
        version = tk.Label(self, text=self.version, bg="white")
        version.grid(sticky='S',column= 1, row=7, pady=5)

    def help_me(self):
        wb.open("https://isis.tu-berlin.de/mod/wiki/view.php?pageid=5463&group=0")

    def load_data(self):
        files = askopenfilenames(parent=self.parent, filetypes = (('Txt-File', '*.txt'),("All Files", "*.*")))
        self.guiListe.delete(0, 'end')
        self.file_list = []
        for file_name in files:
            working_dir = os.getcwd().replace("\\", "/")
            self.guiListe.insert('end', file_name.replace(working_dir,""))
            self.file_list.append(file_name.replace(working_dir+"/",""))

    def process_data(self):
        calc = Calculator()
        plotter = Plotter()
        rpm_data = []
        rpm_str = []
        for filename in self.file_list:
            print(filename)
            _filename =filename.replace(".txt","").split("/")[-1]
            day, time, id, iteration = _filename.split('_')
            df_list, ps_shapes, ps_annos, amp_shapes, amp_annos= calc.get_formatted_data(filename, 10000)
            filename=filename.replace(".txt","")
            time_data = []
            shapes = []
            annos = []
            df = pd.concat(df_list)
            if myConfig.get("t_c_dc"):
                time_data.append(plotter.make_graph(df, "time", "current_dc"," {}|{}".format(id, iteration)))
                time_data.append(plotter.make_graph(df, "time", "eff_curr_dc"," {}|{}".format(id, iteration)))
            if myConfig.get("t_v_dc"):
                time_data.append(plotter.make_graph(df, "time", "voltage_dc"," {}|{}".format(id, iteration)))
                time_data.append(plotter.make_graph(df, "time", "eff_volt_dc"," {}|{}".format(id, iteration)))
            if myConfig.get("t_c_ac_1"):
                time_data.append(plotter.make_graph(df, "time", "current_1"," {}|{}".format(id, iteration)))
                time_data.append(plotter.make_graph(df, "time", "eff_curr_1"," {}|{}".format(id, iteration)))
            if myConfig.get("t_c_ac_2"):
                time_data.append(plotter.make_graph(df, "time", "current_2"," {}|{}".format(id, iteration)))
                time_data.append(plotter.make_graph(df, "time", "eff_curr_2"," {}|{}".format(id, iteration)))
            if myConfig.get("t_c_ac_3"):
                time_data.append(plotter.make_graph(df, "time", "current_3"," {}|{}".format(id, iteration)))
                time_data.append(plotter.make_graph(df, "time", "eff_curr_3"," {}|{}".format(id, iteration)))
            if myConfig.get("t_v_ac_1"):
                time_data.append(plotter.make_graph(df, "time", "voltage_1"," {}|{}".format(id, iteration)))
                time_data.append(plotter.make_graph(df, "time", "eff_volt_1"," {}|{}".format(id, iteration)))
            if myConfig.get("t_v_ac_2"):
                time_data.append(plotter.make_graph(df, "time", "voltage_2"," {}|{}".format(id, iteration)))
                time_data.append(plotter.make_graph(df, "time", "eff_volt_2"," {}|{}".format(id, iteration)))
            if myConfig.get("t_v_ac_3"):
                time_data.append(plotter.make_graph(df, "time", "voltage_3"," {}|{}".format(id, iteration)))
                time_data.append(plotter.make_graph(df, "time", "eff_volt_3"," {}|{}".format(id, iteration)))
            if myConfig.get("t_rpm"):
                time_data.append(plotter.make_graph(df, "time", "rpm"," {}|{}".format(id, iteration)))
            if myConfig.get("t_torque"):
                time_data.append(plotter.make_graph(df, "time", "torque"," {}|{}".format(id, iteration)))
            if myConfig.get("t_input"):
                time_data.append(plotter.make_graph(df, "time", "input"," {}|{}".format(id, iteration)))
            if myConfig.get("t_output"):
                time_data.append(plotter.make_graph(df, "time", "output"," {}|{}".format(id, iteration)))
            if myConfig.get("t_output_dc"):
                time_data.append(plotter.make_graph(df, "time", "output_dc"," {}|{}".format(id, iteration)))
            if myConfig.get("t_eff"):
                time_data.append(plotter.make_graph(df, "time", "efficiency"," {}|{}".format(id, iteration)))
            if myConfig.get("t_amp"):
                shapes+=amp_shapes
                annos+=amp_annos
            if myConfig.get("t_ps"):
                shapes+=ps_shapes
                annos+=ps_annos
            if myConfig.get("t_volt_orig"):
                time_data.append(plotter.make_graph(df, "time", "_voltage_1"," {}|{}".format(id, iteration)))
                time_data.append(plotter.make_graph(df, "time", "_voltage_2"," {}|{}".format(id, iteration)))
                time_data.append(plotter.make_graph(df, "time", "_voltage_3"," {}|{}".format(id, iteration)))
            if myConfig.get("rpm_c_dc"):
                rpm_data.append(plotter.make_graph(df, "rpm", "current_dc"," {}|{}".format(id, iteration)))
            if myConfig.get("rpm_v_dc"):
                rpm_data.append(plotter.make_graph(df, "rpm", "voltage_dc"," {}|{}".format(id, iteration)))
            if myConfig.get("rpm_c_ac_1"):
                rpm_data.append(plotter.make_graph(df, "rpm", "current_1"," {}|{}".format(id, iteration)))
            if myConfig.get("rpm_c_ac_2"):
                rpm_data.append(plotter.make_graph(df, "rpm", "current_2"," {}|{}".format(id, iteration)))
            if myConfig.get("rpm_c_ac_3"):
                rpm_data.append(plotter.make_graph(df, "rpm", "current_3"," {}|{}".format(id, iteration)))
            if myConfig.get("rpm_v_ac_1"):
                rpm_data.append(plotter.make_graph(df, "rpm", "voltage_1"," {}|{}".format(id, iteration)))
            if myConfig.get("rpm_v_ac_2"):
                rpm_data.append(plotter.make_graph(df, "rpm", "voltage_2"," {}|{}".format(id, iteration)))
            if myConfig.get("rpm_v_ac_3"):
                rpm_data.append(plotter.make_graph(df, "rpm", "voltage_3"," {}|{}".format(id, iteration)))
            if myConfig.get("rpm_torque"):
                rpm_data.append(plotter.make_graph(df, "rpm", "torque"," {}|{}".format(id, iteration)))
            if myConfig.get("rpm_input"):
                rpm_data.append(plotter.make_graph(df, "rpm", "input"," {}|{}".format(id, iteration)))
            if myConfig.get("rpm_output"):
                rpm_data.append(plotter.make_graph(df, "rpm", "output"," {}|{}".format(id, iteration)))
            if myConfig.get("rpm_output_dc"):
                time_data.append(plotter.make_graph(df, "time", "output_dc"," {}|{}".format(id, iteration)))
            if myConfig.get("rpm_eff"):
                rpm_data.append(plotter.make_graph(df, "rpm", "efficiency"," {}|{}".format(id, iteration)))
            if time_data:
                i=0
                htmlname = _filename
                while True:
                    if glob.glob("graphs/{}.{}".format(htmlname,".html")):
                        i+=1
                        htmlname = htmlname.replace("({})".format(i-1), "")+"({})".format(i)
                        continue
                    break

                plotter.plot_it(time_data, "graphs/{}.{}".format(htmlname,"html"), shapes, annos)

            i=0
            excelname = _filename
            while True:
                if glob.glob("excels/{}.{}".format(excelname,"xlsx")):
                    i+=1
                    excelname = excelname.replace("({})".format(i-1), "")+"({})".format(i)
                    continue
                break
            writer = pd.ExcelWriter("excels/{}.{}".format(excelname,"xlsx"))
            df.to_excel(writer)
            writer.save()
            rpm_str.append("{}-{}".format(id, iteration))
        if rpm_data:
            i=0
            rpmname = "RPM " + "_".join(rpm_str)
            while True:
                if glob.glob("graphs/{}.".format(rpmname,"html")):
                    i+=1
                    rpmname = rpmname.replace("({})".format(i-1), "")+"({})".format(i)
                    continue
                break
            plotter.plot_it(rpm_data, "graphs/{}.{}".format(rpmname,"html"), shapes, annos)
    def settings(self):
        self.build_settings()

    def build_settings(self):
        settings = tk.Toplevel()
        settings.title("Settings")
        settings.resizable(width=False, height=False)
        self.topSet = settings # external reference
        tk.Label(settings, text="Channel").grid(row=1, column=0)
        tk.Label(settings, text="Multiplyer").grid(row=1, column=1)
        tk.Label(settings, text="Divider").grid(row=1, column=2)
        tk.Label(settings, text="AC-Voltage").grid(row=2, column=0)
        self.ac_v_multi = tk.Entry(settings, width=10)
        self.ac_v_multi.grid(row=2, column=1)
        self.ac_v_multi.insert(0, myConfig.get('ac_v_multi'))
        self.ac_v_divi = tk.Entry(settings, width=10)
        self.ac_v_divi.grid(row=2, column=2)
        self.ac_v_divi.insert(0, myConfig.get('ac_v_divi'))
        tk.Label(settings, text="AC-Current").grid(row=3, column=0)
        self.ac_c_multi = tk.Entry(settings, width=10)
        self.ac_c_multi.grid(row=3, column=1)
        self.ac_c_multi.insert(0, myConfig.get('ac_c_multi'))
        self.ac_c_divi = tk.Entry(settings, width=10)
        self.ac_c_divi.grid(row=3, column=2)
        self.ac_c_divi.insert(0, myConfig.get('ac_c_divi'))
        tk.Label(settings, text="DC-Voltage").grid(row=4, column=0)
        self.dc_v_multi = tk.Entry(settings, width=10)
        self.dc_v_multi.grid(row=4, column=1)
        self.dc_v_multi.insert(0, myConfig.get('dc_v_multi'))
        self.dc_v_divi = tk.Entry(settings, width=10)
        self.dc_v_divi.grid(row=4, column=2)
        self.dc_v_divi.insert(0, myConfig.get('dc_v_divi'))
        tk.Label(settings, text="DC-Current").grid(row=5, column=0)
        self.dc_c_multi = tk.Entry(settings, width=10)
        self.dc_c_multi.grid(row=5, column=1)
        self.dc_c_multi.insert(0, myConfig.get('dc_c_multi'))
        self.dc_c_divi = tk.Entry(settings, width=10)
        self.dc_c_divi.grid(row=5, column=2)
        self.dc_c_divi.insert(0, myConfig.get('dc_c_divi'))
        tk.Label(settings, text="Torque").grid(row=6, column=0)
        self.torque_multi = tk.Entry(settings, width=10)
        self.torque_multi.grid(row=6, column=1)
        self.torque_multi.insert(0, myConfig.get('torque_multi'))
        self.torque_divi = tk.Entry(settings, width=10)
        self.torque_divi.grid(row=6, column=2)
        self.torque_divi.insert(0, myConfig.get('torque_divi'))
        saveBtn = tk.Button(settings, text="Save", command = self.save_settings, height=1, width=15)      
        saveBtn.grid(row=7,column=0)
        saveBtn = tk.Button(settings, text="Abbrechen", command = settings.destroy, height=1, width=15)
        saveBtn.grid(row=7, column=3)

    def save_settings(self):
        items = ["ac_v_multi"]
        myConfig.update("ac_v_multi", self.ac_v_multi.get())
        myConfig.update("ac_v_divi", self.ac_v_divi.get())
        myConfig.update("ac_c_multi", self.ac_c_multi.get())
        myConfig.update("ac_c_divi", self.ac_c_divi.get())
        myConfig.update("dc_v_multi", self.dc_v_multi.get())
        myConfig.update("dc_v_divi", self.dc_v_divi.get())
        myConfig.update("dc_c_multi", self.dc_c_multi.get())
        myConfig.update("dc_c_divi", self.dc_c_divi.get())
        myConfig.update("torque_multi", self.torque_multi.get())
        myConfig.update("torque_divi", self.torque_divi.get())
        self.topSet.destroy()

    def settings_2(self):
        self.build_settings_2()

    def build_settings_2(self):
        settings = tk.Toplevel()
        settings.title("Data-Choice")
        settings.resizable(width=False, height=False)
        self.topSet_2 = settings # external reference
        tk.Label(settings, text="Variable").grid(row=1, column=0)
        tk.Label(settings, text="Zeit").grid(row=1, column=1)
        tk.Label(settings, text="RPM").grid(row=1, column=2)

        tk.Label(settings, text="DC Current").grid(row=2, column=0)
        self.t_c_dc = tk.IntVar() #Current DC über Zeit
        self.t_c_dc.set(myConfig.get("t_c_dc"))
        tk.Checkbutton(settings, variable=self.t_c_dc).grid(row=2, column=1)
        self.rpm_c_dc = tk.IntVar() #current DC über RPM
        tk.Checkbutton(settings, variable=self.rpm_c_dc).grid(row=2, column=2)
        self.rpm_c_dc.set(myConfig.get("rpm_c_dc"))

        tk.Label(settings, text="DC Voltage").grid(row=3, column=0)
        self.t_v_dc = tk.IntVar() #Current DC über Zeit
        self.t_v_dc.set(myConfig.get("t_v_dc"))
        tk.Checkbutton(settings, variable=self.t_v_dc).grid(row=3, column=1)
        self.rpm_v_dc = tk.IntVar() #current DC über RPM
        tk.Checkbutton(settings, variable=self.rpm_v_dc).grid(row=3, column=2)
        self.rpm_v_dc.set(myConfig.get("rpm_v_dc"))

        tk.Label(settings, text="AC Current 1").grid(row=4, column=0)
        self.t_c_ac_1 = tk.IntVar() #Current DC über Zeit
        self.t_c_ac_1.set(myConfig.get("t_c_ac_1"))
        tk.Checkbutton(settings, variable=self.t_c_ac_1).grid(row=4, column=1)
        self.rpm_c_ac_1 = tk.IntVar() #current DC über RPM
        tk.Checkbutton(settings, variable=self.rpm_c_ac_1).grid(row=4, column=2)
        self.rpm_c_ac_1.set(myConfig.get("rpm_c_ac_1"))

        tk.Label(settings, text="AC Current 2").grid(row=5, column=0)
        self.t_c_ac_2 = tk.IntVar() #Current DC über Zeit
        self.t_c_ac_2.set(myConfig.get("t_c_ac_2"))
        tk.Checkbutton(settings, variable=self.t_c_ac_2).grid(row=5, column=1)
        self.rpm_c_ac_2 = tk.IntVar() #current DC über RPM
        tk.Checkbutton(settings, variable=self.rpm_c_ac_2).grid(row=5, column=2)
        self.rpm_c_ac_2.set(myConfig.get("rpm_c_ac_2"))

        tk.Label(settings, text="AC Current 3").grid(row=6, column=0)
        self.t_c_ac_3 = tk.IntVar() #Current DC über Zeit
        self.t_c_ac_3.set(myConfig.get("t_c_ac_3"))
        tk.Checkbutton(settings, variable=self.t_c_ac_3).grid(row=6, column=1)
        self.rpm_c_ac_3 = tk.IntVar() #current DC über RPM
        tk.Checkbutton(settings, variable=self.rpm_c_ac_3).grid(row=6, column=2)
        self.rpm_c_ac_3.set(myConfig.get("rpm_c_ac_3"))

        tk.Label(settings, text="AC Voltage 1").grid(row=7, column=0)
        self.t_v_ac_1 = tk.IntVar() #Current DC über Zeit
        self.t_v_ac_1.set(myConfig.get("t_v_ac_1"))
        tk.Checkbutton(settings, variable=self.t_v_ac_1).grid(row=7, column=1)
        self.rpm_v_ac_1 = tk.IntVar() #current DC über RPM
        tk.Checkbutton(settings, variable=self.rpm_v_ac_1).grid(row=7, column=2)
        self.rpm_v_ac_1.set(myConfig.get("rpm_v_ac_1"))

        tk.Label(settings, text="AC Voltage 2").grid(row=8, column=0)
        self.t_v_ac_2 = tk.IntVar() #Current DC über Zeit
        self.t_v_ac_2.set(myConfig.get("t_v_ac_2"))
        tk.Checkbutton(settings, variable=self.t_v_ac_2).grid(row=8, column=1)
        self.rpm_v_ac_2 = tk.IntVar() #current DC über RPM
        tk.Checkbutton(settings, variable=self.rpm_v_ac_2).grid(row=8, column=2)
        self.rpm_v_ac_2.set(myConfig.get("rpm_v_ac_2"))

        tk.Label(settings, text="AC Voltage 3").grid(row=9, column=0)
        self.t_v_ac_3 = tk.IntVar() #Current DC über Zeit
        self.t_v_ac_3.set(myConfig.get("t_v_ac_3"))
        tk.Checkbutton(settings, variable=self.t_v_ac_3).grid(row=9, column=1)
        self.rpm_v_ac_3 = tk.IntVar() #current DC über RPM
        tk.Checkbutton(settings, variable=self.rpm_v_ac_3).grid(row=9, column=2)
        self.rpm_v_ac_3.set(myConfig.get("rpm_v_ac_3"))

        tk.Label(settings, text="Input").grid(row=10, column=0)
        self.t_input = tk.IntVar() #Current DC über Zeit
        self.t_input.set(myConfig.get("t_input"))
        tk.Checkbutton(settings, variable=self.t_input).grid(row=10, column=1)
        self.rpm_input = tk.IntVar() #current DC über RPM
        tk.Checkbutton(settings, variable=self.rpm_input).grid(row=10, column=2)
        self.rpm_input.set(myConfig.get("rpm_input"))

        tk.Label(settings, text="Output").grid(row=11, column=0)
        self.t_output = tk.IntVar() #Current DC über Zeit
        self.t_output.set(myConfig.get("t_output"))
        tk.Checkbutton(settings, variable=self.t_output).grid(row=11, column=1)
        self.rpm_output = tk.IntVar() #current DC über RPM
        tk.Checkbutton(settings, variable=self.rpm_output).grid(row=11, column=2)
        self.rpm_output.set(myConfig.get("rpm_output"))

        tk.Label(settings, text="Output DC").grid(row=12, column=0)
        self.t_output_dc = tk.IntVar() #Current DC über Zeit
        self.t_output_dc.set(myConfig.get("t_output_dc"))
        tk.Checkbutton(settings, variable=self.t_output_dc).grid(row=12, column=1)
        self.rpm_output_dc = tk.IntVar() #current DC über RPM
        tk.Checkbutton(settings, variable=self.rpm_output_dc).grid(row=12, column=2)
        self.rpm_output_dc.set(myConfig.get("rpm_output_dc"))

        tk.Label(settings, text="Efficiency").grid(row=13, column=0)
        self.t_eff = tk.IntVar() #Current DC über Zeit
        self.t_eff.set(myConfig.get("t_eff"))
        tk.Checkbutton(settings, variable=self.t_eff).grid(row=13, column=1)
        self.rpm_eff = tk.IntVar() #current DC über RPM
        tk.Checkbutton(settings, variable=self.rpm_eff).grid(row=13, column=2)
        self.rpm_eff.set(myConfig.get("rpm_eff"))

        tk.Label(settings, text="Amplitude (V)").grid(row=14, column=0)
        self.t_amp = tk.IntVar() #Current DC über Zeit
        self.t_amp.set(myConfig.get("t_amp"))
        tk.Checkbutton(settings, variable=self.t_amp).grid(row=14, column=1)
        
        tk.Label(settings, text="Phaseshift (V)").grid(row=15, column=0)
        self.t_ps = tk.IntVar() #Current DC über Zeit
        self.t_ps.set(myConfig.get("t_ps"))
        tk.Checkbutton(settings, variable=self.t_ps).grid(row=15, column=1)

        tk.Label(settings, text="Volt(only factors)").grid(row=16, column=0)
        self.t_volt_orig = tk.IntVar() #Current DC über Zeit
        self.t_volt_orig.set(myConfig.get("t_volt_orig"))
        tk.Checkbutton(settings, variable=self.t_volt_orig).grid(row=16, column=1)

        tk.Label(settings, text="Torque").grid(row=17, column=0)
        self.t_torque = tk.IntVar() #Current DC über Zeit
        self.t_torque.set(myConfig.get("t_torque"))
        tk.Checkbutton(settings, variable=self.t_torque).grid(row=17, column=1)

        tk.Label(settings, text="RPM").grid(row=18, column=0)
        self.t_rpm = tk.IntVar() #Current DC über Zeit
        self.t_rpm.set(myConfig.get("t_rpm"))
        tk.Checkbutton(settings, variable=self.t_rpm).grid(row=18, column=1)

        saveBtn = tk.Button(settings, text="Save", command = self.save_settings_2, height=1, width=15)      
        saveBtn.grid(row=19,column=0)
        saveBtn = tk.Button(settings, text="Abbrechen", command = settings.destroy, height=1, width=15)
        saveBtn.grid(row=19, column=2)

    def save_settings_2(self):
        myConfig.update("t_c_dc", self.t_c_dc.get())
        myConfig.update("t_v_dc", self.t_v_dc.get())
        myConfig.update("t_c_ac_1", self.t_c_ac_1.get())
        myConfig.update("t_c_ac_2", self.t_c_ac_2.get())
        myConfig.update("t_c_ac_3", self.t_c_ac_3.get())
        myConfig.update("t_v_ac_1", self.t_v_ac_1.get())
        myConfig.update("t_v_ac_2", self.t_v_ac_2.get())
        myConfig.update("t_v_ac_3", self.t_v_ac_3.get())
        myConfig.update("t_input", self.t_input.get())
        myConfig.update("t_output", self.t_output.get())
        myConfig.update("t_output_dc", self.t_output_dc.get())
        myConfig.update("t_eff", self.t_eff.get())
        myConfig.update("t_amp", self.t_amp.get())
        myConfig.update("t_ps", self.t_ps.get())
        myConfig.update("t_rpm", self.t_rpm.get())
        myConfig.update("t_torque", self.t_torque.get())
        myConfig.update("t_volt_orig", self.t_volt_orig.get())

        myConfig.update("rpm_c_dc", self.rpm_c_dc.get())
        myConfig.update("rpm_v_dc", self.rpm_v_dc.get())
        myConfig.update("rpm_c_ac_1", self.rpm_c_ac_1.get())
        myConfig.update("rpm_c_ac_2", self.rpm_c_ac_2.get())
        myConfig.update("rpm_c_ac_3", self.rpm_c_ac_3.get())
        myConfig.update("rpm_v_ac_1", self.rpm_v_ac_1.get())
        myConfig.update("rpm_v_ac_2", self.rpm_v_ac_2.get())
        myConfig.update("rpm_v_ac_3", self.rpm_v_ac_3.get())
        myConfig.update("rpm_input", self.rpm_input.get())
        myConfig.update("rpm_output", self.rpm_output.get())
        myConfig.update("rpm_eff", self.rpm_eff.get())
        self.topSet_2.destroy()

def main():
    #Build GUI-Root
    tkRoot=tk.Tk()
    tkRoot.geometry("500x470+300+300")
    tkRoot.resizable(width=False, height=False)
    PlotIns = PlotTK(tkRoot)
    tkRoot.mainloop()

if __name__ =="__main__":
    main()

