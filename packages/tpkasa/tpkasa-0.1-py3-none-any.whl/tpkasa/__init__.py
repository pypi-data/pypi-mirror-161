# -*- coding: utf-8 -*-
"""
Created on Wed Jul 27 19:25:54 2022

@author: franc
"""


import subprocess


class SmartPlug:

    
    def __init__(self,ip_address):
        self.ip_address = ip_address
        self.status = False
        self.change_status()

        
    def change_status(self):
        
        if(self.status):
            option = "on"
        else:
            option = "off"

        p = subprocess.Popen(f"kasa --host {self.ip_address} {option}")
        (output, err) = p.communicate()  
        p_status = p.wait()


    def __call__(self,s):
        
        s = s == 1
        if( s & (self.status == False) ):
            self.status = True
            self.change_status()
        elif( (s == False) & self.status ):
            self.status = False
            self.change_status()
