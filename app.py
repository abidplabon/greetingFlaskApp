import imp
from flask import Flask, render_template, request, flash,redirect,url_for,request
import os
import json
from uuid import uuid4
from operator import itemgetter
from werkzeug.utils import secure_filename
import numpy as np
import cv2
import requests

headings = ("ID","Paitent Name","Gender","Paitent Age","Clinic Name","Clinic ID","Diagnosis","Date","Doctor"," ")

result = 0
global checkData


app = Flask(__name__)
app.secret_key = "manbearpig_MUDMAN888"
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = 'static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

endpoint = "http://localhost:8601/v1/models/pneumonia_model:predict"
CLASS_NAMES = ["Normal", "Lung Opacity"]

@app.route("/welcome")
def index():
   return render_template("welcome.html")

@app.route('/index')
def Index():
    jsonFile = open("pneumoniadatacollection.json", "r")
    data = json.load(jsonFile)
    jsonFile.close()
    sortedVersion=sorted(data, key=itemgetter('type'))
    return render_template('index.html',data=sortedVersion)

@app.route('/edit/<id>',methods = ['POST','GET'])
def get_data(id):
    jsonFile = open("pneumoniadatacollection.json", "r+")
    data = json.load(jsonFile)
    
    for i in range(len(data)):
        if data[i]["ID"]==id:
            record = data[i]
    jsonFile.close()
    return render_template('edit.html',data= record)

@app.route('/update/<string:id>',methods=['POST'])
def update(id):
        paitentname = request.form.get('paitentname')
        gender      = request.form.get('gender')
        patientage  = request.form.get('patientage')
        clinicname  = request.form.get('clinicname')
        imageid     = request.form.get('imageid')
        type        = request.form.get('type')
        date        = request.form.get('date')
        doctorname  = request.form.get('doctorname')
        jsonFile = open("pneumoniadatacollection.json", "r+")
        data = json.load(jsonFile)
    
        for i in range(len(data)):
            if data[i]['ID']==id:
                data.pop(i)
                break
        entry={"ID":id,"paitentname":paitentname,"gender":gender,"patientage":patientage,"clinicname":clinicname,"imageid":imageid,"type":type,"date":date,"doctorname":doctorname}
        data.append(entry)
        with open('pneumoniadatacollection.json', 'w') as f:
            f.write(json.dumps(data, indent=9, separators=(',', ': ')))
        return redirect(url_for('Index'))
    
@app.route('/delete/<string:id>', methods = ['POST','GET'])
def delete(id):
    obj = json.load(open("pneumoniadatacollection.json","r+"))
    for i in range(len(obj)):
        if obj[i]['ID']==id:
            obj.pop(i)
            break
    open("pneumoniadatacollection.json","w").write(
        json.dumps(obj,sort_keys=True,indent=4,separators=(',',':'))
    )
    return render_template("index.html")

@app.route("/form")
def form():
    return render_template('upload.html')

@app.route("/upload", methods=["POST"])
def upload():
    paitentname = request.form.get("paitentname")
    gender = request.form.get("gender")
    paitentage = request.form.get("paitentage")
    clinicname=request.form.get("clinicname")
    imageid= request.form.get("imageid")
    type=request.form.get("type")
    date=request.form.get("date")
    doctorname=request.form.get("doctorname")
    
    # Image folder 
    target = os.path.join(APP_ROOT, 'static/images/')
    # target = os.path.join(APP_ROOT, 'static/')
    targetReport = os.path.join(APP_ROOT,'report/')
    
    targetRep = os.path.join(APP_ROOT,'doctoroffice/')

    if not os.path.isdir(target):
            os.mkdir(target)
    if not os.path.isdir(targetReport):
            os.mkdir(targetReport)
    if not os.path.isdir(targetRep):
            os.mkdir(targetRep)
    for upload in request.files.getlist("file"):
        file_name = str(uuid4())
        print(file_name)
        destination = "/".join([target, f'{file_name}.jpg'])
        upload.save(destination)
    for uploadReport in request.files.getlist("file1"):
        destinationReport = "/".join([targetReport, f'{file_name}.jpg'])
        uploadReport.save(destinationReport)
    for uploadRep in request.files.getlist("fil"):
        destinationRep = "/".join([targetRep, f'{file_name}.jpg'])
        uploadRep.save(destinationRep)
    
    jsonfilename='pneumoniadatacollection.json'


    if os.path.getsize(jsonfilename) == 0:
        entryFirst = [{"ID":file_name,"paitentname":paitentname,"gender":gender,"patientage":paitentage,"clinicname":clinicname,"imageid":imageid,"type":type,"date":date,"doctorname":doctorname}]
        with open(jsonfilename,mode='w') as f:
            json.dump(entryFirst,f)
    else:
        with open(jsonfilename, "r+") as file:
            data = json.load(file)
            entry={"ID":file_name,"paitentname":paitentname,"gender":gender,"patientage":paitentage,"clinicname":clinicname,"imageid":imageid,"type":type,"date":date,"doctorname":doctorname}
        for element in data:
            if(element['paitentname'] == entry['paitentname'] and element['imageid'] == entry['imageid']):
                checkData = "Not Found"
                break
            else:
                checkData = "Found"
                
        if checkData == "Found":
            print("Okay Working")
            data.append(entry)
            with open(jsonfilename,'w') as file:
                json.dump(data,file)
            

    return render_template("upload.html")

@app.route("/detection")
def detection():
    return render_template('detection.html')


@app.route("/detectResult")
def detectResult():
    return render_template('complete.html')



@app.route("/searchPage")
def searchID():
    return render_template('search.html')

@app.route("/search",methods=['GET','POST'])
def search():
    obj = json.load(open("pneumoniadatacollection.json","r+"))
    #if request.method == "POST":
    get_imageid = request.form.get("imageid")
    for i in range(len(obj)):
        if obj[i]['imageid']==get_imageid:
            record=obj[i]
            found_imageid=record['imageid']
            print(found_imageid)
            #return redirect(url_for('confirm',imageid=found_imageid))
            return redirect(url_for('confirmPage',imageid=found_imageid))
    return render_template("search.html")


@app.route("/confirm/<string:imageid>",methods=['GET','POST'])
def confirmPage(imageid): 
    jsonFile = open("pneumoniadatacollection.json", "r+")
    data = json.load(jsonFile)
    
    for i in range(len(data)):
        if data[i]["imageid"]==imageid:
            record = data[i]
            full_filename = record['ID']
            print(full_filename)
    jsonFile.close()
    return render_template('confirm.html',data= record,user=full_filename)
    #return render_template('confirm.html')
    
@app.route('/DiagnosisConfirmed/<string:imageid>',methods=['POST'])
def diagnosisConfirmed(imageid):
        ID = request.form.get('ID')
        print(ID)
        paitentname = request.form.get('paitentname')
        print(paitentname)
        gender      = request.form.get('gender')
        print(gender)
        patientage  = request.form.get('patientage')
        print(patientage)
        clinicname  = request.form.get('clinicname')
        print(clinicname)
        imageid     = request.form.get('imageid')
        print(imageid)
        type        = request.form.get('type')
        print(type)
        date        = request.form.get('date')
        print(date)
        doctorname  =request.form.get('doctorname')
        print(doctorname)
        jsonFile = open("pneumoniadatacollection.json", "r+")
        data = json.load(jsonFile)
    
        for i in range(len(data)):
            if data[i]['imageid']==imageid:
                
                data.pop(i)
                print("data deleted")
                break
                
        entry={"ID":ID,"paitentname":paitentname,"gender":gender,"patientage":patientage,"clinicname":clinicname,"imageid":imageid,"type":type,"date":date,"doctorname":doctorname}
        data.append(entry)
        with open('pneumoniadatacollection.json', 'w') as f:
            f.write(json.dumps(data, indent=9, separators=(',', ': ')))
        return render_template("search.html")

@app.route("/complete",methods=['POST','GET'])
async def complete():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)  #Use this werkzeug method to secure filename.
            destination = os.path.join(app.config['UPLOAD_FOLDER'],filename) 
            file.save(destination)

            image = cv2.imread(destination)
            img_batch = np.expand_dims(image, 0)

            json_data = {
                "instances": img_batch.tolist()
            }

            #print(json_data)

            response = requests.post(endpoint, json=json_data)
            prediction = np.array(response.json()["predictions"][0])

            predicted_class = CLASS_NAMES[np.argmax(prediction)]
            confidence = np.max(prediction)

            label = predicted_class
            print('---------------')
            print(label)
            print('---------------')
            flash(label)
            full_filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            flash(full_filename)
            return render_template('detection.html')


@app.route("/hello")
def indexs():
	flash("what's your name?")
	return render_template("indexs.html")

@app.route("/greet", methods=['POST', 'GET'])
def greeter():
	flash("Hi " + str(request.form['name_input']) + ", great to see you!")
	return render_template("indexs.html")