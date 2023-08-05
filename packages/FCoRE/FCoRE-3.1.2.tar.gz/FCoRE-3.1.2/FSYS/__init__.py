import os,platform,socket,re,uuid,json,logging,pwd
from FList import LIST

def get_pid():
    return os.getpid()

def get_username():
    return LIST.get(0, pwd.getpwuid(os.getuid()), False)

def getSystemInfo():
    try:
        info = {}
        info['pid'] = get_pid()
        info['user'] = get_username()
        info['platform'] = platform.system()
        info['platform-release'] = platform.release()
        info['platform-version'] = platform.version()
        info['architecture'] = platform.machine()
        info['hostname'] = socket.gethostname()
        info['ip-address'] = socket.gethostbyname(socket.gethostname())
        info['mac-address'] = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
        info['processor'] = platform.processor()
        # info['ram'] = str(round(psutil.virtual_memory().total / (1024.0 **3)))+" GB"
        return info
    except Exception as e:
        logging.exception(e)


# print(get_username())
# print(json.loads(getSystemInfo()))