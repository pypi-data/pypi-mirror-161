#!/usr/bin/python3

# Importing necessary modules
from audioop import mul
import multiprocessing as mp
import socket
# Imports the GUIWindow
from WagonTestGUI.PythonFiles.GUIWindow import GUIWindow
from WagonTestGUI.PythonFiles.utils.SUBClient import SUBClient
import os

# Creates a task of creating the GUIWindow
def task_GUI(conn, queue):
    # creates the main_window as an instantiation of GUIWindow
    main_window = GUIWindow(conn, queue)

# Creates a task of creating the SUBClient
def task_SUBClient(conn, queue):
    # Creates the SUBSCRIBE Socket Client
    sub_client = SUBClient(conn, queue)

def run():    
    # Creates a Pipe for the SUBClient to talk to the GUI Window
    conn_SUB, conn_GUI = mp.Pipe()

    queue = mp.Queue()

    # Turns creating the GUI and creating the SUBClient tasks into processes
    process_GUI = mp.Process(target = task_GUI, args=(conn_GUI, queue,))
    process_SUBClient = mp.Process(target = task_SUBClient, args = (conn_SUB, queue,))
    

    # Starts the processes
    process_GUI.start()
    process_SUBClient.start()

    # Should hold the code at this line until the GUI process ends
    process_GUI.join()

    try:
        conn_SUB.close()
        conn_GUI.close()
    except:
        print("Pipe close is unnecessary.")

    try:
        # Cleans up the SUBClient process
        process_SUBClient.terminate()
    except:
        print("Terminate is unnecessary.")
        pass

def main(args):
    pass

if __name__ == "__main__":

    curpath = os.path.abspath(os.curdir)
    print( "Current path is: %s" % (curpath))

    print(socket.gethostname())
    ###### Example code to branch between the different GUIS #####
    # visual_GUI_computers = [
    # computer_1,
    # computer_2,
    # etc.
    # ]
    # wagon_GUI_computers = [
    # computer_3,
    # computer_4,
    # etc.
    # ]
    # engine_GUI_computers = [
    # computer_5,
    # computer_6,
    # etc.
    # ]
    # current_computer = socket.gethostname()
    # for computer in visual_GUI_computers:
    #    if current_computer == computer:
    #        run_visual_GUI()
    #    else:
    #        pass
    # for computer in wagon_GUI_computers:
    #    if current_computer == computer:
    #        run_wagon_GUI()
    #    else:
    #        pass
    # for computer in engine_GUI_computers:
    #    if current_computer == computer:
    #        run_engine_GUI()
    #    else:
    #        pass
    ###### END EXAMPLE CODE ######
    run()
