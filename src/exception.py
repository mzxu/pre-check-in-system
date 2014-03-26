'''
Created on Jul 31, 2012

@author: Mingze
'''
from log import log

class Error(Exception):
    """
    Base class for exceptions in this module.
    """    
    pass

class UnableParsePostDataError(Error):
    """
    Exception raised for errors in parsing data posted.
    """

    def __init__(self, 
                 message = "Invalid json data",
                 status = "101"):
        self.message = message
        self.status = status
        log.error(message)

class NoAuthorFoundError(Error):
    """
    Exception raised if no valid author found.
    """

    def __init__(self, 
                 message = "No Author found, cannot trigger tests", 
                 status = "102"):
        self.message = message
        self.status = status
        log.error(message)

class NoValidJobFoundError(Error):
    """
    Exception raised if no jobs to trigger.
    """

    def __init__(self, 
                 message = "No triggerable jobs found", 
                 status = "103"):
        self.message = message
        self.status = status
        log.error(message)

class IncorrectCIServerPrefixError(Error):
    """
    Exception raised for incorrect CI server prefix.
    """
    def __init__(self, 
                 message = "Incorrect CI server prefix", 
                 status = "104"):
        self.message = message
        self.status = status
        log.error(message)
        
class IncorrectCIServerSuffixError(Error):
    """
    Exception raised for incorrect CI server suffix.
    """
    def __init__(self, 
                 message = "Incorrect CI server suffix", 
                 status = "105"):
        self.message = message
        self.status = status
        log.error(message)

class NoJobTriggeredError(Error):
    """
    Exception raised for incorrect CI server suffix.
    """
    def __init__(self, 
                 message = "No jobs can be triggerred", 
                 status = "106"):
        self.message = message
        self.status = status
        log.error(message)
        
class AuthenticationError(Error):
    """
    Exception raised for incorrect CI server suffix.
    """
    def __init__(self, 
                 message = "Authentication failed", 
                 status = "107"):
        self.message = message
        self.status = status
        log.error(message)

class InvalidQueryStringError(Error):
    """
    Exception raised for incorrect CI server suffix.
    """
    def __init__(self, 
                 message = "Invalid query string", 
                 status = "108"):
        self.message = message
        self.status = status
        log.error(message)