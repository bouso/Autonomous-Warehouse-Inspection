import cv2
import numpy as np
from pyzbar.pyzbar import decode
import mysql.connector
import threading
import time

#--Database Login Info--#
db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="root",
    database="testdatabase"
)
mycursor = db.cursor()

#--Creating new table in mySQL database--#
# mycursor.execute("CREATE TABLE warehouse (item VARCHAR(50), quantity SMALLINT , itemID SMALLINT)")

#--OpenCV Video Stream--#
cap = cv2.VideoCapture('http://192.168.0.224:9000/stream.mjpg')
# cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()

#--OpenCV Video Stream Output--#
def stream():
    cv2.imshow('Stock Taking', img)
    cv2.waitKey(1)

#--Database Query--#
def database():
    mycursor.execute("UPDATE warehouse SET item = '%s', quantity = quantity + '%s' WHERE itemID = %s " % tuple(myList))
    mycursor.execute("CREATE TABLE temp6 LIKE warehouse")
    mycursor.execute("INSERT INTO temp6 SELECT DISTINCT * FROM warehouse")
    mycursor.execute("DROP TABLE warehouse")
    mycursor.execute("RENAME TABLE temp6 TO warehouse")
    db.commit()

#--main program--#
def scan():
    global img, myList
    while cap.isOpened():
        success, img = cap.read()
        if success:
            for barcode in decode(img):
                myData = barcode.data.decode('utf-8')
                myString = myData
                myList = myString.split(" ")
                print(myList)
                # --import database function--#\
                database()
                pts = np.array([barcode.polygon], np.int32)
                pts = pts.reshape((-1, 1, 2))
                cv2.polylines(img, [pts], True, (0, 0, 255), 5)
                pts2 = barcode.rect
                cv2.putText(img, myData, (pts2[0], pts2[1]), cv2.FONT_HERSHEY_COMPLEX, 0.9, (0, 0, 255), 2)

        ###import stream function###
        stream()
    # list(a.pop())

#--Activate scan function--#
if __name__ == '__main__':
    scan()
    p2 = threading.Thread(target=scan).start()
    p1 = threading.Thread(target=stream).start()
    p3 = threading.Thread(target=database).start()
