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
            # page += '<h1>' + ip + ':' + str(port) + '</h1><br>'
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


import socket

from gevent import monkey

monkey.patch_all()

timeout = 20
socket.setdefaulttimeout(timeout)

import requests

import pickle

server_dict = {}


def check_http(ip):
    print "test", ip
    try:
        r = requests.Session().get('http://' + str(ip), timeout=3)
        server_dict[ip] = r.status_code
    except Exception as e:
        print e
        pass


if __name__ == "__main__":
    hosts = [
        '10.150.166.93',
        '10.150.166.74',
        '10.150.166.78',
        '10.150.166.79',
        '10.150.166.101',
        '10.191.10.22',
    ]

    from gevent.pool import Pool
    pool = Pool(30)

    pool.join(timeout=20)
    pool.map(check_http, hosts)
    print "Dumping port-80 response..."
    print server_dict
    # with open('server_dict.txt', 'wb') as f:
    #     pickle.dump(server_dict, f, True)

    with open('http_scan.log', 'wb') as f:
        f.write(str(server_dict))
