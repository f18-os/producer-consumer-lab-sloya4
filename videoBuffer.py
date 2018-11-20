#!/usr/bin/env python3

import threading
from queue import Queue
from random import randint
import cv2
import numpy as np
import base64

def main():
	#Threading conditions
	condition = threading.Condition()
	condition2 = threading.Condition()
	#Color queue
	q = Queue(10)
	
	#Gray queue
	gq = Queue(10)

	fileName = 'clip.mp4'
	#Initializing producer, consumer, and gray producer
	producer = Producer(q, condition, fileName)
	consume = Consumer(gq, condition2)
	grayProducer = GrayProducer(q, condition, condition2, gq)

	#Start thread
	producer.start()
	consume.start()
	grayProducer.start()
	q.join()

#Producer class
class Producer(threading.Thread):
	def __init__(self,queue, condition, fileName):
		super(Producer, self).__init__()
		self.queue = queue
		self.condition = condition
		self.fileName = fileName

	def run(self):
		count = 0
		vidcap = cv2.VideoCapture(self.fileName)
		sucess,image = vidcap.read()

		while True:
			self.condition.acquire()
			#Execute only if the queue is not full	
			if self.queue.qsize() < 10:
				success, jpgImage = cv2.imencode('.jpg', image)
				jpgAsText = base64.b64encode(jpgImage)
				self.queue.put(jpgAsText)
				sucess,image =vidcap.read()
				print('Reading frame {} {}'.format(count,success))
				count += 1
				self.condition.notify()
				self.condition.wait()
			self.condition.release()

#Consumer class
class Consumer(threading.Thread):
	def __init__(self, queue, condition):
		super(Consumer,self).__init__()
		self.queue = queue
		self.condition = condition

	def run(self):
		count = 0
		while True:
			self.condition.acquire()
			#Consumes only if the queue is not empty
			if self.queue.qsize() <= 0:
				self.condition.notify()
				self.condition.wait()
			frameAsText = self.queue.get()

			jpgRawImage = base64.b64decode(frameAsText)
			jpgImage = np.asarray(bytearray(jpgRawImage), dtype=np.uint8)

			img = cv2.imdecode( jpgImage,cv2.IMREAD_UNCHANGED)
			print("Displaying frame {}".format(count))
	
			cv2.imshow("Video", img)
			if cv2.waitKey(42) and 0xFF == ord("q"):
				break
			count += 1
			self.condition.release()

#Gray producer class
class GrayProducer(threading.Thread):
	def __init__(self, queue, condition,condition2, gQueue):
		super(GrayProducer,self).__init__()
		self.queue = queue
		self.condition = condition
		self.condition2 = condition2
		self.gQueue = gQueue
	
	def run(self):
		count = 0
		while True:
			self.condition.acquire()
			#Consumes only if is not empty
			if self.queue.qsize() <= 0:
				self.condition.notify()
				self.condition.wait()
			frameAsText = self.queue.get()
			self.condition.release()
			
			#Produce gray frame if queue is not full
			self.condition2.acquire()	
			if self.gQueue.qsize() < 10:
				jpgRawImage = base64.b64decode(frameAsText)
				jpgImage = np.asarray(bytearray(jpgRawImage), dtype=np.uint8)
				#Changes color image to gray image
				img = cv2.imdecode( jpgImage,cv2.IMREAD_GRAYSCALE)
				success, jpgImage = cv2.imencode('.jpg', img)
				grayFrame = base64.b64encode(jpgImage)
				print("Transforming frame {}".format(count))
				self.gQueue.put(grayFrame)
				self.condition2.notify()
				self.condition2.wait()
			self.condition2.release()


main()
 





