import os
import socket
import thread
import time
import cv2
import random

from ftplib import FTP

class SDCard:
	def __init__(self, ip, dlfolder):
		self.ip=ip
		self.dlfolder = dlfolder
		self.existing_files = os.listdir(self.dlfolder)
		self.new_files = []
		self.ping_successful = False



	def find_card_thread (self, callback=None):
		while True:
			response = os.system("ping -c 1 -W 1 " + self.ip + " > /dev/null")

			#and then check the response...
			if response == 0:
				self.ping_successful = True
				time.sleep(1)
			else:
				self.ping_successful = False
			

	def ftp_thread(self, callback):
		

		while True:
			if not self.ping_successful:
				time.sleep(0.5)
				continue

			lastfile = 'notexisting'
			try:
				ftp = FTP(self.ip, timeout=10)
				ftp.login()
				ftp.cwd(CARD_FOLDER)
				file_list = ftp.nlst()
				#get only new files
				diff = set(file_list) - set(self.existing_files)
				for fn in diff:
					print "downloading %s" % fn
					lastfile = fn
					ftp.retrbinary("RETR " + fn ,open(self.dlfolder + fn, 'wb').write)
					self.new_files.append(fn)
					self.existing_files.append(fn)

				ftp.quit()
				ftp.close()
				time.sleep(1)	
			except:
				print 'Lost FTP connection'
				if os.path.isfile(self.dlfolder + lastfile):
					print 'Removing broken download'
					os.remove(self.dlfolder + lastfile)
				continue

	def find_card (self, callback=None):
		thread.start_new_thread (self.find_card_thread, (callback,))

	def ftp(self, callback=None):
		thread.start_new_thread( self.ftp_thread, (callback,))


	def display_photo(self, fn, new = False):
		print "showing " + fn
		img =  cv2.imread(self.dlfolder + fn)
		if new:
			print "new"
			cv2.circle(img,(63,63), 63, (0,255,0), -1)
			delay = 10
		else:
			delay = 5
		cv2.imshow("test",img)
		cv2.waitKey(delay*1000)	


	def display_loop(self):
		cv2.namedWindow("test", cv2.WND_PROP_FULLSCREEN)
		cv2.setWindowProperty("test", cv2.WND_PROP_FULLSCREEN, cv2.cv.CV_WINDOW_FULLSCREEN)
	

		while True:
			#first display new files
			while self.new_files:
				self.display_photo(self.new_files[0], True)
				self.new_files.pop(0)

			if self.existing_files:
				self.display_photo(random.choice(self.existing_files))
			



		


CARD_IP = '192.168.2.1'
CARD_FOLDER = 'DCIM/211_FUJI'


DOWNLOAD_FOLDER='/tmp/bilder/'

card = SDCard(CARD_IP, DOWNLOAD_FOLDER)

card.find_card(None)
card.ftp(None)
card.display_loop()

time.sleep(1000)

