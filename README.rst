Logwatcher
==========

Usage
-----

* Launch the server with : `python logwatcher.py`
* Launch the page logwatcher.hmtl in your favorite browser.
* Add a file to watch (relative path beginning with "./", absolute with "/") that is readable by the user who launched the server.
* Check the box "Watch"
* Modify the watched file with for example `cat >> file_to_watch.txt`
* See the magic happen as the modifications are pushed to the client via WebSockets

Dependencies
------------

Python, Twisted, autobahn

Screencast
----------

http://www.youtube.com/watch?v=pzfL7eZ4Iwc 
