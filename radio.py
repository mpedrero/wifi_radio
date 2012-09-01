import serial, subprocess, time, shlex, threading, sys, urllib2

# Sets the serial connection
print "Opening serial port..."
portOpened = False

while(not portOpened):
	if(sys.platform == 'win32'):
		try:
			ser = serial.Serial('COM4', 9600, rtscts=1)
			ser.close()
			ser = serial.Serial('COM4', 9600)
		except:
			print "Could not open port"
	else:
		try:
			ser = serial.Serial('/dev/ttyUSB0', 9600, rtscts=1)
			ser.close()
			ser = serial.Serial('/dev/ttyUSB0', 9600)
		except:
			print "Could not open port"
	
	if(ser.name != ""):
		print "Port opened!",ser
		portOpened = True
	else:
		print "Port can't be opened, retrying..."
		portOpened = False

# Trying with infinite timeout
ser.timeout = None


# Globals
isPlaying = False
# Locks
isPlayingLock = threading.Lock()

'''This function receives button interaction from Arduino and respond to them'''	
def button_receiver():
	print "Receiver started"
	global isPlaying
	while(True):
		serial_in = ser.readline();
		serial_out = ""
		
		if(serial_in == 'BTNSEL\r\n'):
			if(not isPlaying):
				print "[A->R] Received SEL: Playing..."
				# Put mpc to play
				args = shlex.split("mpc play")
				subprocess.check_output(args)
				# Send the info to Arduino
				serial_out = "DW Play"
				serial_out += '\n'
				ser.write(serial_out)
				serial_out = ""
				# Sets isPlaying to True
				time.sleep(1)
				isPlayingLock.acquire()
				try:
					isPlaying = True
				finally:
					isPlayingLock.release()
			else:
				print "[A->R] Received SEL: Stopping..."
				# Sets isPlaying to False
				isPlayingLock.acquire()
				try:
					isPlaying = False
				finally:
					isPlayingLock.release()
				# Stop mpc
				args = shlex.split("mpc stop")
				subprocess.check_output(args)
				# Send the info to Arduino
				serial_out = "DW Stop"
			
		elif(serial_in == 'BTNLFT\r\n'):
			serial_out = "DW BTNLFT OK"
		elif(serial_in == 'BTNRGT\r\n'):
			serial_out = "DW BTNRGT OK"
		elif(serial_in == 'BTNUP\r\n'):
			serial_out = "DW BTNUP OK"
		elif(serial_in == 'BTNDWN\r\n'):
			serial_out = "DW BTNDWN OK"
			
		if(serial_out != ""):
			print "[R->A]",serial_out
			serial_out += '\n'
			ser.write(serial_out)
		else:
			pass
			#print "No data"
		#time.sleep(2)
	
'''This function sends display updates to arduino'''	
def display_sender():
	global isPlaying
	
	print "Sender started"
	
	# Strings to ask things to mpc
	com_radio = 'mpc current -f "%name%"'
	com_song = 'mpc current -f "%title%"'
	
	# String to send over serial
	serial_out = ""
	
	while(True):
		if (isPlaying):
			args = shlex.split(com_song)
			str_song = subprocess.check_output(args)
			list = str_song.split(' - ')

			serial_out = "UP "
			try:
				serial_out += list[0]
			except IndexError:
				serial_out += "Unknown artist"
			serial_out += '\n'
			ser.write(serial_out)
			#print "[DISPLAY_SENDER] RPi -> Ard:",serial_out

			
			serial_out = "DW "
			try:
				serial_out += list[1]
			except IndexError:
				serial_out += "Unknown song"
			serial_out += '\n'
			ser.write(serial_out)
			#print "[DISPLAY_SENDER] RPi -> Ard:",serial_out
		
		time.sleep(1)

''' This functon tests the Internet connection '''		
def connectedToInternet():
	try:
		urllib2.urlopen("http://www.google.com", timeout=3)
	except urllib2.URLError:
		return False
	return True
		
if __name__ == "__main__":
	arduinoReady = False
	while(not arduinoReady):
		serial = ser.readline()
		if(serial == "INITOK\r\n"):
			arduinoReady = True
			print "Arduino connected!"
			ser.write("UP RPi Connected!\n")
		else:
			print "Waiting Arduino connection..."
			time.sleep(1)
			
	while(not connectedToInternet()):
		print "Testing internet connection..."
		ser.write("DW Waiting Inet...\n")
		time.sleep(1)
		
	ser.write("DW Inet. Connected!\n")
		
	rec = threading.Thread(target=button_receiver,name='ButtonReceiverTh')
	sen = threading.Thread(target=display_sender,name='DisplaySenderTh')
	rec.start()
	sen.start()
	