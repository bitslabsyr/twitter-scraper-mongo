# BITS Lab Twitter Scraper Mongo

This package fetches Twitter timelines for a specified set of Twitter users. It writes data obtained from Twitter to a Mongo database. After collecting all timelines for specified users, the code begins again after waiting 1 hour. 

This package creates 3 collections inside the Mongo database:
1) TW_cand:  
   * This collection contains 1 document for each tweet collected. If this package collects a tweet that already exists in this collection, it updates the sharing metrics at the tweet level (retweet count and favorite count) and the user level (followers count, friends count, and listed count) with the latest information for these metrics.
2) TW_cand_crawl_history:  
   * This collection contains 1 document for each time each tweet is collected. That means this collection will contain _many_ more items than the number of unique tweets. Each document in this collection contains a tweet ID, the time that information for the tweet was collected, and sharing metrics at the tweet level (retweet count and favorite count) and at the user level (followers count, friends count, and listed count) from the time the information was collected. This collection allows us to do longitudinal analysis fo sharing metrics at a fairly granular level.
3) TW_cand_info:  
   * This collection contains 1 document for each user whose timelines are being collected. Each document contains a user name, screenname, id number, and the latest sharing metrics (friends count, followers count, and listed count). It also contains the time when this information is collected. This collection provides easy access to this core user information. 

### Installation and setup

To run this package:  
1) Clone the code to your server using `git clone https://github.com/bitslabsyr/twitter-scraper-mongo.git`.    
2) Rename `config_template.py` to `config.py`.
3) Modify the parameters in config.py to match your preferences. This file contains configuration information that will always be used for this installation of this package. 
    1) Modify [Mongo credentials](https://github.com/bitslabsyr/twitter-scraper-mongo/blob/master/config_template.py#L6) to match your Mongo instance.  
    2) Modify [COLLECT_FROM](https://github.com/bitslabsyr/twitter-scraper-mongo/blob/master/config_template.py#L11) with the date for the earliest tweet you want to collect. If you want all tweets with no date restriction, replace datetime object with "False".
4) Make a copy of `input.txt` with an informative name. This file contains configuration information specific to a particular process. You can have multiple main.py running at the same time, each with a different input.txt file.
5) Modify the parameters of your input file. Notice that this is a plaintext file, not a python file. That means you *should not* use python syntax in this file. In other words, don't use quotes for *anything*.
   1) Modify the [name of the Mongo database](https://github.com/bitslabsyr/twitter-scraper-mongo/blob/master/input.txt#L1) where this package will insert data.
   2) Modify the [Twitter credentials](https://github.com/bitslabsyr/twitter-scraper-mongo/blob/master/input.txt#L2) this package will use to pull data.
   3) Modify [TERMS_LIST](https://github.com/bitslabsyr/twitter-scraper-mongo/blob/master/input.txt#L6) with the list of accounts whose timelines you want to collect. This should be a comma-separated list of account usernames. 
6) Run with `sudo python3 main.py {input_filename.txt} >> {log_filename.txt} 2>&1 &`
7) If you want to collect an additional set of users with a different set of Twitter credentials (for example, to reduce the chance of rate limits), repeat steps 4 through 6 as many times as you want.

### A word about Mongo

Since this code checks to see whether each tweet that it collects exists in the database before inserting it, it can be computationally expensive. It is a good idea to index TW_cand on "id" (this is the tweet id) and TW_cand_info on "id" (this is the user id). This will both speed up the processes and reduce the CPU load. 

### Requirements

This code was developed and tested with Python3.
       