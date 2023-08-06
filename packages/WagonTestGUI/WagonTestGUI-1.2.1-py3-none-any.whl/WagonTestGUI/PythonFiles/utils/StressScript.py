import string    
import random 
from random import randint


class StressScript():
    def __init__(self, conn):
        # Set random test_length within a range. Meant to be close to 3-5 min.
        test_length = randint(500,1500)
        i = 0
        while i < test_length:
            # Creates random strings of 10 characters and sends them until the test length has been reached.
            S = 10  
            ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k = S))
            conn.send(ran)
            i += 1
        conn.send("Done.")
        conn.send("Run completed")
        
