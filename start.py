import pdfkit
import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import sys
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice, TagExtractor
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
from pdfminer.cmapdb import CMapDB
from pdfminer.layout import LAParams
from pdfminer.image import ImageWriter
from werkzeug import secure_filename
app = Flask(__name__,template_folder='.')#Need to specify the template folder

def mypdf2txt(argv):
    import getopt
    def usage():
        print ('usage: %s [-d] [-p pagenos] [-m maxpages] [-P password] [-o output]'
               ' [-C] [-n] [-A] [-V] [-M char_margin] [-L line_margin] [-W word_margin]'
               ' [-F boxes_flow] [-Y layout_mode] [-O output_dir] [-R rotation]'
               ' [-t text|html|xml|tag] [-c codec] [-s scale]'
               ' file ...' % argv[0])
        return 100
    try:
        (opts, args) = getopt.getopt(argv[1:], 'dp:m:P:o:CnAVM:L:W:F:Y:O:R:t:c:s:')
    except getopt.GetoptError:
        return usage()
    if not args: return usage()
    # debug option
    debug = 0
    # input option
    password = ''
    pagenos = set()
    maxpages = 0
    # output option
    outfile = None
    outtype = None
    imagewriter = None
    rotation = 0
    layoutmode = 'normal'
    codec = 'utf-8'
    pageno = 1
    scale = 1
    caching = True
    showpageno = True
    laparams = LAParams()
    for (k, v) in opts:
        if k == '-d': debug += 1
        elif k == '-p': pagenos.update( int(x)-1 for x in v.split(',') )
        elif k == '-m': maxpages = int(v)
        elif k == '-P': password = v
        elif k == '-o': outfile = v
        elif k == '-C': caching = False
        elif k == '-n': laparams = None
        elif k == '-A': laparams.all_texts = True
        elif k == '-V': laparams.detect_vertical = True
        elif k == '-M': laparams.char_margin = float(v)
        elif k == '-L': laparams.line_margin = float(v)
        elif k == '-W': laparams.word_margin = float(v)
        elif k == '-F': laparams.boxes_flow = float(v)
        elif k == '-Y': layoutmode = v
        elif k == '-O': imagewriter = ImageWriter(v)
        elif k == '-R': rotation = int(v)
        elif k == '-t': outtype = v
        elif k == '-c': codec = v
        elif k == '-s': scale = float(v)
    #
    PDFDocument.debug = debug
    PDFParser.debug = debug
    CMapDB.debug = debug
    PDFResourceManager.debug = debug
    PDFPageInterpreter.debug = debug
    PDFDevice.debug = debug
    #
    rsrcmgr = PDFResourceManager(caching=caching)
    if not outtype:
        outtype = 'text'
        if outfile:
            if outfile.endswith('.htm') or outfile.endswith('.html'):
                outtype = 'html'
            elif outfile.endswith('.xml'):
                outtype = 'xml'
            elif outfile.endswith('.tag'):
                outtype = 'tag'
    if outfile:
        outfp = file(outfile, 'w')
    else:
        outfp = sys.stdout
    if outtype == 'text':
        device = TextConverter(rsrcmgr, outfp, codec=codec, laparams=laparams,
                               imagewriter=imagewriter)
    elif outtype == 'xml':
        device = XMLConverter(rsrcmgr, outfp, codec=codec, laparams=laparams,
                              imagewriter=imagewriter)
    elif outtype == 'html':
        device = HTMLConverter(rsrcmgr, outfp, codec=codec, scale=scale,
                               layoutmode=layoutmode, laparams=laparams,
                               imagewriter=imagewriter)
    elif outtype == 'tag':
        device = TagExtractor(rsrcmgr, outfp, codec=codec)
    else:
        return usage()
    for fname in args:
        fp = file(fname, 'rb')
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.get_pages(fp, pagenos,
                                      maxpages=maxpages, password=password,
                                      caching=caching, check_extractable=True):
            page.rotate = (page.rotate+rotation) % 360
            interpreter.process_page(page)
        fp.close()
    device.close()
    outfp.close()
    return
@app.route("/")
def hello():
    return "DOCSPAD - Now access, view, edit, annotate your documents with ease :)"

@app.route("/preview")
def preview():
	try:
		fid=int(request.args.get('id'));
		print fid
		db=sqlite3.connect('docspad.db')
		cur=db.cursor()
		record=cur.execute("select * from details where pid="+str(fid))
		mc=0;
		for ls in record:
			pname=ls[1];
			mc=mc+1;
		if(mc==0):
			disp_msg="Invalid Id"
		else:			
			print "Working check point"
			argv="pdf2txt -o temp.txt -t text out.pdf"
			argv=argv.replace("out.pdf",os.path.join(app.config['UPLOAD_FOLDER'], pname));
			argv=argv.split();
			mypdf2txt(argv); #pdf to text conversion done
			contents=open("temp.txt")
			myhtml=""
			for lines in contents.readlines():
				myhtml=myhtml+"<pre>" + lines + "</pre>"
			disp_msg=myhtml
		db.commit();
		db.close();
		return disp_msg
	except Exception as e:
		print e;
		return "Error occurred"
		

@app.route("/download")
def download():
	try:
		#~ return "lol"
		uploads=""
		fid=int(request.args.get('id'));
		print fid
		db=sqlite3.connect('docspad.db')
		cur=db.cursor()
		record=cur.execute("select * from details where pid="+str(fid))
		mc=0;
		for ls in record:
			pname=ls[1];
			mc=mc+1;
		if(mc==0):
			disp_msg="Invalid Id"
		else:		
			#~ print "here"	
			print "Working check point"
			uploads = app.config['UPLOAD_FOLDER']
			#~ print "here"
			print "here ",uploads
			return send_from_directory(directory=uploads, filename=pname)
			return "Sorry"
		db.commit();
		db.close();
		return "Sorry"
	except Exception as e:
		print e;
		return "Error occurred"
		
	
@app.route("/rename")
def rename():
	try:
		fid=int(request.args.get('id'));
		fname=request.args.get('name');
		print fid
		db=sqlite3.connect('docspad.db')
		cur=db.cursor()
		record=cur.execute("select * from details where pid="+str(fid))
		mc=0;
		for ls in record:
			pname=ls[1];
			mc=mc+1;
		if(mc==0):
			display_msg="Invalid Id"
		else:		
			record=cur.execute("select * from details where pname="+"'"+fname+"'");
			mc=0;
			for ls in record:
				mc=mc+1;
			if(mc>0):
				display_msg="Sorry can't rename since file with same name already exists.";
			else:
				display_msg="File successfully renamed";	
				cur.execute("update details set pname="+"'"+fname+"'"+" where pname = "+"'"+pname+"' and pid="+str(fid))
				os.rename(os.path.join(app.config['UPLOAD_FOLDER'], pname),os.path.join(app.config['UPLOAD_FOLDER'], fname));
		db.commit();
		db.close();
		return display_msg
	except Exception as e:
		print e;
		return "Error occurred"

@app.route("/delete")
def delete():
	try:
		fid=int(request.args.get('id'));
		print fid
		db=sqlite3.connect('docspad.db')
		cur=db.cursor()
		record=cur.execute("select * from details where pid="+str(fid))
		mc=0;
		for ls in record:
			pname=ls[1];
			mc=mc+1;
		if(mc==0):
			display_msg="Invalid Id"
		else:		
			display_msg="File successfully deleted";	
			cur.execute("delete from details where pid ="+str(fid))
			os.remove(os.path.join(app.config['UPLOAD_FOLDER'], pname));
		db.commit();
		db.close();
		return display_msg
	except Exception as e:
		print e;
		return "Error occurred"

@app.route("/edit")
def edit():
	try:
		fid=int(request.args.get('id'));
		print fid
		db=sqlite3.connect('docspad.db')
		cur=db.cursor()
		record=cur.execute("select * from details where pid="+str(fid))
		mc=0;
		for ls in record:
			pname=ls[1];
			mc=mc+1;
		if(mc==0):
			disp_msg="Invalid Id"
		else:			
			print "Working check point 2"
			argv="pdf2txt -o temp.txt -t text out.pdf"
			argv=argv.replace("out.pdf",os.path.join(app.config['UPLOAD_FOLDER'], pname));
			argv=argv.split();
			mypdf2txt(argv); #pdf to text conversion done
			contents=open("temp.txt")
			mydata=""
			for lines in contents.readlines():
				mydata=mydata+ lines
			return '<h1>Edit Mode</h1><form action="/save" method="POST" enctype=multipart/form-data> <textarea rows =35 cols=55 name="ta" autofocus>'+mydata+'</textarea><br><br><input type="submit" name="myok" value="Save">&nbsp&nbsp<input type="submit" name="myok" value="Cancel">'+'<input type="hidden" name="hfname" value="'+pname+'"></form>'
	except Exception as e:
		print e;
		return "Error occurred"
		
		
@app.route("/upload")
def upload():
    return '<h1>Upload File</h1><form action="/upload_it" method="POST" enctype=multipart/form-data> <input type="file" name="myfile"><br><br><input type="submit" name="myok" value="Ok"><input type="submit" name="myok" value="Cancel"></form>'

@app.route("/upload_it",methods=['POST'])
def upload_it():
	try:
		 db=sqlite3.connect('docspad.db')
	 	 cur=db.cursor()
		 record=cur.execute("select * from getid")
		 record=cur.fetchone()
		 x=int(record[0]);
		 myfile=request.files['myfile']
		 fname = secure_filename(myfile.filename)
		 if(request.form['myok']=='Ok'):
			if(fname.strip()==""):
				display_msg="No file selected"
			else:
				if (fname.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']):
					myfile.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
					record=cur.execute("select * from details where pname="+"'"+fname+"'");
					mc=0;
					for ls in record:
						mc=mc+1;
					if(mc>0):
						display_msg="Sorry file with same name already exists.";
					else:
						cur.execute("insert into details values("+str(x+1)+',"'+fname+'"'+")");
						cur.execute("update getid set sid="+str(x+1)+" where sid = "+str(x))
						display_msg="File with Id "+str(x+1)+" successfully uploaded";
				else:
					display_msg="Invalid file format"
	 	 else:
			display_msg="No file selected"
		 db.commit();
		 db.close();
		 return display_msg
	except Exception as e:
		print str(e)
		return "Error Occurred"
		
	
@app.route("/list")    
def mylist():
	try:
		print "Listings of documents in the cloud"
		db=sqlite3.connect('docspad.db')
	 	cur=db.cursor()
	 	record=cur.execute("select * from details")
	 	mc=0;
	 	display_msg="<pre><b>Id Filename</b></pre>"
	 	for ls in record:
			mc=mc+1;
			display_msg="<pre>"+display_msg+str(ls[0])+" "+str(ls[1])+"</pre>"
		if(mc==0):
			display_msg="Your Dashboard is empty";
		db.commit();
		db.close();
		return display_msg;
	except Exception as e:
		print e
		return "Error occured"

@app.route("/save",methods=['POST'])    
def save():
	if(request.form['myok']=='Save'):
		s = request.form['ta']
		s=s.split('\n')
		pname=request.form['hfname']
		print pname
		with open("temp.html", "w") as e:
			e.write("<html>");
			for l in s:
				e.write("<pre>"+l+"</pre>");
			e.write("</html>");
		pdfkit.from_url('temp.html',os.path.join(app.config['UPLOAD_FOLDER'],pname))
		return "File successfully saved";
	else:
		return "No changes made"
 
if __name__ == '__main__':
	app.config['UPLOAD_FOLDER'] = './uploads/'
	app.config['ALLOWED_EXTENSIONS'] = set(['pdf'])
	app.run(port=5000,debug=True)
