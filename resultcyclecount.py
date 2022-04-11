import mysql.connector
from tkinter import *

#--Tkinter setup--#
root = Tk()
root.geometry("600x350")
root.title("Cycle Counting Results")

#--Database Login Info--#
db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="root",
    database="testdatabase"
)
mycursor = db.cursor()
mycursor.execute("INSERT INTO cycleresults SELECT t1.* from warehouse t1 left outer join cyclecount t2 on t1.itemID=t2.itemID where t2.itemID is null"
                 " UNION ALL SELECT t2.* from warehouse t1 right outer join cyclecount t2 on t1.itemID=t2.itemID where t1.itemID is null;")
mycursor.execute("CREATE TABLE ctemp LIKE cycleresults")
mycursor.execute("INSERT INTO ctemp SELECT DISTINCT * FROM cycleresults")
mycursor.execute("DROP TABLE cycleresults")
mycursor.execute("RENAME TABLE ctemp TO cycleresults")
mycursor.execute("SELECT * FROM cycleresults")

e = Label(root, width=16, text='Missing Item Name', borderwidth=2, relief='ridge', anchor='w', font=10, bg='red')
e.grid(row=0, column=0)
e = Label(root, width=16, text='Quantity', borderwidth=2, relief='ridge', anchor='w', font=10, bg='red')
e.grid(row=0, column=1)
e = Label(root, width=16, text='Item ID', borderwidth=2, relief='ridge', anchor='w', font=10, bg='red')
e.grid(row=0, column=2)

def tabledb():
    i = 1
    for warehouse in mycursor:
        for j in range(len(warehouse)):
            e = Label(root, width=16,text=warehouse[j],borderwidth=2,relief='ridge',anchor='w',font=5)
            e.grid(row=i, column=j)
        i = i + 1
        e.after(1000,tabledb)

if __name__ == '__main__':
    tabledb()
    root.mainloop()
    mycursor.execute("TRUNCATE cycleresults;")