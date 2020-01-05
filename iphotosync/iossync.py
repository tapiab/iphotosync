#!/usr/bin/env python

import os
import shutil
import subprocess
import exiftool
from shutil import copy

def mount_idevice(mountpoint: str):
    #Check not mounted?: TODO
    try:
        subprocess.run(['ifuse',mountpoint])
        print('idevice mounted on {}'.mountpoint)
    except:
        print('Error while mounting idevice, check the following points : ifuse is installed, mountpoint exists and you have the permissions on it')

def list_dcim_folder(mountpoint: str):
    return [ os.path.join(mountpoint,'DCIM',x) for x in os.listdir(os.path.join(mountpoint,'DCIM')) if 'APPLE' in x]

def listdir_abs(root:str):
    return [os.path.join(root,x) for x in os.listdir(root)]

def get_file_list(mountpoint:str):
    return [item for sublist in list(map(listdir_abs, list_dcim_folder(mountpoint))) for item in sublist]

def get_photos_list(mountpoint:str):
    photos = list(filter(lambda filename: '.JPG'in filename or '.HEIC' in filename,get_file_list(mountpoint)))
    with exiftool.ExifTool() as et:
        metadata = et.get_metadata_batch(photos)
    
    return metadata

def get_photos_after_date(mountpoint: str, date:str):
    """
    Date format in EXIF yyyy:mm:dd, look for EXIF:CreateDate
    """
    metadata = get_photos_list(mountpoint)
    filtered_meta = list()
    for m in metadata:
        if 'File:FileModifyDate' in m:
            if is_after(m['File:FileModifyDate'].split(' ')[0],date):
                filtered_meta.append(m)
    return filtered_meta

def is_after(date, origin):
    """
    return True if date is after origin
    """
    #Let's split the strings
    year,month,day=date.split(':')
    oyear, omonth, oday = origin.split(':')
    if year > oyear:
        return True
    elif year == oyear and month > omonth:
        return True
    elif year == oyear and month == omonth and day >= oday :
        return True
    else:
        return False
    
def backup_after_date(mountpoint: str, date: str, backup_dir:str):
    """
    Copy the photos after the given date
    """
    for item in get_photos_after_date(mountpoint,date):
        if '.HEIC' in item['SourceFile']:
            new_name = item['File:FileName'].replace('HEIC','JPG')
            date = item['File:FileModifyDate'].split(' ')[0].replace(':','.')
            new_name = date + '_' + new_name
            convert_from_heif_to_jpg(item['SourceFile'],os.path.join(backup_dir,new_name))
        else:
            new_name = item['File:FileModifyDate'].split(' ')[0].replace(':','.') + '_' + item['File:FileName']
            copy(item['SourceFile'],os.path.join(backup_dir,new_name))
        

def convert_from_heif_to_jpg(filename_in, filemane_out):
    subprocess.run(['heif-convert',filename_in,filemane_out])
