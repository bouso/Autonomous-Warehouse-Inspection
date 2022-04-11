import cv2
import numpy as np
from pyzbar.pyzbar import decode
import mysql.connector
import winsound
import os

db = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="root",
        database="testdatabase"
    )
mycursor = db.cursor()

cap = cv2.VideoCapture(0)
cap.set(3,640)
cap.set(4,480)

# mycursor.execute("CREATE TABLE warehouse (item VARCHAR(50), quantity SMALLINT , itemID SMALLINT)")

def stockentry():
    while True:
        success, img = cap.read()
        for barcode in decode(img):
            myData = barcode.data.decode('utf-8')
            myString = myData
            myList = myString.split(" ")
            winsound.PlaySound('beep.wav', winsound.SND_FILENAME)

            mycursor.execute("INSERT INTO warehouse (item, quantity, itemID) VALUES ('%s', '%s', '%s')" %tuple(myList))
            mycursor.execute("CREATE TABLE tem LIKE warehouse")
            mycursor.execute("INSERT INTO tem SELECT DISTINCT * FROM warehouse")
            mycursor.execute("DROP TABLE warehouse")
            mycursor.execute("RENAME TABLE tem TO warehouse")
            db.commit()
            mycursor.execute("SELECT * FROM warehouse")
            for x in mycursor:
                print(x)

            pts = np.array([barcode.polygon], np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(img, [pts], True, (0, 0, 255), 5)
            pts2 = barcode.rect
            cv2.putText(img, myData, (pts2[0], pts2[1]), cv2.FONT_HERSHEY_COMPLEX, 0.9, (0, 0, 255), 2)

        cv2.imshow('Stock Entry', img)
        cv2.waitKey(1)

if __name__ == '__main__':
    stockentry()