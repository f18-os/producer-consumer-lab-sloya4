
import threading
from queue import Queue
from random import randint
import cv2
import numpy as np
import base64

def main():
	condition = threading.Condition()
	#condition = threading.Conditon()
	q = Queue(10)
	fileName = 'clip.mp4'
	producer = Producer(q, condition, fileName)
	consume = Consumer(q, condition)

	producer.start()
	consume.start()
	q.join()

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

class Consumer(threading.Thread):
	def __init__(self, queue, condition):
		super(Consumer,self).__init__()
		self.queue = queue
		self.condition = condition

	def run(self):
		count = 0
		while True:
			self.condition.acquire()
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

main()
 





