# coding=utf-8

import nmap
from threading import Thread
from Queue import Queue
import time
import requests
import re

URLS = ['']

TimeOut = 3


def NmapPortServiceScan(host, speed="-T4", noPing=True, portRange="80,8080,8090"):
    lines = ""
    nm = nmap.PortScanner()

    args = "-sT %s " % speed

    if noPing:
        args += "-Pn"

    nm.scan(hosts=host, ports=portRange, arguments=args, sudo=False)

    csv = nm.csv()

    lineList = csv.split("\r\n")

    lineList = lineList[1:]

    for line in lineList:
        lines += line + "\n"

    return lines


def scan_httpports():
    global nmap_list
    while True:
        host = q.get()

        nmap_list.append(NmapPortServiceScan(host))

        q.task_done()


def dlpage():
    header = {}
    page = ''
    global pages
    pages = []
    while True:
        ip = pq.get()
        for port in ['80']:
            #page += '<h1>' + ip + ':' + str(port) + '</h1><br>'
            for url in URLS:

                try:
                    r = requests.Session().get(
                        'http://' + str(ip), headers=header, timeout=TimeOut)

                    status = r.status_code
                    text = r.text
                    # get the title
                    title = re.search(r'<title>(.*)</title>', r.text)

                    if title:
                        title = title.group(1).strip().strip(
                            "\r").strip("\n")[:30]
                    else:
                        title = "Unkown"
                    banner = ''

                    try:
                        # get the server banner
                        banner += r.headers['Server'][:20]
                    except:
                        banner = "Unkown"

                    page = '%-20s%-20s%-20s%-20s' % (
                        ip, status, banner, title)

                except Exception as e:
                    print e
                    pass
        pages.append(page)
        pq.task_done()

    return pages


if __name__ == "__main__":
    hosts = [
        '10.150.166.93',
        '10.150.166.74',
        '10.150.166.78',
        '10.150.166.79',
        '10.150.166.101',
        '10.191.10.22',


    ]
    csvHeader = "Host;Protocol;Port;Name;State;"
    csvHeader += "Product;Extrainfo;Reason;Version;Conf;CPE\n\r"
    fileName = "NmapScan.csv"
    scanFile = open(fileName, "w").close()
    scanFile = open(fileName, "a")
    scanFile.write(csvHeader)

    global nmap_list
    nmap_list = []
    q = Queue()

    for i in range(5):
        t = Thread(target=scan_httpports)
        t.setDaemon(True)
        t.start()

    for ip in hosts:
        q.put(ip)
    q.join()

    nmap_list_s = "\n".join(nmap_list)
    scanFile.write(nmap_list_s)

    scanFile.close()

    global pages
    page = ''
    pq = Queue()

    for i in range(5):
        t = Thread(target=dlpage)
        t.setDaemon(True)
        t.start()

    for ip in hosts:
        pq.put(ip)
    pq.join()

    f = open('index.csv', 'w')
    f.write('%-20s%-20s%-20s%-20sn\n' % ('ip', 'Status', 'WebSvr', 'Title'))
    _pages = "\n".join(pages)
    f.write(_pages)
    f.close()
