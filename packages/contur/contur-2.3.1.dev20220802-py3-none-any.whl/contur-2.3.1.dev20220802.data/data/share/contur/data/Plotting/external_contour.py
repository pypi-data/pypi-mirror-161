#!/usr/bin/env python	
import os
import pandas as pd
      
#set up returned lists
pts=[]
onesigma = []
excluded = []
nonexcluded = []
title = []
n = 1

#check the current directory for all files end with .csv and rename the file names by order, if you don't want to rename it, you can comment out the os.rename line and put your own names. Then each of these files are read with dataframe. Current setting is reading max three files, if more files needed, edit the section for n == 4 and n == 5 or further. 
for filename in os.listdir(os.getcwd()):
    if filename.endswith(".csv"):
      
      
      if n == 1:
         os.rename(filename,"ANALYSIS1.csv")
         df1 = pd.read_csv("ANALYSIS1.csv", sep=',')
      if n == 2:
         os.rename(filename,"ANALYSIS2.csv")
         df2 = pd.read_csv("ANALYSIS2.csv", sep=',')
      if n == 3:
         os.rename(filename,"ANALYSIS3.csv")
         df3 = pd.read_csv("ANALYSIS3.csv", sep=',')
         print(filename)
      if n == 4:
         os.rename(filename,"ANALYSIS4.csv")
      if n == 5:
         os.rename(filename,"ANALYSIS5.csv")

        
      n = n + 1


#function returning the parameter points of x and y args and the filtered CL value (>0.68), change the filtering condition as you wish in line 25. Adjust the line number and required x and y args when use (check your own .csv file for details). 
    def extracontour(paramDict):
     
           pts=[]
           onesigma = []
           excluded = []
           nonexcluded = []
           z = []                  #z let here will send a list of data(horizontal)
       
           for i in df1.values:
             temp = dict.fromkeys(paramDict)

             temp["MASS:1000006"] = i[1]
             temp["MASS:1000022"] = i[2]       
             temp["CL"] = i[42]
         
             filtered = {k: v for k, v in temp.items() if v is not None}
             
             temp.clear()
             temp.update(filtered)
  #       
         
             keys = ['MASS:1000006','MASS:1000022','CL']

             excluded.append(temp.get("CL"))

             filtered_CL = {k: v for k, v in temp.items() if k is not "CL"}

             pts.append(filtered_CL)
        
         #  print(pts)                        
           return pts,excluded


#if a second file exsits, this function will output the data for plotting the second contour line.                
    def anothercontour(paramDict):

     
           pts=[]
           onesigma = []
           excluded = []
           nonexcluded = []
           z = []                  #z let here will send a list of data(horizontal)
       
           for i in df2.values:
             temp = dict.fromkeys(paramDict)

             temp["MASS:1000005"] = i[1]
             temp["MASS:1000022"] = i[2]       
             temp["CL"] = i[42]
         
             filtered = {k: v for k, v in temp.items() if v is not None}
           
             temp.clear()
             temp.update(filtered)
  #     
         
             excluded.append(temp.get("CL"))

             filtered_CL = {k: v for k, v in temp.items() if k is not "CL"}

             pts.append(filtered_CL)
        
         #  print(filename)                        
           return pts,excluded



         
#uncomment this function if a third contour is needed, if further contour lines required, please name the function with another name and do the copy and paste again for a fourth function. 

#    def thridcontour(paramDict):
     
#           pts=[]
#           onesigma = []
#           excluded = []
#           nonexcluded = []
#           z = []                  #z let here will send a list of data(horizontal)
       
#           for i in df3.values:
#             temp = dict.fromkeys(paramDict)

#             temp["MASS:1000006"] = i[1]
#             temp["MASS:1000022"] = i[2]       
#             temp["CL"] = i[41]
         
#             if temp["CL"] < 0.68:
#                temp["CL"] = 0
         
#             filtered = {k: v for k, v in temp.items() if v is not None}
#             
#             temp.clear()
#             temp.update(filtered)
  #       z.append(temp)


#             excluded.append(temp.get("CL"))

 #            filtered_CL = {k: v for k, v in temp.items() if k is not "CL"}

  #           pts.append(filtered_CL)
        
          # print(pts)                        
   #        return pts,excluded

#number of function should match the number of contour lines needed. 
