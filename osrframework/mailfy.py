#!/usr/bin/env python
# -*- coding: cp1252 -*-
#
##################################################################################
#
#    Copyright 2015 Félix Brezo and Yaiza Rubio (i3visio, contacto@i3visio.com)
#
#    This program is part of OSRFramework. You can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##################################################################################

'''
mailfy.py Copyright (C) F. Brezo and Y. Rubio (i3visio) 2015
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it under certain conditions.  For additional info, visit to <http://www.gnu.org/licenses/gpl-3.0.txt>.
'''
__author__ = "Felix Brezo, Yaiza Rubio "
__copyright__ = "Copyright 2015, i3visio"
__credits__ = ["Felix Brezo", "Yaiza Rubio"]
__license__ = "GPLv3+"
__version__ = "v2.2"
__maintainer__ = "Felix Brezo, Yaiza Rubio"
__email__ = "contacto@i3visio.com"


import argparse
import datetime as dt
import json
import os
import sys

import osrframework.utils.banner as banner
import osrframework.utils.platform_selection as platform_selection
import osrframework.utils.general as general
# From emailahoy code
import emailahoy
from validate_email import validate_email
            
# Pending
#188.com", "21cn.cn", "popo.163.com", "vip.126.com", "vip.163.com", "vip.188.com"
EMAIL_DOMAINS = ["126.com", "163.com", "189.cn", "gmail.com", "hushmail.com", "keemail.me", "protonmail.com", "yandex.com", "yeah.net"]


def getMoreInfo(e):
    '''
        Method that calls different third party API.

        :param e:   Email to verify.

        :result:
    '''
    # Grabbing the email
    email = {}
    email["type"] = "i3visio.email"
    email["value"] = e
    email["attributes"] = []

    # Grabbing the alias
    alias = {}
    alias["type"] = "i3visio.alias"
    alias["value"] = e.split("@")[0]
    alias["attributes"] = []

    # Grabbing the domain
    domain= {}
    domain["type"] = "i3visio.domain"
    domain["value"] = e.split("@")[1]
    domain["attributes"] = []

    return email, alias, domain

def weCanCheckTheseDomains(email):
    '''
    '''
    # Known platform not to be working...
    notWorking = ["outlook.com", "hotmail.com", "@yahoo.", "@ymail", "@gmx.", "@inbox.", "@mail.ru", "@gandhi.net"]
    #notWorking = []
    for n in notWorking:
        if n in email:
            return False
    emailDomains = EMAIL_DOMAINS
    safe = False
    for e in emailDomains:
        if e in email:
            safe =  True
            break
    if not safe:
        print "WARNING: the domain of '" + email + "' will not be safely verified."
    return True

def performSearch(emails=[]):
    '''
        Method to perform the mail verification process.

        :param emails: List of emails.

        :return:
    '''
    results = []

    for e in emails:
        if weCanCheckTheseDomains(e):
            #if emailahoy.verify_email_address(e):
            try:
                is_valid = validate_email(e,verify=True)
            except TimeoutError as e:
                print "Something went wrong as a TimeoutError has been raised. Is your internet connection ready?"
                print "We recommend you to repeat this test..."
                is_validad = False
                

            if is_valid:
                email, alias, domain = getMoreInfo(e)
                aux = {}
                aux["type"] = "i3visio.profile"
                aux["value"] =  domain["value"]+ " - " +alias["value"]
                aux["attributes"]= []
                aux["attributes"].append(email)
                aux["attributes"].append(alias)
                aux["attributes"].append(domain)
                results.append(aux)
            else:
                pass
    return results

def grabEmails(emails=None, emailsFile=None, nicks=None, nicksFile=None, domains = EMAIL_DOMAINS):
    '''
        Method that globally permits to grab the emails.

        :param emails:  list of emails.
        :param emailsFile: filepath to the emails file.
        :param nicks:   list of aliases.
        :param nicksFile:  filepath to the aliases file.
        :param domains: domains where the aliases will be tested.

        :result:    list of emails to check,

    '''
    email_candidates = []
    if emails != None:
        email_candidates = emails
    elif emailsFile != None:
        with open(emailsFile, "r") as iF:
            email_candidates = iF.read().splitlines()
    elif nicks != None:
        for n in nicks:
            for d in domains:
                email_candidates.append(n+"@"+d)
    elif nicksFile != None:
        with open(nicksFile, "r") as iF:
            nicks = iF.read().splitlines()
            for n in nicks:
                for d in domains:
                    email_candidates.append(n+"@"+d)
    return email_candidates

def main(args):
    '''
        Main program.

        :param args: Arguments received in the command line.
    '''
    sayingHello = """mailfy.py Copyright (C) F. Brezo and Y. Rubio (i3visio) 2015
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it under certain conditions. For additional info, visit <http://www.gnu.org/licenses/gpl-3.0.txt>."""
    if not args.quiet:
        print banner.text

        print sayingHello
        print

    if sys.platform == 'win32':
        print "WARNING:"
        print "\tmailfy.py seems to be run in a Windows system."
        print "\tThe emailahoy libraries may NOT work properly. We are trying to find a fix for this issue."
        print

    # Processing the options returned to remove the "all" option
    if "all" in args.domains:
        domains = EMAIL_DOMAINS
    else:
        # processing only the given domains
        domains = args.domains

    if args.create_emails:  
        emails = grabEmails(nicksFile = args.create_emails, domains = domains)
    else:
        emails = grabEmails(emails=args.emails, emailsFile = args.emails_file, nicks=args.nicks, nicksFile = args.nicks_file, domains = domains)


    # Showing the execution time...
    if not args.quiet:
        startTime= dt.datetime.now()
        print str(startTime) +"\tStarting search of the following " + str(len(emails))+ " different emails: "+ str(emails) + ". Be patient!\n"

    results = performSearch(emails)

    # Trying to store the information recovered
    if args.output_folder != None:
        if not os.path.exists(args.output_folder):
            os.makedirs(args.output_folder)
        # Grabbing the results
        fileHeader = os.path.join(args.output_folder, args.file_header)
        for ext in args.extension:
            # Generating output files
            general.exportUsufy(results, ext, fileHeader)

    # Showing the information gathered if requested
    if not args.quiet:
        print "A summary of the results obtained are shown in the following table:"
        print unicode(general.usufyToTextExport(results))
        print

        print "You can find all the information collected in the following files:"
        for ext in args.extension:
            # Showing the output files
            print "\t-" + fileHeader + "." + ext

    # Showing the execution time...
    if not args.quiet:
        print
        endTime= dt.datetime.now()
        print str(endTime) +"\tFinishing execution..."
        print
        print "Total time used:\t" + str(endTime-startTime)
        print "Average seconds/query:\t" + str((endTime-startTime).total_seconds()/len(emails)) +" seconds"
        print

    # Urging users to place an issue on Github...
    if not args.quiet:
        print
        print "Did something go wrong? Is a platform reporting false positives? Do you need to integrate a new one?"
        print "Then, place an issue in the Github project: <https://github.com/i3visio/osrframework/issues>."
        print "Note that otherwise, we won't know about it!"
        print


def getParser():
    parser = argparse.ArgumentParser(description='mailfy.py - Checking the existence of a given mail.', prog='mailfy.py', epilog='Check the README.md file for further details on the usage of this program or follow us on Twitter in <http://twitter.com/i3visio>.', add_help=False)
    parser._optionals.title = "Input options (one required)"

    # Defining the mutually exclusive group for the main options
    groupMainOptions = parser.add_mutually_exclusive_group(required=True)
    # Adding the main options
    groupMainOptions.add_argument('--license', required=False, action='store_true', default=False, help='shows the GPLv3+ license and exists.')
    groupMainOptions.add_argument('-m', '--emails', metavar='<emails>', nargs='+', action='store', help = 'the list of emails to be checked.')
    groupMainOptions.add_argument('-M', '--emails_file', metavar='<emails_file>', action='store', help = 'the file with the list of emails.')
    groupMainOptions.add_argument('-n', '--nicks', metavar='<nicks>', nargs='+', action='store', help = 'the list of nicks to be checked in the domains selected.')
    groupMainOptions.add_argument('-N', '--nicks_file', metavar='<nicks_file>', action='store', help = 'the file with the list of nicks to be checked in the domains selected.')
    groupMainOptions.add_argument('--create_emails', metavar='<nicks_file>',  action='store', help = 'the file with the list of nicks to be created in the domains selected.')
    # Configuring the processing options
    groupProcessing = parser.add_argument_group('Processing arguments', 'Configuring the way in which mailfy will process the identified profiles.')
    #groupProcessing.add_argument('-L', '--logfolder', metavar='<path_to_log_folder', required=False, default = './logs', action='store', help='path to the log folder. If none was provided, ./logs is assumed.')
    groupProcessing.add_argument('-e', '--extension', metavar='<sum_ext>', nargs='+', choices=['csv', 'gml', 'json', 'mtz', 'ods', 'png', 'txt', 'xls', 'xlsx' ], required=False, default = ['xls'], action='store', help='output extension for the summary files. Default: xls.')
    groupProcessing.add_argument('-o', '--output_folder', metavar='<path_to_output_folder>', required=False, default = './results', action='store', help='output folder for the generated documents. While if the paths does not exist, usufy.py will try to create; if this argument is not provided, usufy will NOT write any down any data. Check permissions if something goes wrong.')
    groupProcessing.add_argument('-d', '--domains',  metavar='<candidate_domains>',  nargs='+', choices= ['all'] + EMAIL_DOMAINS, action='store', help='list of domains where the nick will be looked for.', required=False, default = ["all"])
    # Getting a sample header for the output files
    groupProcessing.add_argument('-F', '--file_header', metavar='<alternative_header_file>', required=False, default = "profiles", action='store', help='Header for the output filenames to be generated. If None was provided the following will be used: profiles.<extension>.' )
    groupProcessing.add_argument('--quiet', required=False, action='store_true', default=False, help='tells the program not to show anything.')

    # About options
    groupAbout = parser.add_argument_group('About arguments', 'Showing additional information about this program.')
    groupAbout.add_argument('-h', '--help', action='help', help='shows this help and exists.')
    #groupAbout.add_argument('-v', '--verbose', metavar='<verbosity>', choices=[0, 1, 2], required=False, action='store', default=1, help='select the verbosity level: 0 - none; 1 - normal (default); 2 - debug.', type=int)
    groupAbout.add_argument('--version', action='version', version='%(prog)s ' +" " +__version__, help='shows the version of the program and exists.')

    return parser

if __name__ == "__main__":
    # Grabbing the parser
    parser = getParser()

    args = parser.parse_args()

    # Calling the main function
    main(args)
