#!/usr/bin/python3
"""
Why:
    - https://nmap.org/book/output-formats-output-to-database.html

Summary:
    - Take the XML results given from (masscan || nmap) and parse
        - GUI visualization provided by Plotly Bubble chart
        - SQL visualization provided by sqlite3
    - Visualize the data in interesting ways as to find quirks and commonalities
    - Uses the services list from Nmap for visualization points
    - Prettifies XML scan results for better deciphering
    - Expandable to use other datasets as well
"""

from lxml import etree
from lib import db_handler
from lib import list_handler
from lib import plot_handler
from lib import scan_handler
from lib import stats_handler
from lib import xml_handler
import argparse
import os
import sqlite3 as lite
import sys

## Grab the port lists
lHandler = list_handler.List()
lHandler.list_pick()

def pScan(xHandler):
    """Prettify scan results, useful for deciphering unknown xml scans"""
    xHandler.pFy()

def vScan(xHandler):
    """Visualize scan results"""
   ## Map out the XML
    try:
        tree = etree.parse(xHandler.xmlInput)
        sqlFile = '.'.join(xHandler.xmlInput.split('.')[:-1]) + '.sqlite3'
        htmlFile = '.'.join(xHandler.xmlInput.split('.')[:-1]) + '_'
    except:
        sys.exit(1)
    root = tree.getroot()

    ## prep
    try:
        os.remove(sqlFile)
    except:
        pass

    ## Setup the DB connections
    con = lite.connect(sqlFile)
    con.text_factory = str
    db = con.cursor()

    ## Be friendly to GUI SQL visualization
    db.execute("""CREATE TABLE `_` (`_` INTEGER)""")

    ## Generate initial tables
    dBase = db_handler.Database(db)
    dBase.scan_prep()
    dBase.svc_prep()
    con.commit()

    ## Generate scan info
    scan = scan_handler.Scan(con, db, lHandler, root, xHandler)
    con.commit()

    ## Generate stats and closeout
    stats = stats_handler.Stats(db)
    stats.by_addr()
    stats.by_port()
    stats.by_svc()
    addrStats = stats.addrStats()
    portStats = stats.portStats()
    svcStats = stats.svcStats()
    con.commit()
    con.close()

    ## Plot the GUIs
    plot_handler.Plotter(addrStats, htmlFile + 'byAddr.html', autoOpen = True)
    plot_handler.Plotter(portStats, htmlFile + 'byPort.html', autoOpen = True)
    plot_handler.Plotter(svcStats, htmlFile + 'bySvc.html', autoOpen = True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'scanParser - Visualize port scan data')
    group = parser.add_mutually_exclusive_group(required = True)
    group.add_argument('-v',
                       help = 'Visualize xml input file')
    group.add_argument('-p',
                       help = 'Prettify raw xml output from various scanners')
    args = parser.parse_args()

    if args.v is not None:
        xHandler = xml_handler.Xml(args.v)
        vScan(xHandler)
    if args.p is not None:
        xHandler = xml_handler.Xml(args.p)
        pScan(xHandler)
