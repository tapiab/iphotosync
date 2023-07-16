import os
import exiftool
import typer
import sh
import logging
from shutil import copy

logging.basicConfig(level=logging.INFO)
mountpoint = "/mnt/iphone"
app = typer.Typer()


def check_environment():
    if not sh.which("idevicepair"):
        logging.info("idevice pair is missing")
        typer.Exit()

    if not sh.which("ifuse"):
        logging.info("ifuse is missing")
        typer.Exit()

    if not sh.which("heif-convert"):
        logging.info("heif-convert is missing")
        typer.Exit()


def mount_idevice():
    with sh.contrib.sudo:
        sh.idevicepair("pair")

    logging.info("device is paired")

    with sh.contrib.sudo:
        sh.ifuse(mountpoint)

    logging.info(f"device is mounted on {mountpoint}")


@app.command("run")
def run(date: str, backup_dir: str):
    check_environment()
    mount_idevice()
    # backup_after_date(date, backup_dir)


def list_dcim_folder():
    return [os.path.join(mountpoint, 'DCIM', x) for x in os.listdir(os.path.join(mountpoint, 'DCIM')) if 'APPLE' in x]


def listdir_abs(root: str):
    return [os.path.join(root, x) for x in os.listdir(root)]


def get_file_list():
    return [item for sublist in list(map(listdir_abs, list_dcim_folder())) for item in sublist]


def get_media_list():
    media = list(
        filter(lambda filename: '.JPG' in filename or '.HEIC' in filename or '.MOV' in filename or '.mov' in filename,
               get_file_list()))
    with exiftool.ExifToolHelper() as et:
        metadata = et.get_metadata(media)

    return metadata


def get_media_after_date(date: str):
    """
    Date format in EXIF yyyy:mm:dd, look for EXIF:CreateDate
    """
    metadata = get_media_list()
    filtered_meta = list()
    for m in metadata:
        if 'File:FileModifyDate' in m:
            if is_after(m['File:FileModifyDate'].split(' ')[0], date):
                filtered_meta.append(m)
    return filtered_meta


def is_after(date, origin):
    """
    return True if date is after origin
    """
    year, month, day = date.split(':')
    oyear, omonth, oday = origin.split(':')
    if year > oyear:
        return True
    elif year == oyear and month > omonth:
        return True
    elif year == oyear and month == omonth and day >= oday:
        return True
    else:
        return False


def backup_after_date(date: str, backup_dir: str):
    """
    Copy the photos after the given date
    """
    for item in get_media_after_date(date):
        if '.HEIC' in item['SourceFile']:
            new_name = item['File:FileName'].replace('HEIC', 'JPG')
            date = item['File:FileModifyDate'].split(' ')[0].replace(':', '-')
            hour = item['File:FileModifyDate'].split(' ')[1].split('+')[0].replace(':', '-')
            new_name = date + '_' + hour + '_' + new_name
            convert_from_heif_to_jpg(item['SourceFile'], os.path.join(backup_dir, new_name))
        elif '.MOV' in item['SourceFile'] or '.mov' in item['SourceFile']:
            date = item['QuickTime:MediaCreateDate'].split(' ')[0].replace(':', '-')
            hour = item['QuickTime:MediaCreateDate'].split(' ')[1].split('+')[0].replace(':', '-')
            new_name = date + '_' + hour + '_' + item['File:FileName']
            copy(item['SourceFile'], os.path.join(backup_dir, new_name))
        else:
            date = item['File:FileModifyDate'].split(' ')[0].replace(':', '-')
            hour = item['File:FileModifyDate'].split(' ')[1].split('+')[0].replace(':', '-')
            new_name = date + '_' + hour + '_' + item['File:FileName']
            copy(item['SourceFile'], os.path.join(backup_dir, new_name))


def convert_from_heif_to_jpg(filename_in, filename_out):
    sh.heif_convert(filename_in, filename_out)


if __name__ == "__main__":
    typer.run(run)