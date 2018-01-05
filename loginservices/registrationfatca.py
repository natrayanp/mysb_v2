from loginservices import app
from flask import redirect, request,make_response
from datetime import datetime
from flask import jsonify

from loginservices import dbfunc as db
from loginservices import jwtdecodenoverify as jwtnoverify
from flask import Flask, request, redirect, url_for
from werkzeug.utils import secure_filename

import psycopg2, psycopg2.extras
import jwt
import requests
import json
import os


      
@app.route('/registdetfetch',methods=['GET','POST','OPTIONS'])
def registdetfetch():
#This is called by setjws service
    if request.method=='OPTIONS':
        print("inside REGISTRATIONDETAILSFETCH options")
        return make_response(jsonify('inside REGISTRATIONDETAILSFETCH options'), 200)  

    elif request.method=='GET':
        print("inside REGISTRATIONDETAILSFETCH GET")
        
        print((request))        
        userid,entityid=jwtnoverify.validatetoken(request)
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        '''
        try:
            con
        except NameError:
            print("con not defined so assigning as null")
            conn_string = "host='localhost' dbname='postgres' user='postgres' password='password123'"
            con=psycopg2.connect(conn_string)
            cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
        else:            
            if con.closed:
                conn_string = "host='localhost' dbname='postgres' user='postgres' password='password123'"
                con=psycopg2.connect(conn_string)
                cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
        '''



        #need to think on a way to get entity id for this

        #Select registration details for the userid and entity id derived from JWT START

        con,cur=db.mydbopncon()

        print(con)
        print(cur)
        
        command = cur.mogrify("SELECT clientcode, clientholding, clienttaxstatus, clientoccupationcode,clientappname1,clientdob, clientgender , clientpan, clientnominee, clientnomineerelation, clientnomineedob, clientnomineeaddress, clienttype, clientacctype1, clientaccno1, clientmicrno1, clientifsccode1, defaultbankflag1, clientadd1, clientadd2, clientadd3, clientcity, clientstate, clientpincode, clientcountry, clientemail, clientcommmode, clientdivpaymode, cm_foradd1, cm_foradd2, cm_foradd3, cm_forcity, cm_forpincode , cm_forstate, cm_forcountry, cm_mobile FROM uccclientmaster WHERE ucclguserid = %s AND uccentityid = %s;",(userid,entityid,))
        print(command)
        cur, dbqerr = db.mydbfunc(con,cur,command)
        print(cur)
        print(dbqerr)
        print(type(dbqerr))
        print(dbqerr['natstatus'])
        if cur.closed == True:
            if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
                dbqerr['statusdetails']="loginuser Fetch failed"
            resp = make_response(jsonify(dbqerr), 400)
            return(resp)
        else:
            pass
    
        if (cur.rowcount) != 1:
            errorresp= {'natstatus':'error','statusdetails':'ZERO or MORE THAN ONE registration record for user'}
            resps = make_response(jsonify(errorresp), 400)
            print(resps)
            return(resps)
        else:
            rec = cur.fetchone()
            #createdetailfrm
            clientname = rec['clientappname1']
            clientpan = rec['clientpan']
            clientcode = rec['clientcode']
            clientgender = rec['clientgender']
            clientdob = rec['clientdob']
            clientemail = rec['clientemail']
            clientmobile = rec['cm_mobile']
            clientcommode = rec['clientcommmode']
            clientholding=rec['clientholding']
            #clientpepflg='' this is set in fatca

            #CLIENT TAX STATUS: 1-individual, 21-NRE, 24-NRO
            if rec['clienttaxstatus']==21:
                clientisnri = true
                clienttaxstatusres = False 
                clienttaxstatusnri = 'NRE'
            elif rec['clienttaxstatus']==24:
                clientisnri = true
                clienttaxstatusres = False 
                clienttaxstatusnri = 'NRO'
            else:
                clientisnri = False
                clienttaxstatusres = True 
                clienttaxstatusnri = ''

            clientocupation = rec['clientoccupationcode']

            if clientocupation in ['01','43']:
                clientocutyp = 'B'
            elif clientocupation in ['02','03','04','09','41','42','44']:
                clientocutyp = 'S'
            elif clientocupation in ['05','06','07','08','99']:
                clientocutyp = 'O'
            else:
                clientocutyp=''

            clientnomineename = rec['clientnominee']
            if clientnomineename:
                clienthasnominee = True
                clientnomineerel = rec['clientnomineerelation']
                clientnomineedob = rec['clientnomineedob']
                clientnomineeaddres = rec['clientnomineeaddress']
            else:
                clienthasnominee = False
                clientnomineerel = ''
                clientnomineedob = ''
                clientnomineeaddres = ''
            
            clientfndhldtype = rec['clienttype'] #Defaulted to PHYS
            #createclientaddfrm
            clientaddress1 =  rec['clientadd1']
            clientaddress2 =  rec['clientadd2']
            clientaddress3 =  rec['clientadd3']
            clientcity =  rec['clientcity']
            clientstate =  rec['clientstate']
            clientcountry =  rec['clientcountry']
            clientpincode =  rec['clientpincode']
            
            if clientisnri:
                clientforinadd1 =  rec['cm_foradd1']
                clientforinadd2 =  rec['cm_foradd2']
                clientforinadd3 =  rec['cm_foradd3']
                clientforcity =  rec['cm_forcity']
                clientforstate =  rec['cm_forstate']
                clientforcountry =  rec['cm_forcountry']
                clientforpin =  rec['cm_forpincode']
            else:
                clientforinadd1 =  ''
                clientforinadd2 =  ''
                clientforinadd3 =  ''
                clientforcity =  ''
                clientforstate = ''
                clientforcountry =  ''
                clientforpin =  ''

            #createclientbankfrm
            clientactype = rec['clientacctype1']
            clientacnumb = rec['clientaccno1']
            clientmicrno = rec['clientmicrno1']
            clientifsc = rec['clientifsccode1']


        command = cur.mogrify("SELECT pan_rp,inv_name,tax_status,po_bir_inc,co_bir_inc,tax_res1,tpin1,id1_type,tax_res2,tpin2,id2_type,tax_res3,tpin3,id3_type,tax_res4,tpin4,id4_type,srce_wealt,inc_slab,pep_flag,occ_code,occ_type FROM fatcamaster WHERE fatcalguserid = %s AND fatcaentityid = %s;",(userid,entityid,))
        print(command)
        cur, dbqerr = db.mydbfunc(con,cur,command)
        print(cur)
        print(dbqerr)
        print(type(dbqerr))
        print(dbqerr['natstatus'])
        if cur.closed == True:
            if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
                dbqerr['statusdetails']="loginuser Fetch failed"
            resp = make_response(jsonify(dbqerr), 400)
            return(resp)
        else:
            pass
        
        if (cur.rowcount) != 1:
            errorresp= {'natstatus':'error','statusdetails':'ZERO or MORE THAN ONE Fatca record for user'}
            resps = make_response(jsonify(errorresp), 400)
            print(resps)
            return(resps)
        else:
            rec = cur.fetchone()
            #createclientfatcafrm
            clientsrcwealth = rec['srce_wealt']
            clientincslb = rec['inc_slab']
            clienttaxrescntry1 = rec['tax_res1']
            clienttaxid1 = rec['tpin1']
            clienttaxidtype1 = rec['id1_type']
            clienttaxrescntry2 = rec['tax_res2']
            clienttaxid2 = rec['tpin2']
            clienttaxidtype2 = rec['id2_type']
            clienttaxrescntry3 = rec['tax_res3']
            clienttaxid3 = rec['tpin3']
            clienttaxidtype3 = rec['id3_type']
            clienttaxrescntry4 = rec['tax_res4']
            clienttaxid4 = rec['tpin4']
            clienttaxidtype4 = rec['id4_type']
            clientpepflg = rec['pep_flag']
        
    
        #Select registration details for the userid and entity id derived from JWT END
        
        return (json.dumps({'clientname':clientname,'clientpan':clientpan,'clientcode':clientcode,'clientgender':clientgender,'clientdob':clientdob,'clientemail':clientemail,'clientmobile':clientmobile,'clientcommode':clientcommode,'clientholding':clientholding,'clientpepflg':clientpepflg,'clientisnri':clientisnri,'clienttaxstatusres':clienttaxstatusres,'clienttaxstatusnri':clienttaxstatusnri,'clientocupation':clientocupation,'clientocutyp':clientocutyp,'clientnomineename':clientnomineename,'clienthasnominee':clienthasnominee,'clientnomineerel':clientnomineerel,'clientnomineedob':clientnomineedob,'clientnomineeaddres':clientnomineeaddres,'clientfndhldtype':clientfndhldtype,'clientaddress1':clientaddress1,'clientaddress2':clientaddress2,'clientaddress3':clientaddress3,'clientcity':clientcity,'clientstate':clientstate,'clientcountry':clientcountry,'clientpincode':clientpincode,'clientforinadd1':clientforinadd1,'clientforinadd2':clientforinadd2,'clientforinadd3':clientforinadd3,'clientforcity':clientforcity,'clientforstate':clientforstate,'clientforcountry':clientforcountry,'clientforpin':clientforpin,'clientactype':clientactype,'clientacnumb':clientacnumb,'clientmicrno':clientmicrno,'clientifsc':clientifsc,'clientsrcwealth':clientsrcwealth,'clientincslb':clientincslb,'clienttaxrescntry1':clienttaxrescntry1,'clienttaxid1':clienttaxid1,'clienttaxidtype1':clienttaxidtype1,'clienttaxrescntry2':clienttaxrescntry2,'clienttaxid2':clienttaxid2,'clienttaxidtype2':clienttaxidtype2,'clienttaxrescntry3':clienttaxrescntry3,'clienttaxid3':clienttaxid3,'clienttaxidtype3':clienttaxidtype3,'clienttaxrescntry4':clienttaxrescntry4,'clienttaxid4':clienttaxid4,'clienttaxidtype4':clienttaxidtype4,'clientpepflg':clientpepflg}))


@app.route('/uploadfile', methods=['GET', 'POST'])
def upload_file():
    print(request)
    if request.method == 'POST':
        # check if the post request has the file part
        if 'upload' not in request.files:
            print('No file part')
            return 'failed'
        file = request.files['upload']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            print('No selected file')
            return 'no file selected'
        if file:
            filename = secure_filename(file.filename)
            print(type(file))
            filecontenttype = file.content_type
            print('filename : ', filename)            
            print("filecontenttype :",filecontenttype)     
            
            file.save(os.path.join('/home/natrayan/Downloads/', filename))
            return make_response(jsonify('filesaved'), 200)    
    else:
        print("inside else")
        return make_response(jsonify('ok'), 200)  



@app.route('/dtlfrmsave',methods=['GET','POST','OPTIONS'])
def dtlfrmsave():
#This is called when save for later button is clicked
    if request.method=='OPTIONS':
        print("inside DETAIL FORM SAVE options")
        return make_response(jsonify('inside DETAIL FORM SAVE options'), 200)  

    elif request.method=='POST':
        print("inside DETAIL FORM SAVE post")
        
        print((request))        
        userid,entityid=jwtnoverify.validatetoken(request)
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        data = request.get_json()
        print(data)

        return make_response(jsonify('ok'), 200) 

