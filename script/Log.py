import os.path
import shutil

logPrefix = "./log/"

def writeLog(result, today):
    if not os.path.exists(logPrefix):
        os.mkdir(logPrefix)
    fileName = logPrefix + today.strftime("%Y_%m_") + "log" + ".txt"
    print(fileName)
    mode = 'a+' if os.path.exists(fileName) else 'w+'
    with open(fileName, mode) as f:
        nodes = result['data']['search']['edges']
        count = 1
        for n in nodes:
            if n['node']['object'] != None:
                f.write(n['node']['nameWithOwner'] + ':\n')
                f.write(n['node']['url'] + ':\n')
                f.write(('').join(n['node']['object']['text'])) 
                f.write('\n')
                count += 1
        f.close()

def clearLog():
    if os.path.exists(logPrefix):
        shutil.rmtree(logPrefix)