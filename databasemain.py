import mysql.connector
from tkinter import *

#--Tkinter setup--#
root = Tk()
root.geometry("400x350")
root.title("Database")

#--Database Login Info--#
db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="root",
    database="testdatabase"
)
mycursor = db.cursor()
mycursor.execute("SELECT * FROM warehouse")
e = Label(root, width=10, text='Item Name', borderwidth=2, relief='ridge', anchor='w', font=10, bg='yellow')
e.grid(row=0, column=0)
e = Label(root, width=10, text='Quantity', borderwidth=2, relief='ridge', anchor='w', font=10, bg='yellow')
e.grid(row=0, column=1)
e = Label(root, width=10, text='Item ID', borderwidth=2, relief='ridge', anchor='w', font=10, bg='yellow')
e.grid(row=0, column=2)

def tabledb():
    i = 1
    for warehouse in mycursor:
        for j in range(len(warehouse)):
            e = Label(root, width=10,text=warehouse[j],borderwidth=2,relief='ridge',anchor='w',font=5)
            e.grid(row=i, column=j)
        i = i + 1
        e.after(1000,tabledb)

if __name__ == '__main__':
    tabledb()
    root.mainloop()