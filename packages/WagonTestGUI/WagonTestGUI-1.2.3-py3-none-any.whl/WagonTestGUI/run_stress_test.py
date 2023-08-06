# Importing necessary modules
from audioop import mul
import multiprocessing as mp
import socket
# Imports the GUIWindow
from PythonFiles.StressTest import StressTest
from PythonFiles.utils.SUBClient import SUBClient


#####################################################################
#                                                                   #
#            Please go to PythonFiles/StressTest.py                 #
#          to set up the settings for the Stress Test.              #
#         This file is essentially an executable for the            #
#                       stress test script.                         # 
#                                                                   #
#####################################################################


# Creates a task of creating the GUIWindow
def task_GUI(conn, queue):
    # creates the main_window as an instantiation of GUIWindow
    stress_test = StressTest(conn, queue)

# Creates a task of creating the SUBClient
def task_SUBClient(conn, queue):
    # Creates the SUBSCRIBE Socket Client
    sub_client = SUBClient(conn, queue)

def run():    
    # Creates a Pipe for the SUBClient to talk to the GUI Window
    conn_SUB, conn_GUI = mp.Pipe()

    queue = mp.Queue()

    # Turns creating the GUI and creating the SUBClient tasks into processes
    process_test = mp.Process(target = task_GUI, args=(conn_GUI, queue,))
    process_SUBClient = mp.Process(target = task_SUBClient, args = (conn_SUB, queue,))
    

    # Starts the processes
    process_test.start()
    process_SUBClient.start()

    # Should hold the code at this line until the GUI process ends
    process_test.join()

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

if __name__ == "__main__":
    run()
