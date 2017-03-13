#!/usr/bin/python
# Copyright (c) 2013, 2014-2017 Oracle and/or its affiliates. All rights reserved.


"""Provide Module Description
"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
__author__ = "Andrew Hopkinson (Oracle Cloud Solutions A-Team)"
__copyright__ = "Copyright (c) 2013, 2014-2017 Oracle and/or its affiliates. All rights reserved."
__ekitversion__ = "@VERSION@"
__ekitrelease__ = "@RELEASE@"
__version__ = "1.0.0.0"
__date__ = "@BUILDDATE@"
__status__ = "Development"
__module__ = "orchestration"
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#


import datetime
import getopt
import json
import locale
import logging
import operator
import os
import requests
import sys

def addOrchestration(endpoint, resourcename, cookie, orchestration):
    basepath = '/orchestration/'
    params = None
    data = orchestration
    response = callRESTApi(endpoint, basepath, resourcename, data, 'POST', params, cookie)
    jsonResponse = json.loads(response.text)
    return jsonResponse

def deleteOrchestration(endpoint, resourcename, cookie):
    basepath = '/orchestration/'
    params = None
    data = None
    response = callRESTApi(endpoint, basepath, resourcename, data, 'DELETE', params, cookie)
    print(response)
    # jsonResponse = json.loads(response.text)
    jsonResponse = {}
    return jsonResponse

def getOrchestration(endpoint, resourcename, cookie):
    basepath = '/orchestration/'
    params = None
    data = None
    response = callRESTApi(endpoint, basepath, resourcename, data, 'GET', params, cookie)
    jsonResponse = json.loads(response.text)
    return jsonResponse

def listOrchestrations(endpoint, resourcename, cookie):
    basepath = '/orchestration/'
    params = None
    data = None
    response = callRESTApi(endpoint, basepath, resourcename, data, 'GET', params, cookie)
    jsonResponse = json.loads(response.text)
    return jsonResponse

def updateOrchestration(endpoint, resourcename, cookie, orchestration):
    basepath = '/orchestration/'
    params = None
    data = orchestration
    response = callRESTApi(endpoint, basepath, resourcename, data, 'PUT', params, cookie)
    jsonResponse = json.loads(response.text)
    return jsonResponse

def startOrchestration(endpoint, resourcename, cookie):
    basepath = '/orchestration/'
    params = {"action": "START"}
    data = None
    response = callRESTApi(endpoint, basepath, resourcename, data, 'PUT', params, cookie)
    jsonResponse = json.loads(response.text)
    return jsonResponse

def stopOrchestration(endpoint, resourcename, cookie):
    basepath = '/orchestration/'
    params = {"action": "STOP"}
    data = None
    response = callRESTApi(endpoint, basepath, resourcename, data, 'PUT', params, cookie)
    jsonResponse = json.loads(response.text)
    return jsonResponse

# Read Module Arguments
def readModuleArgs(opts, args):
    moduleArgs = {}
    moduleArgs['endpoint'] = None
    moduleArgs['user'] = None
    moduleArgs['password'] = None
    moduleArgs['pwdfile'] = None

    # Read Module Command Line Arguments.
    for opt, arg in opts:
        if opt in ("-e", "--endpoint"):
            moduleArgs['endpoint'] = arg
        elif opt in ("-u", "--user"):
            moduleArgs['user'] = arg
        elif opt in ("-p", "--password"):
            moduleArgs['password'] = arg
        elif opt in ("-P", "--pwdfile"):
            moduleArgs['pwdfile'] = arg
    return moduleArgs


# Main processing function
def main(argv):
    # Configure Parameters and Options
    options = 'e:u:p:P:'
    longOptions = ['endpoint=', 'user=', 'password=', 'pwdfile=']
    # Get Options & Arguments
    try:
        opts, args = getopt.getopt(argv, options, longOptions)
        # Read Module Arguments
        moduleArgs = readModuleArgs(opts, args)
    except getopt.GetoptError:
        usage()
    except Exception as e:
        print('Unknown Exception please check log file')
        logging.exception(e)
        sys.exit(1)

    return


# Main function to kick off processing
if __name__ == "__main__":
    main(sys.argv[1:])