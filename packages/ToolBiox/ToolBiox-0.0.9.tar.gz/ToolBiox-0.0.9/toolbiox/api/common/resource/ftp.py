from ftplib import FTP


def ftp_connect(ip, user='', passwd='', port=0):
    try:
        ftp = FTP()
        ftp.connect(ip, port=port)
        ftp.login(user, passwd)
        return ftp
    except:
        return False


def downloadfile(ftp, remotepath, localpath):
    try:
        bufsize = 1024
        fp = open(localpath, 'wb')
        ftp.retrbinary('RETR  ' + remotepath, fp.write, bufsize)
        ftp.set_debuglevel(0)
        fp.close()
        return True
    except:
        return False


def uploadfile(ftp, remotepath, localpath):
    try:
        bufsize = 1024
        fp = open(localpath, 'rb')
        ftp.storbinary('STOR ' + remotepath, fp, bufsize)
        ftp.set_debuglevel(0)
        fp.close()
        return True
    except:
        return False




if __name__ == '__main__':
    from toolbiox.lib.common.os import get_file_name
    from toolbiox.lib.common.fileIO import read_list_file

    ip = 'submit.big.ac.cn'
    user = 'wujianqiang@mail.kib.ac.cn'
    passwd = 'VXyTwef9gxgti2A'

    upload_fof = '/lustre/home/xuyuxing/tmp/1'
    file_list = read_list_file(upload_fof)

    for file in file_list:
        print(file)

        file_name = get_file_name(file)
        target_dir = '/GSA/PRJCA008847/' + file_name

        ftp = ftp_connect(ip, user, passwd)
        uploadfile(ftp, target_dir, file)

"""
#!/usr/bin/python
#encoding=utf-8
 
from ftplib import FTP   
import sys   

class MyFTP(FTP):   
    ''' 
    conncet to FTP Server 
    '''   
    def __init__(self): 
        print 'make a object' 
    def ConnectFTP(self,remoteip,remoteport,loginname,loginpassword):   
        ftp=MyFTP() 
 
        try: 
            ftp.connect(remoteip,remoteport,600) 
            print 'success' 
        except Exception, e:
            print >> sys.stderr, "conncet failed1 - %s" % e
            return (0,'conncet failed')   
        else:   
            try:   
                ftp.login(loginname,loginpassword)   
                print('login success')
            except Exception, e:
                print >>sys.stderr, 'login failed - %s' % e
                return (0,'login failed')   
            else:
                print 'return 1'
                return (1,ftp)   
         
    def download(self,remoteHost,remotePort,loginname,loginpassword,remotePath,localPath):   
        #connect to the FTP Server and check the return   
        res = self.ConnectFTP(remoteHost,remotePort,loginname,loginpassword)   
        if(res[0]!=1):
            print >>sys.stderr, res[1]
            sys.exit()
             
        #change the remote directory and get the remote file size   
        ftp=res[1]
        ftp.set_pasv(0)
        dires = self.splitpath(remotePath)
        if dires[0]:
            ftp.cwd(dires[0])   # change remote work dir
        remotefile=dires[1]     # remote file name
        print dires[0]+' '+ dires[1]   
        fsize=ftp.size(remotefile)   
        if fsize==0 : # localfime's site is 0
            return
             
        #check local file isn't exists and get the local file size   
        lsize=0L
        if os.path.exists(localPath):   
            lsize=os.stat(localPath).st_size   
                 
        if lsize >= fsize:   
            print 'local file is bigger or equal remote file'   
            return   
        blocksize=1024 * 1024
        cmpsize=lsize
        ftp.voidcmd('TYPE I')
        conn = ftp.transfercmd('RETR '+remotefile,lsize)
        lwrite=open(localPath,'ab')
        while True:
            data=conn.recv(blocksize)
            if not data:
                break
            lwrite.write(data)
            cmpsize+=len(data)
            #print '\b'*30,'download process:%.2f%%'%(float(cmpsize)/fsize*100),
            print '\n','download process:%.2f%%'%(float(cmpsize)/fsize*100),
        lwrite.close()
        ftp.voidcmd('NOOP')
        ftp.voidresp()
        conn.close()
        ftp.quit()
 
    def upload(self,remotehost,remoteport,loginname,loginpassword,remotepath,localpath,callback=None):
        if not os.path.exists(localpath):
            print "Local file doesn't exists"
            return
        self.set_debuglevel(2)
        res=self.ConnectFTP(remotehost,remoteport,loginname,loginpassword)
        if res[0]!=1:
            print res[1]
            sys.exit()
        ftp=res[1]
        remote=self.splitpath(remotepath)
        ftp.cwd(remote[0])
        rsize=0L
        try:
            rsize=ftp.size(remote[1])
        except:
            pass
        if (rsize==None):
            rsize=0L
        lsize=os.stat(localpath).st_size
        print('rsize : %d, lsize : %d' % (rsize, lsize))
        if (rsize==lsize):
            print 'remote filesize is equal with local'
            return
        if (rsize<lsize):
            localf=open(localpath,'rb')
            localf.seek(rsize)
            ftp.voidcmd('TYPE I')
            datasock=''
            esize=''
            try:
                print(remote[1])
                datasock,esize=ftp.ntransfercmd("STOR "+remote[1],rsize)
            except Exception, e:
                print >>sys.stderr, '----------ftp.ntransfercmd-------- : %s' % e
                return
            cmpsize=rsize
            while True:
                buf=localf.read(1024 * 1024)
                if not len(buf):
                    print '\rno data break'
                    break
                datasock.sendall(buf)
                if callback:
                    callback(buf)
                cmpsize+=len(buf)
                print '\b'*30,'uploading %.2f%%'%(float(cmpsize)/lsize*100),
                if cmpsize==lsize:
                    print '\rfile size equal break'
                    break
            datasock.close()
            print 'close data handle'
            localf.close()
            print 'close local file handle'
            ftp.voidcmd('NOOP')
            print 'keep alive cmd success'
            ftp.voidresp()
            print 'No loop cmd'
            ftp.quit()
 
    def splitpath(self,remotepath):
        position=remotepath.rfind('/')
        return (remotepath[:position+1],remotepath[position+1:])
 
#下面是使用代码
ftpClient = MyFTP();
ftpClient.download('10.61.101.151',21,'test','test','/home/test/X86_GDB','D:\Pmp\X86_GDB');
ftpClient.upload('10.61.101.151',21,'test','test','/home/test/123','D:\Pmp\g123');
"""