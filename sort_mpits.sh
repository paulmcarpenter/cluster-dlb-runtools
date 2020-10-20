#!/bin/bash

#EXAMPLE 
#TRACE@r1i3n23.0000065214000011000000.mpit
# r1i3n23 -> node name
# 0000065214 -> PID
# 000011 -> MPI Task ID
# 000000 -> Thread ID (inside MPI Task)

#SORTING 
# It must be sorted by MPI Task ID.
AUX_FILE=aux.txt
OUTPUT_FILE=sorted_mpit_list.txt
FILES=$(ls set-0/*.mpit)

for FILENAME in $FILES 
do
    PREFIX=$(echo $FILENAME | cut -d'@' -f1)
    NODEPIDTIDTHID=$(echo $FILENAME | cut -d'@' -f2)
    NODE=$(echo $NODEPIDTIDTHID | cut -d'.' -f1)
    PIDTIDTHID=$(echo $NODEPIDTIDTHID | cut -d'.' -f2) 
    PID=$(echo $PIDTIDTHID | cut -c1-10) 
    TID=$(echo $PIDTIDTHID | cut -c11-16)
    THID=$(echo $PIDTIDTHID | cut -c17-22)
#    echo $PREFIX
#    echo $NODEPIDTIDTHID
#    echo $NODE
#    echo $PIDTIDTHID
#    echo $PID
#    echo $TID
#    echo $THID
    echo ${TID}_${THID}_${PID}_${NODE} >> $AUX_FILE
done

sort $AUX_FILE -o $AUX_FILE 

PREFIX="set-0/TRACE@"
cat $AUX_FILE | while read LINE
do
    TID=$(echo $LINE | cut -d'_' -f1)
    THID=$(echo $LINE | cut -d'_' -f2)
    PID=$(echo $LINE | cut -d'_' -f3)
    NODE=$(echo $LINE | cut -d'_' -f4)
#    echo $TID
#    echo $THID
#    echo $PID
#    echo $NODE
    echo ${PREFIX}${NODE}.${PID}${TID}${THID}.mpit >> $OUTPUT_FILE
done

rm $AUX_FILE
