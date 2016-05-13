#!/usr/bin/env python2

import os
import datetime
import time
import pickle
import zlib

class DataCollector:
    """Manages data collection from a revision control repository."""
    def __init__(self):
        self.stamp_created = time.time()
        self.cache = {}

        self.total_authors = 0
        self.activity_by_hour_of_day = {} # hour -> commits
        self.activity_by_day_of_week = {} # day -> commits
        self.activity_by_month_of_year = {} # month [1-12] -> commits
        self.activity_by_hour_of_week = {} # weekday -> hour -> commits
        self.activity_by_hour_of_day_busiest = 0
        self.activity_by_hour_of_week_busiest = 0
        self.activity_by_year_week = {} # yy_wNN -> commits
        self.activity_by_year_week_peak = 0

        self.authors = {} # name -> {commits, first_commit_stamp, last_commit_stamp, last_active_day, active_days, lines_added, lines_removed}

        self.total_commits = 0
        self.total_files = 0
        self.authors_by_commits = 0

        # domains
        self.domains = {} # domain -> commits

        # author of the month
        self.author_of_month = {} # month -> author -> commits
        self.author_of_year = {} # year -> author -> commits
        self.commits_by_month = {} # month -> commits
        self.commits_by_year = {} # year -> commits
        self.lines_added_by_month = {} # month -> lines added
        self.lines_added_by_year = {} # year -> lines added
        self.lines_removed_by_month = {} # month -> lines removed
        self.lines_removed_by_year = {} # year -> lines removed
        self.first_commit_stamp = 0
        self.last_commit_stamp = 0
        self.last_active_day = None
        self.active_days = set()

        # lines
        self.total_lines = 0
        self.total_lines_added = 0
        self.total_lines_removed = 0

        # size
        self.total_size = 0

        # timezone
        self.commits_by_timezone = {} # timezone -> commits

        # tags
        self.tags = {}

        self.files_by_stamp = {} # stamp -> files

        # extensions
        self.extensions = {} # extension -> files, lines

        # line statistics
        self.changes_by_date = {} # stamp -> { files, ins, del }

    ##
    # This should be the main function to extract data from the repository.
    def collect(self, dir, project_name = None):
        self.dir = dir
        if project_name:
            self.projectname = project_name
        else:
            self.projectname = os.path.basename(os.path.abspath(dir))

    ##
    # Load cacheable data
    def loadCache(self, cachefile):
        if not os.path.exists(cachefile):
            return
        print('Loading cache...')
        f = open(cachefile, 'rb')
        try:
            self.cache = pickle.loads(zlib.decompress(f.read()))
        except:
            # temporary hack to upgrade non-compressed caches
            f.seek(0)
            self.cache = pickle.load(f)
        f.close()

    ##
    # Save cacheable data
    def saveCache(self, cachefile):
        print('Saving cache...')
        tempfile = cachefile + '.tmp'
        f = open(tempfile, 'wb')
        #pickle.dump(self.cache, f)
        data = zlib.compress(pickle.dumps(self.cache))
        f.write(data)
        f.close()
        try:
            os.remove(cachefile)
        except OSError:
            pass
        os.rename(tempfile, cachefile)

    ##
    # Produce any additional statistics from the extracted data.
    def refine(self):
        pass

    # dict['author'] = { 'commits': 512 } - ...key(dict, 'commits')
    def getkeyssortedbyvaluekey(self, d, key):
        return map(lambda el : el[1], sorted(map(lambda el : (d[el][key], el), d.keys())))

    ##
    # : get a dictionary of author
    def getAuthorInfo(self, author):
        return self.authors[author]

    def getActivityByDayOfWeek(self):
        return self.activity_by_day_of_week

    def getActivityByHourOfDay(self):
        return self.activity_by_hour_of_day

    def getActiveDays(self):
        return self.active_days

    def getDomains(self):
        return self.domains.keys()

    # : get a dictionary of domains
    def getDomainInfo(self, domain):
        return self.domains[domain]

    ##
    # Get a list of authors
    def getAuthors(self, limit = None):
        res = self.getkeyssortedbyvaluekey(self.authors, 'commits')
        res.reverse()
        return res[:limit]

    def getFirstCommitDate(self):
        return datetime.datetime.fromtimestamp(self.first_commit_stamp)

    def getLastCommitDate(self):
        return datetime.datetime.fromtimestamp(self.last_commit_stamp)

    def getCommitDeltaDays(self):
        return (self.last_commit_stamp / 86400 - self.first_commit_stamp / 86400) + 1

    def getStampCreated(self):
        return self.stamp_created

    def getTags(self):
        return self.tags.keys().sort()

    def getTotalAuthors(self):
        return self.total_authors

    def getTotalCommits(self):
        return self.total_commits

    def getTotalFiles(self):
        return self.total_files

    def getTotalLOC(self):
        return self.total_lines

    def getTotalSize(self):
        return self.total_size

