# This program generates a GUI using which, we can send commands to the bot.

import tkinter as tk
import tkinter.messagebox as tkm
import serial
import pyaudio
import wave
import numpy as np
import soundfile as sf
from python_speech_features import mfcc
import bluetooth, subprocess
import time



port = 1
bd_addr = '00:18:E4:40:00:06'#HC - 05 MAC Address. You need to enter your own module's address
top = tk.Tk()
top.title("~VOICE RECOG~")
top.configure(background = "black")


def scan():
	l1 = tk.Label(top)
	l1.grid(row = 1, column = 1)
	devices = subprocess.check_output('hcitool scan', shell = True)#scanning
	if len(devices) == 0:
		l1.configure(text = "No devices found!")
	l1.configure(text = devices)
	
b3 = tk.Button(top, text= "Scan", command = scan)
b3["bg"] = "white"
b3["border"] = "0"
b3.grid(row = 0, column = 1)

#ComPort.connect((bd_addr, port))

def welc():
	tkm.showinfo(" ","Connecting....")
	ComPort = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
	ComPort.connect((bd_addr, port))
	time.sleep(0.1)
	#subprocess.call("sudo rfcomm bind 0 00:18:E4:40:00:06" , shell = True)

	
def record():
	
	CHUNK = 1024 
	FORMAT = pyaudio.paInt16 #paInt8
	CHANNELS = 1
	RATE = 8000 #sample rate
	RECORD_SECONDS = 3
	WAVE_OUTPUT_FILENAME = "testab.wav"

	p = pyaudio.PyAudio()

	stream = p.open(format=FORMAT,channels=CHANNELS,rate=RATE,input=True,frames_per_buffer=CHUNK) #buffer
	print("* recording")
	frames = []
	for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
		data = stream.read(CHUNK)
		frames.append(data) # 2 bytes(16 bits) per channel
	print("* done recording")
	stream.stop_stream()
	stream.close()
	p.terminate()
	wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
	wf.setnchannels(CHANNELS)
	wf.setsampwidth(p.get_sample_size(FORMAT))
	wf.setframerate(RATE)
	wf.writeframes(b''.join(frames))
	wf.close()
	b =WAVE_OUTPUT_FILENAME

	data, samplerate = sf.read(b)
	x= len(data)
	p = 25000-x
	l =0
	tests = np.empty([200,4043])
	new_data = np.empty([25000,])
	y1 = np.empty([25000,])	

	y = p/2;

	for i in range(0,y-1):
		new_data[i] = y1 [i]
	for i in range(y,25000-p+y-1):
		new_data[i] = data[i-y]
	for i in range(25000-y,24999):
		new_data[i] = y1[i]
	data1 = mfcc(new_data,samplerate)
	data = data1
	data = data.reshape(4043,)

	nIn = 4043
	nOut = 5
	x = data


	def sigmoid(x):
		x = np.array(x,dtype=np.float128)
		x = x.reshape(nOut,1)
		x = x
		for  i in range (0,5):
			if x[i] < -700:
				x[i]=0
			else:
				x[i] = 1/(1+np.exp(-x[i]))	
		x=x.reshape(-1,nOut)
		return x


	def nn_forward(X, W1, b):
		x = X.reshape(-1, nIn)
		#print x.shape
		layer2 = np.dot(x,W1) + b
		out= sigmoid(layer2)
		#losses1.append(loss)
		return out

	W1 = np.loadtxt('W1.out',delimiter = ',')
	b = np.loadtxt('b.out',delimiter = ',')
	q = np.empty([5,])


	pred = np.argmax(nn_forward(data, W1, b))
	print(nn_forward(data, W1, b))

	q[pred] +=1 
	 
	print("Prediction: Type {}".format(pred))

	   
	pred = np.argmax(q)
	
	ComPort = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
	ComPort.connect((bd_addr, port))

			

	#ser = serial.Serial('/dev/ttyACM2',9600)
	pr = str(pred)
	#ser.write(pr)


	if(pred==0):
		if tkm.askyesno("~Prediction Window~", "Prediction = backward\nIs the prediction correct?"):
			No = ComPort.send("backward")
			ComPort.recv(1024)
			
			
	if(pred==1):
		if tkm.askyesno("~Prediction Window~", "Prediction = forward\nIs the prediction correct?"):
			No = ComPort.send("forward")
			ComPort.recv(1024)
			
	if(pred==2):
		if tkm.askyesno("~Prediction Window~", "Prediction = turn left\nIs the prediction correct?"):
			No = ComPort.send("turn left")
			ComPort.recv(1024)
			
	if(pred==3):
		if tkm.askyesno("~Prediction Window~", "Prediction = turn right\nIs the prediction correct?"):
			No = ComPort.send("turn right")
			ComPort.recv(1024)
			
	if(pred==4):
		if tkm.askyesno("~Prediction Window~", "Prediction = stop\nIs the prediction correct?"):
			No = ComPort.send("stop")
			ComPort.recv(1024)
			

	#data = bytearray(b'')
	#No = ComPort.write(data)

label = tk.Label(top, text = "Arduino-Bluetooth")
label.place(anchor = 's')
 	
loadimage = tk.PhotoImage(file="../Figures/Bluetooth.png")
b1 = tk.Button(top, image= loadimage, command = welc)
b1["bg"] = "black"
b1["border"] = "0"
b1.grid(row = 3, column = 1)
	
image1 = tk.PhotoImage(file='../Figures/mic.png').subsample(6, 6)
b2 = tk.Button(top, text= "Click here to give voice command", command = record,image = image1)
b2["bg"] = "white"
b2["border"] = "0"
b2.grid(row = 5, column = 1)


label = tk.Label(top, text = "~Click the Mic icon to give command~")
label.grid(row = 4, column = 1)

top.mainloop()

