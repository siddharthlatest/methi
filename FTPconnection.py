from ftplib import FTP

class FTPconnection:
	@staticmethod
	def __init__(self, server, username, password):
		self.server = server
		self.username = username
		self.password = password

	@staticmethod
	def upload(self, filename, obj, remotePath="."):
		ftp = FTP(server, username, password)
		ftp.cwd(remotePath)
		ftp.storbinary("STOR %s" % filename, obj)
		ftp.quit()

	@staticmethod
	def uploadFile(self, filename, localFile, remotePath="."):
		obj = open(localFile, "wb")
		self.upload(filename,obj,remotePath)
		obj.close()

	@staticmethod
	def download(self, filename, obj, remotePath="."):
		ftp = FTP(server, username, password)
		ftp.cwd(remotePath)
		ftp.retrbinary("RETR %s" % filename, obj.write)
		ftp.quit()

	@staticmethod
	def downloadFile(self, filename, localFile, remotePath="."):
		obj = open(localFile, "wb")
		self.download(filename,obj,remotePath)
		obj.close()

	@staticmethod
	def delete_file(self, filename, remotePath="."):
		ftp = FTP(server, username, password)
		ftp.cwd(remotePath)
		ftp.delete(filename)
		ftp.quit()

	@staticmethod
	def delete_dir(self, dirname, remotePath="."):
		ftp = FTP(server, username, password)
		ftp.cwd(remotePath)
		ftp.rmd(dirname)
		ftp.quit()

	@staticmethod
	def make_dir(self, dirname, remotePath="."):
		ftp = FTP(server, username, password)
		ftp.cwd(remotePath)
		ftp.mkd(dirname)
		ftp.quit()