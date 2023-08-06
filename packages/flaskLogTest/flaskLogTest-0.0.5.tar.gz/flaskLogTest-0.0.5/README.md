without logs,or good undertanding of them  debuuging an aplication through an error starck can be challanging ,therefore flask logger monitors,collect and analyza sers activities in the application
important of the tools
    1.Detect suspecious user activities
    2.can be imortant in the line of defense aganist data breaches & cyber compromises

INSTALLATION
    pip install flaskLogTest
USAGE
    from beansofts.flasklogger import *

    DECORATORS
        @registerusers
            the decorator collects and stores users credetials anylyze and append unique data 
        @login ,@apiKeys
            the decoraors works the same as @registerusers
            