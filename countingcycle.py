import cv2
import numpy as np
from pyzbar.pyzbar import decode
import mysql.connector
import threading
import time

# --Database Login Info--#
db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="root",
    database="testdatabase"
)
mycursor = db.cursor()

# --Creating new table in mySQL database--#
# mycursor.execute("CREATE TABLE cyclecount (item VARCHAR(50), quantity SMALLINT , itemID SMALLINT)")

# --OpenCV Video Stream--#
cap = cv2.VideoCapture('http://192.168.0.224:9000/stream.mjpg')

if not cap.isOpened():
    print("Cannot open camera")
    exit()


# --OpenCV Video Stream Output--#
def stream():
    cv2.imshow('Cycle Counting', img)
    cv2.waitKey(1)


# --Database Query--#
def database():
    mycursor.execute("INSERT INTO cyclecount (item, quantity, itemID) VALUES ('%s', '%s', '%s')" % tuple(myList))
    mycursor.execute("CREATE TABLE tem LIKE cyclecount")
    mycursor.execute("INSERT INTO tem SELECT DISTINCT * FROM cyclecount")
    mycursor.execute("DROP TABLE cyclecount")
    mycursor.execute("RENAME TABLE tem TO cyclecount")
    db.commit()

# --main program--#
def scan():
    global myList, img
    while True:
        success, img = cap.read()
        if success:
            for barcode in decode(img):
                myData = barcode.data.decode('utf-8')
                myString = myData
                myList = myString.split(" ")
                # --import database function--#
                database()
                pts = np.array([barcode.polygon], np.int32)
                pts = pts.reshape((-1, 1, 2))
                cv2.polylines(img, [pts], True, (0, 0, 255), 5)
                pts2 = barcode.rect
                cv2.putText(img, myData, (pts2[0], pts2[1]), cv2.FONT_HERSHEY_COMPLEX, 0.9, (0, 0, 255), 2)

            ###import stream function###
            stream()


# --Activate scan function--#
if __name__ == '__main__':
    scan()
    p1 = threading.Thread(target=stream).start()
    p3 = threading.Thread(target=database).start()
    p2 = threading.Thread(target=scan).start()
