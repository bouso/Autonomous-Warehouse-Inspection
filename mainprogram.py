import time
import numpy as np
import os
import tensorflow as tf
from utils import label_map_util
from utils import visualization_utils as vis_util
import cv2
from djitellopy import Tello
from client import *
from tkinter import *
from tkinter import messagebox
from PIL import ImageTk, Image
import winsound
#---Tkinter Setup---#
tkinter = Tk()  #Makes main window
tkinter.wm_title("UAV Autonomous Warehouse Management")
# tkinter.config(background="#FFFFFF")
tkinter.iconbitmap('SingaporePoly.ico')
my_img = ImageTk.PhotoImage(Image.open("SingaporePolyLogo.png"))
my_label = Label(image=my_img)
my_label.pack()
# imageFrame = Frame(tkinter, width=600, height=500)
# imageFrame.pack(padx=10, pady=2)
labelframe = LabelFrame(tkinter, text="Autonomous UAV Console", font=('Helvetica', 18, 'bold'))
labelframe.place(relx=0.425, rely=0.1)
labelframe.pack(side=LEFT, fill=BOTH, expand=NO, padx=10)
labelframe2 = LabelFrame(tkinter, text="Warehouse Console", font=('Helvetica', 18, 'bold'))
labelframe2.place(relx=0.425, rely=0.1)
labelframe2.pack(side=LEFT, fill=BOTH, expand=NO, padx=10)
labelframe3 = LabelFrame(tkinter, text="Exit Program", font=('Helvetica', 18, 'bold'))
labelframe3.place(relx=0.425, rely=0.1)
labelframe3.pack(side=LEFT, fill=BOTH, expand=NO, padx=10)
# lmain = Label(imageFrame)
# lmain.pack()
buttonframe = Frame(tkinter)
buttonframe.pack()
# frame = Frame(tkinter, text="Main Console", font=('Helvetica', 18, 'bold'))

#---Tello Drone Setup---#
tello = Tello()
tello.connect()
tello.streamon()
tello.set_speed = 0.1
frame_read = tello.get_frame_read()
time.sleep(2)

#---TensorFlow Object Detection Setup--#
MODEL_NAME = 'TensorFlow_Model'
PATH_TO_CKPT = MODEL_NAME + '/frozen_inference_graph.pb'
PATH_TO_LABELS = os.path.join('data', 'object-detection.pbtxt')
NUM_CLASSES = 5 # Indicate the total number of classes

detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.compat.v1.GraphDef()
    with tf.compat.v2.io.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = label_map_util.create_category_index(categories)

def load_image_into_numpy_array(image):
    (im_width, im_height) = image.size
    return np.array(image.getdata()).reshape(
        (im_height, im_width, 3)).astype(np.uint8)

#---Main Program---#
def detection_autonomousmovement():
    my_client()
    with detection_graph.as_default():
        with tf.compat.v1.Session(graph=detection_graph) as sess:
            while True:
                # #---Change Sensor Data from String to Integer---#
                sensor_1 = int(tof1())
                sensor_2 = int(tof2())
                sensor_3 = int(tof3())

                #---ToF sensor data lesser or equals to 200mm, Tello drone will land---#
                if (sensor_1 <= 200) or (sensor_2 <= 200) or (sensor_3 <= 200):
                    tello.land()
                    print("Obstacle Detected *Emergency Landing Activated*")
                    winsound.PlaySound('alert.wav', winsound.SND_FILENAME)

                #---Tkinter Pop-up Message Box---#
                    messagebox.showwarning(title="Emergency Landing",
                                                   message="Obstacle Detected! Emergency Landing Activated")
                    time.sleep(1.5)
                pass

                try:
                    image_np = frame_read.frame
                    image_np_expanded = np.expand_dims(image_np, axis=0)
                    image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
                    boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
                    scores = detection_graph.get_tensor_by_name('detection_scores:0')
                    classes = detection_graph.get_tensor_by_name('detection_classes:0')
                    num_detections = detection_graph.get_tensor_by_name('num_detections:0')
                    (boxes, scores, classes, num_detections) = sess.run(
                        [boxes, scores, classes, num_detections],
                        feed_dict={image_tensor: image_np_expanded})
                    vis_util.visualize_boxes_and_labels_on_image_array(
                        image_np,
                        np.squeeze(boxes),
                        np.squeeze(classes).astype(np.int32),
                        np.squeeze(scores),
                        category_index,
                        use_normalized_coordinates=True,
                        line_thickness=8)

                    objects = []
                    threshold = 0.5
                    for index, value in enumerate(classes[0]):
                        object_dict = {}
                        if scores[0, index] > threshold:
                            object_dict[(category_index.get(value)).get('name').encode('utf8')] = classes[0, index]
                            objects.append(object_dict)
                            for object in objects:
                                key = list(object.keys())[0].decode().split("_")[0]
                                # print("Arrow Detected:",key)
                                # time.sleep(1)

                                #---Main Autonomous control---#
                                if key == "left":
                                    print("Arrow Detected: LEFT")
                                    tello.move_left(40)
                                    time.sleep(0.5)
                                    pass
                                elif key == "up":
                                    print("Arrow Detected: UP")
                                    tello.move_up(20)
                                    time.sleep(0.5)
                                    pass
                                elif key == "down":
                                    print("Arrow Detected: DOWN")
                                    tello.move_down(40)
                                    time.sleep(0.5)
                                    pass
                                elif key == "right":
                                    print("Arrow Detected: RIGHT")
                                    tello.move_right(50)
                                    time.sleep(0.5)
                                    pass
                                elif key == "stop":
                                    print("Landing")
                                    tello.land()
                                    time.sleep(0.5)
                                    pass
                    # image_np.flags.writeable = False
                    #---CV2 VideoStream output---#
                    cv2.imshow('arrow detection', cv2.resize(image_np, (720, 480)))

                except Exception as e:
                        print(f'exc: {e}')
                        pass

                    #---"T" to Take off and "Q" to land---#
                k = cv2.waitKey(1) & 0xFF
                if k == ord('t'):
                    tello.takeoff()
                    pass
                elif k == ord('q'):
                    tello.land()

#---Tkinter GUI Buttons---#

def streamon():
    while True:
        detection_autonomousmovement()
button3 = Button(labelframe, text="Autonomous Mode", width=20, height=3, font=5, borderwidth=5,
                 relief="groove",
                 activebackground="green", activeforeground="blue",
                 command=lambda: threading.Thread(target=streamon).start())
button3.pack(side=TOP,pady=20)
# ---------------------------------------------------------------------------------------------- #
def takeoff():
    tello.takeoff()

button2 = Button(labelframe, text="Take off ",  width=20, height=3, font=5, borderwidth=5,
                 relief="groove",
                 activebackground="green", activeforeground="blue",
                 command=lambda: threading.Thread(target=takeoff).start())
button2.pack(side=TOP,padx=20)
# ---------------------------------------------------------------------------------------------- #
def land():

    tello.land()
button1 = Button(labelframe, text="Land ", width=20, height=3, font=5, borderwidth=5,
                 relief="groove",
                 activebackground="green", activeforeground="blue",
                 command=lambda: threading.Thread(target=land).start())
button1.pack(side=TOP,pady=20)

# ---------------------------------------------------------------------------------------------- #
def stocktaking():
    os.system('python C:/Users/Teddie/Desktop/droneprojhome/inventorycount.py')


button4 = Button(labelframe2, text="Stock Taking", width=20, height=3, font=5, borderwidth=5, relief="groove",
                 activebackground="green", activeforeground="blue",
                 command=lambda: threading.Thread(target=stocktaking).start())

button4.pack(side=TOP, padx=20)


# ---------------------------------------------------------------------------------------------- #
def database():
    os.system('python C:/Users/Teddie/Desktop/droneprojhome/databasemain.py')

button5 = Button(labelframe2, text="Database", width=20, height=3, font=5, borderwidth=5, relief="groove",
                 activebackground="green", activeforeground="blue",
                 command=lambda: threading.Thread(target=database).start())

button5.pack(side=TOP ,pady=20)


# ---------------------------------------------------------------------------------------------- #
def cyclecount():
    os.system('python C:/Users/Teddie/Desktop/droneprojhome/countingcycle.py')


button6 = Button(labelframe2, text="Cycle Counting", width=20, height=3, font=5, borderwidth=5, relief="groove",
                 activebackground="green", activeforeground="blue",
                 command=lambda: threading.Thread(target=cyclecount).start())

button6.pack(side=TOP, padx=20)


# ---------------------------------------------------------------------------------------------- #

def cyclecountresult():
    os.system('python C:/Users/Teddie/Desktop/droneprojhome/resultcyclecount.py')


button7 = Button(labelframe2, text="Cycle Counting Result", width=20, height=3, font=5, borderwidth=5, relief="groove",
                 activebackground="green", activeforeground="blue",
                 command=lambda: threading.Thread(target=cyclecountresult).start())

button7.pack(side=TOP, pady=20)

def stockentry():
    os.system('python C:/Users/Teddie/Desktop/droneprojhome/newstockentry.py')


button4 = Button(labelframe2, text="Stock Entry", width=20, height=3, font=5, borderwidth=5, relief="groove",
                 activebackground="green", activeforeground="blue",
                 command=lambda: threading.Thread(target=stockentry).start())

button4.pack(side=TOP,pady=20)
# ---------------------------------------------------------------------------------------------- #

def exitB():
    os.system('taskkill /f /im python.exe')


exitbutton1 = Button(labelframe3, text="Exit All", width=20, height=2, font=3, borderwidth=5, relief="groove",
                     activebackground="red", activeforeground="blue", command=exitB)

exitbutton1.pack(side=TOP,padx=20)
# ---------------------------------------------------------------------------------------------- #
if __name__ == '__main__':
    tkinter.mainloop()
    threading.Thread(target=streamon()).start()