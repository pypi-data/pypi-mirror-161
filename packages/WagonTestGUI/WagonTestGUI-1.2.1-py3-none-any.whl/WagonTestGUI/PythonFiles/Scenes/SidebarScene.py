#################################################################################

import tkinter as tk
from PIL import ImageTk as iTK
from PIL import Image
import logging
import WagonTestGUI

#################################################################################

FORMAT = '%(asctime)s|%(levelname)s|%(message)s|'
logging.basicConfig(filename="{}/PythonFiles/logs/GUIWindow.log".format(WagonTestGUI.__path__[0]), filemode = 'w', format=FORMAT, level=logging.DEBUG)

class SidebarScene(tk.Frame):

    #################################################

    def __init__(self, parent, sidebar_frame, data_holder):
        super().__init__(sidebar_frame, width=213, height = 500, bg = '#808080', padx = 10, pady=10)

        self.data_holder = data_holder

        self.update_sidebar(parent)

    #################################################

    def update_sidebar(self, parent):
        
        logging.info("SidebarScene: The sidebar has been updated.")

        # List for creating check marks with for loop
        self.list_of_pass_fail = self.data_holder.data_lists['test_results']

        # For loop to create checkmarks based on pass/fail
        for index in range(len(self.list_of_pass_fail)):
            if(self.list_of_pass_fail[index] == True):
                # Create a photoimage object of the QR Code
                Green_Check_Image = Image.open("{}/PythonFiles/Images/GreenCheckMark.png".format(WagonTestGUI.__path__[0]))
                Green_Check_Image = Green_Check_Image.resize((50,50), Image.ANTIALIAS)
                Green_Check_PhotoImage = iTK.PhotoImage(Green_Check_Image)
                GreenCheck_Label = tk.Label(self, image=Green_Check_PhotoImage, width=50, height=50, bg = '#808080')
                GreenCheck_Label.image = Green_Check_PhotoImage

                GreenCheck_Label.grid(row=index + 2, column=1)

            else:
                # Create a photoimage object of the QR Code
                Red_X_Image = Image.open("{}/PythonFiles/Images/RedX.png".format(WagonTestGUI.__path__[0]))
                Red_X_Image = Red_X_Image.resize((50,50), Image.ANTIALIAS)
                Red_X_PhotoImage = iTK.PhotoImage(Red_X_Image)
                RedX_Label = tk.Label(self, image=Red_X_PhotoImage, width=50, height=50, bg = '#808080')
                RedX_Label.image = Red_X_PhotoImage

                RedX_Label.grid(row=index + 2, column=1)

        # Variables for easy button editing
        btn_height = 3
        btn_width = 18
        btn_font = ('Arial', 10)
        btn_pady = 5

        self.btn_login = tk.Button(
            self,
            pady = btn_pady,
            text = 'LOGIN PAGE',
            height = btn_height,
            width = btn_width,
            font = btn_font
        )
        self.btn_login.grid(column = 0, row = 0)

        self.btn_scan = tk.Button(
            self,
            pady = btn_pady,
            text = 'SCAN PAGE',
            height = btn_height,
            width = btn_width,
            font = btn_font
        )
        self.btn_scan.grid(column = 0, row = 1)

        self.btn_test1 = tk.Button(
            self, 
            pady = btn_pady,
            text = 'GEN. RESIST. TEST',
            height = btn_height,
            width = btn_width,
            font = btn_font,
            command = lambda: self.btn_test1_action(parent)
            )
        self.btn_test1.grid(column = 0, row = 2)

        if self.data_holder.data_dict['test1_pass'] == True:
            self.btn_test1.config(state = 'disabled')


        self.btn_test2 = tk.Button(
            self,
            pady = btn_pady, 
            text = 'ID RESISTOR TEST',
            height = btn_height,
            width = btn_width,
            font = btn_font,
            command = lambda: self.btn_test2_action(parent)
            )
        self.btn_test2.grid(column = 0, row = 3)

        if self.data_holder.data_dict['test2_pass'] == True:
            self.btn_test2.config(state = 'disabled')

        self.btn_test3 = tk.Button(
            self, 
            pady = btn_pady,
            text = 'I2C COMM. TEST',
            height = btn_height,
            width = btn_width,
            font = btn_font,
            command = lambda: self.btn_test3_action(parent)
            )
        self.btn_test3.grid(column = 0, row = 4)

        if self.data_holder.data_dict['test3_pass'] == True:
            self.btn_test3.config(state = 'disabled')

        self.btn_test4 = tk.Button(
            self, 
            pady = btn_pady,
            text = 'BIT RATE TEST',
            height = btn_height,
            width = btn_width,
            font = btn_font,
            command = lambda: self.btn_test4_action(parent)
            )
        self.btn_test4.grid(column = 0, row = 5)
        if self.data_holder.data_dict['test4_pass'] == True:
            self.btn_test4.config(state = 'disabled')

        self.btn_summary = tk.Button(
            self, 
            pady = btn_pady,
            text = 'TEST SUMMARY',
            height = btn_height,
            width = btn_width,
            font = btn_font,
            command = lambda: self.btn_summary_action(parent)
            )
        self.btn_summary.grid(column = 0, row = 6)

        self.grid_propagate(0)

    #################################################

    def btn_test1_action(self, _parent):
        _parent.set_frame_test1()

    def btn_test2_action(self, _parent):
        _parent.set_frame_test2()

    def btn_test3_action(self, _parent):
        _parent.set_frame_test3()

    def btn_test4_action(self, _parent):
        _parent.set_frame_test4()

    def btn_summary_action(self, _parent):
        _parent.set_frame_test_summary()

    #################################################

    def disable_all_btns(self):
        self.btn_login.config(state = 'disabled')
        self.btn_scan.config(state = 'disabled')
        self.btn_test1.config(state = 'disabled')
        self.btn_test2.config(state = 'disabled')
        self.btn_test3.config(state = 'disabled')
        self.btn_test4.config(state = 'disabled')
        self.btn_summary.config(state = 'disabled')

    #################################################

    def disable_all_but_log_scan(self):
        self.btn_test1.config(state = 'disabled')
        self.btn_test2.config(state = 'disabled')
        self.btn_test3.config(state = 'disabled')
        self.btn_test4.config(state = 'disabled')
        self.btn_summary.config(state = 'disabled')

    #################################################

    def disable_all_btns_but_scan(self):
        self.btn_login.config(state = 'disabled')
        self.btn_test1.config(state = 'disabled')
        self.btn_test2.config(state = 'disabled')
        self.btn_test3.config(state = 'disabled')
        self.btn_test4.config(state = 'disabled')
        self.btn_summary.config(state = 'disabled')

    #################################################

    def disable_all_btns_but_login(self):
        self.btn_login.config(state = 'normal')
        self.btn_scan.config(state = 'disabled')
        self.btn_test1.config(state = 'disabled')
        self.btn_test2.config(state = 'disabled')
        self.btn_test3.config(state = 'disabled')
        self.btn_test4.config(state = 'disabled')
        self.btn_summary.config(state = 'disabled')

    #################################################

    def disable_log_scan(self):
        self.btn_login.config(state = 'disabled')
        self.btn_scan.config(state = 'disabled')

    #################################################
        
    def disable_login_button(self):
        self.btn_login.config(state = 'disabled')

    #################################################

    def disable_scan_button(self):
        self.btn_scan.config(state = 'disabled')
    
    #################################################


#################################################################################
