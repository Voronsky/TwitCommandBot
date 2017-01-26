import argparse
import json
import logging
import os
import requests
import smtplib
import sys
import tweepy
from email.mime.text import MIMEText
from sparkpost import SparkPost
from modules.credentials import *

api = "" # Will be used as a global var
obj = "" # Will be used as another global var for the credentials module


class RemoteCommand(object):
    """ Will create an object with a given command and an error status

        keyword argument:
        object -- the object to which to instantiate

        returns the object
    """

    def __init__(self):
        self.command = ''
        self.error = None

    def execCmd(self,string):
        try:
            if "!" in string:
                self.command = string[1:]
                logging.debug('Cmd found: '+string)
                os.system(self.command)
        except Exception as e:
            self.error = e


def login(file):
    """ defines the global variables to the values based on
    what was passed in through the credentials file.

    keyword arguments: 
    file -- the credentials file that was passed in to
               execute the script
    """

    global api #We are going to access the 'global' api variable
    global obj
    credsFile = file
    obj = CredentialsReader(credsFile)
    obj.setTwitterApi()
    conKey = obj.creds['CONSUMER_KEY']
    conSecret = obj.creds['CONSUMER_SECRET']
    access_token = obj.creds['ACCESS_TOKEN']
    access_secret = obj.creds['ACCESS_SECRET']
    auth = tweepy.OAuthHandler(conKey, conSecret)
    auth.set_access_token(access_token,access_secret)
    api = tweepy.API(auth, parser=tweepy.parsers.JSONParser()) # tells tweety to make the status object JSON serializable because it is not by default

def getLatestCommand(twitHandle):
    """ returns latest twitter command made as a 'status'

    keyword arguments: 
    twitHandle -- The twitter handle name to grab commands from
    """

    response = api.user_timeline(twitHandle,count=1)
    command = response[0]['text']
    return command

def emailReport(os_command,err):
    """ Emails success or failure with a given SMTP defined by the credentials
    file

    keyword arguments: 
    os_command -- The command found and to be executed
    err -- boolean value which indicates if the command was successful
    """

    recipients = [obj.creds['To']]
    from_email = obj.creds['From']
    if err is not None:
        body = '<html><body><p>A command:\n' + os_command + \
               '\nwas unsuccessful:\nError: '+err + '</p></body></html'
    else:
        body = '<html><body><p>A command:\n' + os_command + \
               '\nsent successfully </p></body></html>'

    subject = obj.creds['Subject']

    """send message via our own SMTP server"""
    sparkykey = obj.creds['SPARKPOST_APIKEY']
    sparky = SparkPost(sparkykey)
    response = sparky.transmission.send(recipients=recipients,html=body,from_email=from_email,subject=subject)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Executes commands remotely using Twitter')
    parser.add_argument('-f', '--file',dest='file',
                        help='Pass the TEXT file carrying credentials')
    parser.add_argument('-v','--version',action='version',
                        version="%(prog)s 1.0",help="Prints out current version of script")
    parser.add_argument('-s','--smtp',dest='smtp', help='Specify the specific SMTP service that will be used')
    parser.add_argument('-l','--list',dest='list',action='store_true', help='displays the available list of SMTP services')
    args = parser.parse_args()
    if args.list:
        print('list of supported SMTP services:\nSparkPost')
        sys.exit(0)
    
    login(args.file)
    twitterCmd = getLatestCommand('ChillinIvan')
    print(twitterCmd)
    remoteCmd = RemoteCommand()
    remoteCmd.command = twitterCmd
    emailReport(remoteCmd.command,remoteCmd.error)

