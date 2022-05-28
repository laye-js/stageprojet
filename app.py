from flask import Flask,render_template,url_for,request,redirect, make_response,session,g,jsonify
import json, csv
from time import time
from datetime import datetime
from random import random, randint
from flask_mail import Mail,Message
import os,re
import numpy
import sqlite3 

########DB######
con = sqlite3.connect("markersdata.db")  
print("Database opened successfully")  
#####################

############################################# 110000 points ###########################################

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/', methods=['GET', 'POST'])
def main():
    if ('user' in session) and ('email' in session):
        con = sqlite3.connect("markersdata.db")  
        con.row_factory = sqlite3.Row  
        cur = con.cursor()  
        cur.execute("select * from markersdata ORDER BY id DESC limit  150") 
        rows = cur.fetchall()  
        return render_template("accueil.html",rows = rows) 
    if request.method == 'POST': 
        session.pop('user',None)
        session.pop('email',None)

        if request.form['user'] == 'admin':
            regex = r'\b[A-Za-z0-9._%+-]+@gmail+\.[A-Z|a-z]{2,}\b' 
            regex2 = r'\b[A-Za-z0-9._%+-]+@prose+\.[A-Z|a-z]{2,}\b'  
            regex3 = r'\b[A-Za-z0-9._%+-]+@esp+\.[A-Z|a-z]{2,}\b'  
            if(re.search(regex,request.form['email']) or re.search(regex2,request.form['email']) or re.search(regex3,request.form['email'])):   
                session['user'] = request.form['user']
                session['email'] = request.form['email']
                return render_template('accueil.html') 
            else:
                return render_template('index.html',errormessage="yes")
        else:
            return render_template('index.html',errormessage="yes")
    return render_template('index.html')

@app.route('/accueil')
def accueil():
    if ('user' in session) and ('email' in session):
        if g.user and g.email:
            return render_template('accueil.html') 
    return render_template('index.html')   


@app.before_request
def before_request():
    g.user=None
    g.email=None

    if ('user' in session) and ('email' in session):
        g.user = session['user']
        g.email = session['email']
        global emailglobal 
        emailglobal = g.email

@app.route('/dropsession')
def dropsession():
    session.pop('user', None)
    session.pop('email',None)
    return render_template('index.html')  
 

@app.route('/charts', methods=['GET', 'POST'])
def charts():
        if ('user' in session) and ('email' in session):
            return render_template('charts.html')
        else:
            return render_template('index.html') 





####################################################Simulateur de l'appareil LevelSender####################################################
now = datetime.now()
timestamp = datetime.timestamp(now)
print("timestamp =", timestamp)


@app.route('/data', methods=["GET", "POST"])
def data():
    print("Get timestamp =", timestamp)
    Z =  datetime.timestamp(datetime.now())
    print("timestamp =", Z)
    with open("info.csv","a+") as f:
        if(Z > timestamp + 30):
            x =  randint(10,200)  #700~1500
            y =  randint(-20,80)  #10~100
        else:
            x =  randint(7,90)  #700~1500
            y =  randint(-10,20)  #10~100

        f.write("\n"+str(x)+","+str(y))
        f.close()

    with open("info.csv","r+") as f:
        reader = csv.reader(f)
        next(reader)
        data = []
        for row in reader:
            data.append({
                "humidite": row[0],
                "Temperature": row[1]
            })

    with open("info.json","w+") as f:
        json.dump(data,f,indent=4)

    with open("info.json") as f:
        donnee = json.load(f)

# @app.route('/mapbi', methods=["GET", "POST"])
# def mapbi():
#     return render_template('mapwithmaps.html') 


    # Data Format
    # [TIME, Debit, NiveauEau]
    max = len(donnee)
    i = randint(0,max)
    humidite = int(donnee[max-1]["humidite"])
    Temperature = int(donnee[max-1]["Temperature"])


###########################   Alerte par mail   #####################
    if(Temperature == 28 or humidite == 75 or Temperature ==66):
        app.config['MAIL_SERVER'] = 'smtp.gmail.com'
        app.config['MAIL_PORT'] = 465
        app.config['MAIL_USERNAME'] = 'bab.y.s.sarr@gmail.com'
        app.config['MAIL_PASSWORD'] = 'Bebelaye123'
        app.config['MAIL_USE_SSL'] = True
        mail = Mail(app)
        if request.method == "GET":
            msg = Message("Alerte!", sender="bab.y.s.sarr@gmail.com", recipients=[emailglobal])
            if(Temperature == 28):
                msg.body = "Attention, les plantes doivent etre arrosés"
                mail.send(msg)
            elif(humidite == 75):
                msg.body = "Attention, milieu beaucoup trop humide pour vos plantes "
                mail.send(msg)
        else:
            print("Probleme Alerte NNN")
########################################################################



    data = [time() * 1000, humidite, Temperature]

    response = make_response(json.dumps(data))

    response.content_type = 'application/json'

    return response



@app.route('/markersdata', methods=['GET', 'POST'])
def testfn():
    # GET request
    if request.method == 'GET':
        with open("markersdata.json") as f:
            donnee = json.load(f)
        return jsonify(donnee)  # serialize and use JSON headers
    # POST request
    if request.method == 'POST':
        print(request.get_json())  # parse as JSON
        return 'Sucesss', 200















################ CRUD#####################################################################################################""""



### ACCUEIL CRUD and VIEW ###
@app.route('/crud')
def crud():
    if ('user' in session) and ('email' in session):
        if g.user and g.email:
            con = sqlite3.connect("markersdata.db")  
            con.row_factory = sqlite3.Row  
            cur = con.cursor()  
            cur.execute("select * from markersdata order by id DESC limit 100")  
            rows = cur.fetchall()
            cur.execute("select count(*) from markersdata")
            n=cur.fetchone()[0] 
            return render_template("crud.html",rows = rows, n=n) 
    return render_template('index.html')


############################################INSERT BY RANDOM###########################################
###CREATE###
@app.route("/insertbyrandom",methods = ["POST","GET"])  
def insertbyrandom():  
    if request.method == "POST": 
        n = int(request.form["number"])
        def waytocreate():
            try:  
                r_lat = numpy.random.uniform(12.5,15.9,1)#randint(12,16)+(randint(10,50)*0.0005)
                lat = r_lat[0]
                r_lng = numpy.random.uniform(13.5,16.0,1)#randint(12,16)+(randint(10,50)*0.0005)
                lng = (r_lng[0])*(-1)  
                zone = "zoneN°"+str(randint(1,11000))
                content = "{} |Latitude: {} |Longitude: {}".format(zone,lat,lng)
                with sqlite3.connect("markersdata.db") as con:  
                    cur = con.cursor()  
                    cur.execute("INSERT into markersdata (content, lat, lng) values (?,?,?)",(content,lat,lng))  
                    con.commit()  
            except:  
                con.rollback()  
            finally:  
                con.close() 
                return  redirect("/crud")  
                

        for i in range(0,int(n)):
            waytocreate()
    return redirect("/crud")
#############################################################################################################




##############################################################insert################################################""
@app.route("/insert",methods = ["POST","GET"])  
def insert():  
    if request.method == "POST":
        try:
            content = request.form["content"]
            lat = request.form["lat"]
            lng = request.form["lng"]
            with sqlite3.connect("markersdata.db") as con: 
                con.row_factory = sqlite3.Row 
                cur = con.cursor()      
                cur.execute("select * from markersdata WHERE lat=? and lng=?",(lat,lng))  
                rowsinsert = cur.fetchall()
                verif = False 
                for row in rowsinsert:
                    veriflat = row["lat"]
                    veriflng = row["lng"]
                    if(lat==veriflat and lng == veriflng):
                        verif = True
                if(verif): 
                    return redirect(url_for('crud',text="insert_no"))
                else:
                    cur = con.cursor()  
                    cur.execute("INSERT into markersdata (content, lat, lng) values (?,?,?)",(content,lat,lng))
                    con.commit()  
                    return redirect(url_for('crud',text="insert_ok"))
        except:
            con.rollback()  
        finally:  
            con.close() 
    return redirect(url_for('crud',text="insert_no"))
##########################################################################################################################""




#########################################################"DELETE#########################################
###DELETE###
@app.route("/delpoint",methods = ["POST"])  
def deleterecord():  
    id = int(request.form["id"])  
    with sqlite3.connect("markersdata.db") as con: 
        con.row_factory = sqlite3.Row 
        cur = con.cursor()      
        cur.execute("select id from markersdata WHERE id={}".format(id)) 
        rowsdelete = cur.fetchall()
        verif = False
        for row in rowsdelete:
            verifid = row["id"]
            if(int(verifid)==int(id)):
                verif = True
        if(verif):
            cur = con.cursor()  
            cur.execute('delete from markersdata where id='+str(id)+"")  
            con.commit()  
            return redirect(url_for('crud',text="del_ok")) 
        else:
            return redirect(url_for('crud',text="del_no"))
            
#######################################################################################################



################################################UPDATE##################################################
###UPDATE###
@app.route('/update', methods=['GET', 'POST'])
def update():
    if request.method == 'POST':
        with sqlite3.connect("markersdata.db") as con:  
            idbi = int(request.form['id'])  
            con.row_factory = sqlite3.Row  
            cur = con.cursor()  
            cur.execute("select id from markersdata WHERE id={}".format(idbi)) 
            rowsupdate = cur.fetchall()
            verif = False
            for row in rowsupdate:
                verifid = row["id"]
                if(int(verifid)==int(idbi)):
                    verif = True
            if(verif):
                cur = con.cursor()  
                contentbi = "{}".format(request.form['content'])
                latbi = "{}".format(request.form['lat'])
                lngbi ="{}".format(request.form['lng'])
                datas = (contentbi,latbi,lngbi,idbi) 
                cur.execute("UPDATE markersdata SET content=? ,lat=?,lng=? WHERE id=?",datas)
                con.commit()  
                return redirect(url_for('crud',text="up_ok")) 
            else:
                return redirect(url_for('crud',text="up_no"))
#######################################################################################################         










if __name__ == "__main__":
    app.run(debug=False, use_reloader=False)
