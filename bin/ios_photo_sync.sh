#!/bin/bash

# Check arguments
if [ "$#" -ne 2 ]; then
	echo "Invalid number of arguments, ios_photo_sync.sh BACKUP_FOLDER DATE where date is a string like year:month:day corresponding to the oldest photo you want to backup"
	echo "Now exiting"
	exit 1
fi

# Check idevicepair is installed
which idevicepair >> /dev/null
if [ $? -ne 0 ]
then
	echo "idevicepair not available on the system"
	exit 1
fi

MOUNTPOINT=/mnt/iphone

echo "iPhone mountpoint is $MOUNTPOINT"

# Association de l'iPhone, attention il doit etrer deverouille
idevicepair pair
if [ $? -ne 0 ]
then
	echo "Failed pairing, try to unlock the phone and retry"
	exit 1
else
	echo "iPhone is paired"
fi

# Creation du point de montage si il nexiste pas deja
if [ ! -d $MOUNTPOINT ]
then
	sudo mkdir -p $MOUNTPOINT
	sudo chown -R $USER $MOUNTPOINT
fi

# Montage
ifuse $MOUNTPOINT
if [ $? -ne 0 ]
then
	echo "Failed to mount iPhone, exiting"
	exit 1
else
	echo "iPhone is mounted"
fi

# Backup
FROM=$MOUNTPOINT
TO=$1
DATE=$2

echo "Try backuping $MOUNTPOINT photos to $TO from date $DATE..."

if [ ! -d $1 ]
then
	echo "Destination folder does not exist, now exiting"
	fusermount -u $MOUNTPOINT
fi

# Python commande
CMD="from iphotosync import iossync; iossync.backup_after_date(\"$FROM\",\"$DATE\",\"$TO\")"
python3 -c "$CMD"

# Wait 1 sec before umount, otherwise it won't...
sleep 1

fusermount -u $MOUNTPOINT

