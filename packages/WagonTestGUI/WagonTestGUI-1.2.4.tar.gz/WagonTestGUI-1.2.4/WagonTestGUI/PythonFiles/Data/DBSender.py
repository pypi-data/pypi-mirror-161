import requests
import json
import WagonTestGUI
# from read_barcode import read_barcode


class DBSender():

    # Empty constructor
    def __init__(self) :
        pass


    def add_new_user_ID(self, user_ID, passwd):
        r = requests.post('http://cmslab3.umncmslab/~cros0400/cgi-bin/add_tester2.py', data= {'person_name':user_ID, 'password': passwd})



    # Returns an acceptable list of usernames from the database
    def get_usernames(self):
        r = requests.get('http://cmslab3.umncmslab/~cros0400/cgi-bin/get_usernames.py')
        lines = r.text.split('\n')


        begin = lines.index("Begin") + 1
        end = lines.index("End")

        usernames = []

        for i in range(begin, end):
            temp = lines[i]
            usernames.append(temp)

        return usernames

        

    # Returns a list of booleans
    # Whether test (by index) has been completed or not
    def get_test_completion_staus(self, serial_number):
        r = requests.post('http://cmslab3.umncmslab/~cros0400/cgi-bin/get_test_completion_status.py', data= serial_number)
        
        lines = r.text.split('\n')
        begin = lines.index("Begin") + 1 
        end = lines.index("End")
        
        tests_completed = []
        for i in range(begin, end):
            temp = lines[i][1:-1].split(",")
            temp[0] = str(temp[0])
            temp[1] = int(temp[1])
            tests_completed.append(temp)

        return tests_completed



    # Returns a list of booleans
    # Whether or not DB has passing results 
    def get_previous_test_results(self, serial_number):
        r = requests.post('http://cmslab3.umncmslab/~cros0400/cgi-bin/get_previous_test_results.py', data={'serial_number': str(serial_number)})
        
        lines = r.text.split('\n')

        begin = lines.index("Begin") + 1
        end = lines.index("End")

        tests_passed= []


        for i in range(begin, end):
            temp = lines[i][1:-1].split(",")
            temp[0] = str(temp[0])
            temp[1] = int(temp[1])
            tests_passed.append(temp)

        return tests_passed

    
    
    # #TODO Verify if a board has already been instantiated with SN
    # Posts a new board with passed in serial number
    def add_new_board(self, sn):
        r = requests.post('http://cmslab3.umncmslab/~cros0400/cgi-bin/add_module2.py', data={"serial_number": str(sn)})





    def is_new_board(self, sn):
        
        r = requests.post('http://cmslab3.umncmslab/~cros0400/cgi-bin/is_new_board.py', data={"serial_number": str(sn)})
        
        lines = r.text.split('\n')
       
        begin = lines.index("Begin") + 1
        end = lines.index("End")

    
        for i in range(begin, end): 
            
            if lines[i] == "True":
                return True
            elif lines[i] == "False":
                return False






    # Posts information via the "info" dictionary
    # Serial number is within the info dictionary
    def add_board_info(self, info):
        r = requests.post('http://cmslab3.umncmslab/~cros0400/cgi-bin/add_board_info2.py', data = info)
    
    def add_initial_tests(self, results):
        r = requests.post('http://cmslab3.umncmslab/~cros0400/cgi-bin/add_init_test.py', data = results)
        
    def add_general_test(self, results, files):
        r = requests.post('http://cmslab3.umncmslab/~cros0400/cgi-bin/add_test2.py', data = results, files=files)

    def add_test_json(self, json_file, datafile_name):
        load_file = open(json_file)
        results = json.load(load_file)        
        load_file.close()

        datafile = open(datafile_name, "rb")        

        attach_data = {'attach1': datafile}
        print("Read from json file:", results)
        r = requests.post('http://cmslab3.umncmslab/~cros0400/cgi-bin/add_test_json.py', data = results, files = attach_data)


 # Returns a list of all different types of tests
    def get_test_list(self):
        r = requests.get('http://cmslab3.umncmslab/~cros0400/cgi-bin/get_test_types.py')

        lines = r.text.split('\n')

        begin = lines.index("Begin") + 1
        end = lines.index("End")

        tests = []

        for i in range(begin, end):
            temp = lines[i][1:-1].split(",")
            temp[0] = str(temp[0][1:-1])
            temp[1] = int(temp[1])
            tests.append(temp)

        return tests

