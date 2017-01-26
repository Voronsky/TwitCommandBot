
class CredentialsReader(object):
    creds={}
    
    def __init__(self,file):
        self.fo = open(file,'r')

    def setTwitterApi(self):
        for line in self.fo.readlines():
            if not '#' in line and len(line)>1:
                string = line.split('=')
                key = string[0].strip()
                #value = string[1].replace('\n','')
                value = string[1].strip('\n')
                value = value.replace('"','').strip()
                self.creds.update({key:value})

