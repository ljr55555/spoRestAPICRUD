# Functions for using SharePoint REST API for CRUD operations on a list

Copy config.sample to config.py and insert your values. Credentials are not stored in clear text. You can use stashStringForConfig.py to get strings to store in config.py

Example script uses a list with columns for Title, SiteID, MailingAddress, City, State, and ZipCode

```
C:\ljr\git\spoRestAPICRUD>python crudExample.py
SAML Assertion received.n...
BinarySecurityToken received.
ADFS Authentication successful
Successfully created record
Full list:
123456: Bedford Office
234567: Twinsburg Office
345678: Twinsburg Office
List filtered with SiteID eq 234567:
234567: Twinsburg Office
Update will be made to record id 21
Successfully updated record 21
345678: Rochester Office
Successfully deleted record 21
```

More details on using the script can be found at (http://lisa.rushworth.us/?p=4583)[http://lisa.rushworth.us/?p=4583]
