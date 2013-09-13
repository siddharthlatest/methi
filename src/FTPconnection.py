from ftplib import FTP_TLS

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


	def uploadFile(self, filename, localFile, remotePath="."):
		obj = open(localFile, "rb")
		self.upload(filename,obj,remotePath)
		obj.close()


	def download(self, filename, obj, remotePath="."):
		ftp = FTP_TLS(self.server, self.username, self.password)
		ftp.prot_p()

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
		ftp = FTP_TLS(self.server, self.username, self.password)
		ftp.prot_p()
		ftp.cwd(remotePath)
		ftp.delete(filename)
		ftp.quit()

	def delete_dir(self, dirname, remotePath="."):
		ftp = FTP_TLS(self.server, self.username, self.password)
		ftp.prot_p()
		ftp.cwd(remotePath)
		try:
			ftp.cwd(dirname)
			for f in ftp.nlst():
				ftp.delete(f)
			ftp.cwd("..")
			ftp.rmd(dirname)
		except:
			self.printQ.put("unable to delete directory")
		ftp.quit()

	def rename(self, original, changed, remotePath="."):
		ftp = FTP_TLS(self.server, self.username, self.password)
		ftp.prot_p()
		ftp.cwd(remotePath)
		if self.directory_exists(ftp, original):
			ftp.rename(original, changed)
		ftp.quit()

	def make_dir(self, dirname, remotePath="."):
		ftp = FTP_TLS(self.server, self.username, self.password)
		ftp.prot_p()
		ftp.cwd(remotePath)
		ftp.mkd(dirname)
		ftp.quit()

	def login(self):
		ftp = FTP_TLS(self.server, self.username, self.password)
		ftp.prot_p()
		return ftp

	def delete_dir_nologin(self, ftp, dirname, remotePath="."):
		try:
			self.printQ.put(ftp.pwd())
			ftp.cwd("/")
			ftp.cwd(remotePath)
			self.printQ.put("after: "+ftp.pwd())
			try:
				ftp.cwd(dirname)
				for f in ftp.nlst():
					ftp.delete(f)
				ftp.cwd("..")
				ftp.rmd(dirname)
			except:
				self.printQ.put("unable to delete directory")

			self.printQ.put(ftp.pwd())
		except:
			self.printQ.put("delete dir failed")

	def rename_nologin(self, ftp, original, changed, remotePath="."):
		self.printQ.put(ftp.pwd())
		try:
			ftp.cwd("/")
			ftp.cwd(remotePath)
			self.printQ.put("after: "+ftp.pwd())
			if self.directory_exists(ftp, original):
				ftp.rename(original, changed)
			ftp.quit()
		except:
			self.printQ.put("rename failed")

	def logout(self,ftp):
		self.printQ.put(ftp.pwd())
		try:
			ftp.quit()
		except:
			self.printQ.put("Quit errror")
			pass