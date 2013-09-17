from ftplib import FTP_TLS
import logging

class FTPconnection:
	def __init__(self, server, username, password):
		self.server = server
		self.username = username
		self.password = password
		self.logger = logging.getLogger("daemon.syncclient.ftpconn")

	def directory_exists(self, ftp, dir):
		try:
			filelist = []
			ftp.retrlines('LIST',filelist.append)
			for f in filelist:
				if f.split()[-1] == dir and f.upper().startswith('D'):
					return True
			return False
		except:
			self.logger.exception("unable to verify existence of directory")
			return False

	def upload(self, filename, obj, remotePath="."):
		try:
			ftp = FTP_TLS(self.server, self.username, self.password)
			ftp.prot_p()
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

			ftp.storbinary("STOR %s" % filename, obj)
			ftp.quit()
		except:
			self.logger.exception("unable to upload")
			return

	def uploadFile(self, filename, localFile, remotePath="."):
		try:
			obj = open(localFile, "rb")
			self.upload(filename,obj,remotePath)
			obj.close()
		except:
			self.logger.exception("unable to upload file")
			return

	def download(self, filename, obj, remotePath="."):
		try:
			ftp = FTP_TLS(self.server, self.username, self.password)
			ftp.prot_p()

			ftp.cwd(remotePath)
			ftp.retrbinary("RETR %s" % filename, obj.write)

			ftp.quit()
		except:
			self.logger.exception("unable to download")
			return

	def downloadFile(self, filename, localFile, remotePath="."):
		try:
			obj = open(localFile, "wb")
			self.download(filename,obj,remotePath)
			obj.close()
		except:
			self.logger.exception("unable to download file")
			return

	def delete_file(self, filename, remotePath="."):
		try:
			ftp = FTP_TLS(self.server, self.username, self.password)
			ftp.prot_p()
			ftp.cwd(remotePath)
			ftp.delete(filename)
			ftp.quit()
		except:
			self.logger.exception("unable to delete file")
			return

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
		except:
			self.logger.exception("unable to delete directory")
			return

	def rename(self, original, changed, remotePath="."):
		try:
			ftp = FTP_TLS(self.server, self.username, self.password)
			ftp.prot_p()
			ftp.cwd(remotePath)
			if self.directory_exists(ftp, original):
				ftp.rename(original, changed)
			ftp.quit()
		except:
			self.logger.exception("unable to rename directory")
			return

	def make_dir(self, dirname, remotePath="."):
		try:
			ftp = FTP_TLS(self.server, self.username, self.password)
			ftp.prot_p()
			ftp.cwd(remotePath)
			ftp.mkd(dirname)
			ftp.quit()
		except:
			self.logger.exception("unable to make directory")
			return


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
				self.logger.error("unable to delete directory")

		except:
			self.logger.error("delete dir failed")

	def rename_nologin(self, ftp, original, changed, remotePath="."):
		try:
			ftp.cwd("/")
			ftp.cwd(remotePath)
			if self.directory_exists(ftp, original):
				ftp.rename(original, changed)
			ftp.quit()
		except:
			self.logger.error("rename failed")

	def logout(self,ftp):
		try:
			ftp.quit()
		except:
			self.logger.error("Quit errror")
			pass