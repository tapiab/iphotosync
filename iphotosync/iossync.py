#!/usr/bin/env python

import os
import shutil
import subprocess
import exiftool

def mount_idevice(mountpoint: str):
    #Check not mounted?: TODO
    try:
        subprocess.run(['ifuse',mountpoint])
        print('idevice mounted on {}'.mountpoint)
    except:
        print('Error while mounting idevice, check the following points : ifuse is installed, mountpoint exists and you have the permissions on it')

def list_dcim_folder(mountpoint: str):
    return [ os.path.join(mountpoint,'DCIM',x) for x in os.listdir(os.path.join(mountpoint,'DCIM')) if 'APPLE' in x]

def get_photos_list(mountpoint:str):
    photos = list()
    for f in list_dcim_folder(mountpoint):
        for (dirpath,dirnames,filenames) in os.walk(f):
            for photo_file in filenames:
                if '.HEIC' in photo_file or '.JPG' in photo_file:
                    photos.append(os.path.join(f,photo_file))
            break
    
    with exiftool.ExifTool() as et:
        metadata = et.get_metadata_batch(photos)
    
    return metadata

def get_photos_after_date(mountpoint: str, date:str):
    """
    Date format in EXIF yyyy:mm:dd, look for EXIF:CreateDate
    """
    metadata = get_photos_list(mountpoint)
    filtered_meta = dict()
    for m in metadata:
        if 'EXIF:CreateDate' in m:
            if is_after(m['EXIF:CreateDate'].split(' ')[0],date):
                filtered_meta.update(m)
        else:
            print(m)
    return filtered_meta


def is_after(date, origin):
    """
    return True if date is after origin
    """
    #Let's split the strings
    year,month,day=date.split(':')
    oyear, omonth, oday = origin.split(':')
    if year >= oyear and month >= omonth and day >= oday:
        return True
    else:
        return False
    

def convert_from_heif_to_jpg(filename_in, filemane_out):
    subprocess.run(['heif-convert',filename_in,filemane_out])
