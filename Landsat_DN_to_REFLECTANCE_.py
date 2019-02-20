# -*- coding: utf-8 -*-
"""
Created on Wed Feb 20 21:44:03 2019

@author: Юлия
"""

import gdal
import os
import re
import math

directory=[]
print('Введите расположение папки с файлами:')
directory = str(input())
folder=os.listdir(directory)
directories=[]
for i in range (len(folder)):
    path=directory+'\\'+folder[i]                         
    directories.append(path)                                                                                      #создание списка с расположением файлов
    for i in range (len(directories)):
        OpenedFile=gdal.Open(directories[i])
        if OpenedFile==None:
            raise Exception('Ошибка в чтении файла ' + directories[i])
k=0  
print('Введите путь к метаданным (.TXT): ')
metfile_directory=str(input())


print('Введите путь к папке для полученных изображений: ')
result_folder=str(input())

with open (metfile_directory,'r') as MTL:
    lines=MTL.readlines()
    
    for i in range (0, len(lines)):
        lines[i]=lines[i][:-1]  
  
for i in range (0, len(lines)):    
    landsat_N=re.search(r'SPACECRAFT_ID', lines[i])
    if landsat_N!=None:
        landsat_NUMBER=lines[i].split('"')[1]                                                          
        if landsat_NUMBER=='LANDSAT_1' or landsat_NUMBER=='LANDSAT_2':
            raise Exception('Расчет производится только для спутников Landsat 3 и выше, предоставленные данные сняты спутником: ' + landsat_NUMBER)
        k=1          
if k!=1:
    raise Exception('Ошибка в чтении файла ' + metfile_directory)
print(landsat_NUMBER)

Mr_FOR_ALL_BANDS=[]
Ar_FOR_ALL_BANDS=[]
for i in range (0,len(lines)):
    Mr=re.search(r'REFLECTANCE_MULT', lines[i])
    if Mr!=None:
        Mr_FOR_ALL_BANDS.append(lines[i])                                      
    Ar=re.search(r'REFLECTANCE_ADD', lines[i])
    if Ar!=None:
        Ar_FOR_ALL_BANDS.append(lines[i])                                       
    sun_el=re.search(r'SUN_ELEVATION', lines[i])
    if sun_el!=None:
        TETTA_degrees=lines[i].split('= ')[1]                                   
        TETTA=math.radians(float(TETTA_degrees))
 
'''Начинаем открывать по одному снимку и считать для них альбедо (REFLECTANCE)'''
for i in range (0, len(Mr_FOR_ALL_BANDS)):
    band_number_pre=directories[i].split('_B')[1]
    band_number=band_number_pre.split('.')[0]
    a=Mr_FOR_ALL_BANDS[i].split('BAND_')[1]
    b=a.split(' =')[0]
    if b==band_number:
        Mr_for_band=Mr_FOR_ALL_BANDS[i].split('= ')[1]                   
    c=Ar_FOR_ALL_BANDS[i].split('BAND_')[1]
    d=c.split(' =')[0]
    if d==band_number:
        Ar_for_band=Ar_FOR_ALL_BANDS[i].split('= ')[1]                     
    print('Band number: ' + band_number)
    
    
    image=gdal.Open(directories[i])
    datatype = gdal.GDT_Float64
    driver = gdal.GetDriverByName("GTiff")
    xsize = image.RasterXSize
    ysize = image.RasterYSize
    projection = image.GetProjection()
    transform = image.GetGeoTransform()
    mass=image.GetRasterBand(1).ReadAsArray()
    R=float(Mr_for_band)*mass + float(Ar_for_band)
    reflectance = R/math.sin(TETTA)
    
   
    name=directories[i].split('\\')[-1]
    outRaster = driver.Create( result_folder + '/REFLECTANCE_' + name, xsize, ysize, 1, datatype)
    outRaster.SetProjection( projection )
    outRaster.SetGeoTransform( transform )
    outRaster.GetRasterBand( 1 ).WriteArray( reflectance )
outRaster=None
print('Completed')