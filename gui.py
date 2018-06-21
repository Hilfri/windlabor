import tkinter as tk
from tkinter.filedialog import askopenfilenames
from PIL import Image, ImageTk
import myConfig
import os
from calc import Calculator


class PlotTK(tk.Frame):
    #GUI APP
    def __init__(self, parent):
        super().__init__(parent, background="white")
        self.version = "Version 21.06.18"
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
        scrollX = tk.Scrollbar(self, orient='horizontal')
        dataBox = tk.Listbox(self, height=26, width = 60, selectmode='extended', yscrollcommand=scrollY.set, xscrollcommand=scrollX.set)
        dataBox.insert('end', "<<No Files chosen>>")
        dataBox.grid(column=1, row=5, columnspan=2)
        self.guiListe = dataBox #external Reference
        scrollY.config(command=dataBox.yview)
        scrollY.grid(column=3, row=5)
        scrollX.config(command=dataBox.xview)
        scrollX.grid(column=2, row=6)

        #Version
        version = tk.Label(self, text=self.version, bg="white")
        version.grid(sticky='S',column= 1, row=7, pady=5)

    def help_me(self):
        print("help yourself!")

    def load_data(self):
        files = askopenfilenames(parent=self.parent, filetypes = (('Txt-File', '*.txt'),("All Files", "*.*")))
        self.guiListe.delete(0, 'end')
        self.file_list = []
        for file_name in files:
            self.guiListe.insert('end', file_name.replace(os.getcwd(),""))
            self.file_list.append(file_name.replace(os.getcwd(),""))

    def process_data(self):
        calc = Calculator()
        calc.get_formatted_data(self.file_list)
        print("cool")

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

def main():
    #Build GUI-Root
    tkRoot=tk.Tk()
    tkRoot.geometry("500x720+300+300")
    tkRoot.resizable(width=False, height=False)
    PlotIns = PlotTK(tkRoot)
    tkRoot.mainloop()

if __name__ =="__main__":
    main()
