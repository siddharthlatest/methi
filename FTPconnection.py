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

	def download(self, filename, localFile, remotePath="."):
		obj = open(localFile, "wb")
		self.downloadObj(filename,obj,remotePath)
		obj.close()

	def downloadObj(self, filename, obj, remotePath="."):
		ftp = FTP(server, username, password)
		ftp.cwd(remotePath)
		ftp.retrbinary("RETR %s" % filename, obj.write)
		ftp.quit()

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