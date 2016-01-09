Bookpad/Docspad is a technology that provides developers with easily integratable API’s for various
document handling tools like

Previewing documents
Editing documents
Annotating documents
Update histories
Download documents
Rename, delete documents & more

A set of easy to use APIs that bring instant document handling to web, mobile and native applications

Technology Used
➔ Python as programming Language.
➔ Flask, a python based micro​web application framework to expose API’s & request
the Cloud web server.
➔ Sqlite Database which keeps details about documents on the Cloud.

Why python Flask??
★ Built in development server and debugger
★ Integrated unit testing support
★ RESTful request dispatching
★ Uses Jinja2 templating
★ Supports for secure cookies (client side sessions)
★ 100% WSGI 1.0 compliant
★ Unicode based
★ Extensively documented
★ Lightweight & takes care of other concurrency and similar stuffs.

API’s Exposed
/list     list all user's document in the cloud
/upload   helps to upload document to the cloud
/preview  helps to preview document in the cloud
/download helps to download document in the cloud
/edit     helps to edit document in the cloud itself & save the changes
/rename   helps to rename the document in the cloud
/delete   helps to delete the unwanted documents from the cloud

Demo
https://www.youtube.com/watch?v=tbpXmuUj_xo

How to run??
1)First run configure.py
  python configure.py
2)Then the main script start.py can be run, access the server with a web browser & perform document handling tasks from remote login.


API’s Exposed
http://server/list/
http://server/upload/
http://server/preview?id=docid
http://server/download?id=docid
http://server/edit?id=docid
http://server/rename?id=docid&name=newname
http://server/delete?id=docid
