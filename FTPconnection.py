from ftplib import FTP

class FTPconnection:
	def __init__(self, server, username, password,printQ):
		self.server = server
		self.username = username
		self.password = password
		self.printQ = printQ

	def directory_exists(self, ftp, dir):
		filelist = []
		ftp.retrlines('LIST',filelist.append)
		for f in filelist:
			if f.split()[-1] == dir and f.upper().startswith('D'):
				return True
		return False

	def upload(self, filename, obj, remotePath="."):
		ftp = FTP(self.server, self.username, self.password)
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


	def uploadFile(self, filename, localFile, remotePath="."):
		obj = open(localFile, "rb")
		self.upload(filename,obj,remotePath)
		obj.close()


	def download(self, filename, obj, remotePath="."):
		ftp = FTP(self.server, self.username, self.password)

		try:
			ftp.cwd(remotePath)
			ftp.retrbinary("RETR %s" % filename, obj.write)

		except Exception:
			self.printQ.put("FTPC Down Error")
			pass

		ftp.quit()


	def downloadFile(self, filename, localFile, remotePath="."):
		obj = open(localFile, "wb")
		self.download(filename,obj,remotePath)
		obj.close()


	def delete_file(self, filename, remotePath="."):
		ftp = FTP(self.server, self.username, self.password)
		ftp.cwd(remotePath)
		ftp.delete(filename)
		ftp.quit()


	def delete_dir(self, dirname, remotePath="."):
		ftp = FTP(self.server, self.username, self.password)
		ftp.cwd(remotePath)
		ftp.rmd(dirname)
		ftp.quit()


	def make_dir(self, dirname, remotePath="."):
		ftp = FTP(self.server, self.username, self.password)
		ftp.cwd(remotePath)
		ftp.mkd(dirname)
		ftp.quit()