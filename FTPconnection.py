from ftplib import FTP

class FTPconnection:
	def __init__(self, server, username, password):
		self.server = server
		self.username = username
		self.password = password

	def upload(self, filename, obj, remotePath="."):
		ftp = FTP(server, username, password)
		ftp.cwd(remotePath)
		ftp.storbinary("STOR %s" % filename, obj)
		ftp.quit()

	def uploadFile(self, filename, localFile, remotePath="."):
		obj = open(localFile, "wb")
		self.upload(filename,obj,remotePath)
		obj.close()

	def download(self, filename, obj, remotePath="."):
		ftp = FTP(server, username, password)
		ftp.cwd(remotePath)
		ftp.retrbinary("RETR %s" % filename, obj.write)
		ftp.quit()

	def downloadFile(self, filename, localFile, remotePath="."):
		obj = open(localFile, "wb")
		self.download(filename,obj,remotePath)
		obj.close()

	def delete_file(self, filename, remotePath="."):
		ftp = FTP(server, username, password)
		ftp.cwd(remotePath)
		ftp.delete(filename)
		ftp.quit()

	def delete_dir(self, dirname, remotePath="."):
		ftp = FTP(server, username, password)
		ftp.cwd(remotePath)
		ftp.rmd(dirname)
		ftp.quit()

	def make_dir(self, dirname, remotePath="."):
		ftp = FTP(server, username, password)
		ftp.cwd(remotePath)
		ftp.mkd(dirname)
		ftp.quit()