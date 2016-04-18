import os
# nmap scans a server to see what processes are running and what ports are open
# print get_nmap('-F', '216.58.197.46')
# google nmap for more nmap flags. -F is does a fast scan

ROOT_DIR = 'web_report'


def create_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def write_file(path, data):
    f = open(path, 'w')
    f.write(data)
    f.close()


create_dir(ROOT_DIR)


def get_nmap(options, ip):
    print "Doing the nmap scan..."
    command = 'nmap ' + options + ' ' + ip
    # starts another process. (like typing a new command on terminal)
    process = os.popen(command)
    results = str(process.read())
    return results


def create_report(name, nmap):
    project_dir = ROOT_DIR + '/' + name
    create_dir(project_dir)
    write_file(project_dir + '/nmap.txt', nmap)


if __name__ == '__main__':
    ip_addr = 'www.qq.com'
    nmap = get_nmap('-F', ip_addr)
    create_report('nmap', nmap)
    print nmap
