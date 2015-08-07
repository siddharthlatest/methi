from ftplib import FTP_TLS
import logging

class FTPconnection:
	def __init__(self, server, username, password, failNotify):
		self.server = server
		self.username = username
		self.password = password
		self.logger = logging.getLogger("daemon.syncclient.ftpconn")
		self.failNotify = failNotify

	def directory_exists(self, ftp, dir,notify=True):
		try:
			filelist = []
			ftp.retrlines('LIST',filelist.append)
			for f in filelist:
				if f.split()[-1] == dir and f.upper().startswith('D'):
					return True
			return False
		except:
			if (notify):
				self.failNotify()
				self.logger.exception("unable to verify existence of directory")
			return False

	def upload(self, filename, obj, remotePath=".",checkDir=True):
		try:
			ftp = FTP_TLS(self.server, self.username, self.password)
			ftp.prot_p()
			if checkDir:
				self.logger.info("checking if Dir exists: "+remotePath)
				remoteDirs = remotePath.split("/")
				i = 0
				while i<len(remoteDirs):
					if not self.directory_exists(ftp, remoteDirs[i]):
						ftp.mkd(remoteDirs[i])
						ftp.cwd(remoteDirs[i])
						i = i+1
					else:
						ftp.cwd(remoteDirs[i])
						i = i+1
			else:
				ftp.cwd(remotePath)

			ftp.storbinary("STOR %s" % filename, obj)
			ftp.quit()
			return 1
		except:
			self.failNotify()
			self.logger.exception("unable to upload")
			return -1

	def uploadFile(self, filename, localFile, remotePath=".",checkDir=True):
		try:
			obj = open(localFile, "rb")
			ret = self.upload(filename,obj,remotePath,checkDir)
			obj.close()
			return ret
		except:
			self.failNotify()
			self.logger.exception("unable to upload file")
			return -1

	def download(self, filename, obj, remotePath=".",notify=True):
		try:
			ftp = FTP_TLS(self.server, self.username, self.password)
			ftp.prot_p()

			ftp.cwd(remotePath)
			ftp.retrbinary("RETR %s" % filename, obj.write)

			ftp.quit()
			return 1
		except:
			if(notify):
				self.failNotify()
				self.logger.exception("unable to download")
			return -1

	def downloadFile(self, filename, localFile, remotePath=".",notify=True):
		try:
			obj = open(localFile, "wb")
			ret = self.download(filename,obj,remotePath,notify)
			obj.close()
			return ret
		except:
			if(notify):
				self.failNotify()
				self.logger.exception("unable to download file")
			return -1

	def delete_file(self, filename, remotePath="."):
		try:
			ftp = FTP_TLS(self.server, self.username, self.password)
			ftp.prot_p()
			ftp.cwd(remotePath)
			ftp.delete(filename)
			ftp.quit()
			return 1
		except:
			self.failNotify()
			self.logger.exception("unable to delete file")
			return -1

	def delete_dir(self, dirname, remotePath="."):
		try:
			ftp = FTP_TLS(self.server, self.username, self.password)
			ftp.prot_p()
			ftp.cwd(remotePath)

			ftp.cwd(dirname)
			for f in ftp.nlst():	#this is kind of noobish improve it
				ftp.delete(f)
			ftp.cwd("..")
			ftp.rmd(dirname)

			ftp.quit()
			return 1
		except:
			self.failNotify()
			self.logger.exception("unable to delete directory")
			return -1

	def rename(self, original, changed, remotePath="."):
		try:
			ftp = FTP_TLS(self.server, self.username, self.password)
			ftp.prot_p()
			ftp.cwd(remotePath)
			if self.directory_exists(ftp, original):
				ftp.rename(original, changed)
			ftp.quit()
			return 1
		except:
			self.failNotify()
			self.logger.exception("unable to rename directory")
			return -1

	def make_dir(self, dirname, remotePath="."):
		try:
			ftp = FTP_TLS(self.server, self.username, self.password)
			ftp.prot_p()
			ftp.cwd(remotePath)
			ftp.mkd(dirname)
			ftp.quit()
			return 1
		except:
			self.failNotify()
			self.logger.exception("unable to make directory")
			return -1


#shitty methods do not work bcos we do not know how to work with passive FTP
	def login(self):
		ftp = FTP_TLS(self.server, self.username, self.password)
		ftp.prot_p()
		return ftp

	def delete_dir_nologin(self, ftp, dirname, remotePath="."):
		try:
			ftp.cwd("/")
			ftp.cwd(remotePath)
			try:
				ftp.cwd(dirname)
				for f in ftp.nlst():
					ftp.delete(f)
				ftp.cwd("..")
				ftp.rmd(dirname)
			except:
				self.failNotify()
				self.logger.error("unable to delete directory")

		except:
			self.failNotify()
			self.logger.error("delete dir failed")

	def rename_nologin(self, ftp, original, changed, remotePath="."):
		try:
			ftp.cwd("/")
			ftp.cwd(remotePath)
			if self.directory_exists(ftp, original):
				ftp.rename(original, changed)
			ftp.quit()
		except:
			self.failNotify()
			self.logger.error("rename failed")

	def logout(self,ftp):
		try:
			ftp.quit()
		except:
			self.failNotify()
			self.logger.error("Quit errror")
			pass