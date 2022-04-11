import socket
import threading

HOST = '192.168.0.224'  # The server's hostname or IP address
PORT = 65432       # The port used by the server

def process_data_from_server(x):        # Define function to split Incoming Data
    sensor1, sensor2, sensor3 = x.split()

    return sensor1, sensor2, sensor3


def my_client():
    global data,tof_1,tof_2,tof_3
    #--DO NOT send Request to often or you will crash server--#
    threading.Timer(5, my_client).start()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:  # define socket TCP
        s.connect((HOST, PORT))

        my_inp = 'Data'

        # encode the message
        my_inp = my_inp.encode('utf-8')

        # send request to server
        s.sendall(my_inp)

        # Get the Data from Server and process the Data
        data = s.recv(1024).decode('utf-8')
        # # Process the data i mean split comma separated value

        tof_1, tof_2, tof_3= process_data_from_server(data)
        print('Sensor 1: {}'.format(tof_1))
        print('Sensor 2: {}'.format(tof_2))
        print('Sensor 3: {}'.format(tof_3))
        s.close()

def tof1():
    sensor_1 = tof_1
    return sensor_1

def tof2():
    sensor_2 = tof_2
    return sensor_2

def tof3():
    sensor_3 = tof_3
    return sensor_3

if __name__ == "__main__":
    while True:
        my_client()

