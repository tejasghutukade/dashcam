import RPi.GPIO as GPIO
import time


GPIO.setmode(GPIO.BCM)


GPIO.setup(17, GPIO.IN) # Ignition Status
GPIO.setup(18,GPIO.OUT,initial = GPIO.HIGH) #Power continuation Output High=KeepON, Low=SHutDown




try:
   ignition = GPIO.input(17)
   while ignition:
      ignition = GPIO.input(17)
      print("ignition Status - Ignition ON")
      time.sleep(1)
      if(not ignition):                
         break  

   print('Ignition Turned OFF')
   print("Upload will start")
   time.sleep(60)
except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
   print("Keyboard interrupt")
   #GPIO.cleanup()
   
except Exception  as e:
   print(e)
   #GPIO.cleanup()

finally:
   print("clean up") 
   GPIO.cleanup()    
                      
        