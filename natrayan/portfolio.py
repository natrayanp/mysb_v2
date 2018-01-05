from natrayan import app
#from .hello_world import app
from flask import request, make_response, jsonify, Response, redirect
from datetime import datetime

import psycopg2
import json
import jwt


@app.route('/pfdatafetch',methods=['GET','POST','OPTIONS'])
def pfdatafetchh():
    records=[]
    
    if 'Authorization' in request.headers:
        natjwtfrhead=request.headers.get('Authorization')
        if natjwtfrhead.startswith("Bearer "):
            natjwtfrheadf =  natjwtfrhead[8:-1]
        natjwtdecoded = jwt.decode(natjwtfrheadf, verify=False)
        userid=natjwtdecoded['userid']
        if  (not userid) or (userid ==""):
            dbqerr['natstatus'] == "error"
            dbqerr['statusdetails']="No user id in request"
            resp = make_response(jsonify(dbqerr), 400)
            return(resp)
        conn_string = "host='localhost' dbname='postgres' user='postgres' password='password123'"
        con=psycopg2.connect(conn_string)
        cur = con.cursor()
        #cur.execute("select row_to_json(art) from (select a.*, (select json_agg(b) from (select * from pfstklist where pfportfolioid = a.pfportfolioid ) as b) as pfstklist, (select json_agg(c) from (select * from pfmflist where pfportfolioid = a.pfportfolioid ) as c) as pfmflist from pfmaindetail as a where pfuserid =%s ) art",(userid,))
        command = cur.mogrify("select row_to_json(art) from (select a.*, (select json_agg(b) from (select * from pfstklist where pfportfolioid = a.pfportfolioid ) as b) as pfstklist, (select json_agg(c) from (select * from pfmflist where pfportfolioid = a.pfportfolioid ) as c) as pfmflist from pfmaindetail as a where pfuserid =%s ) art",(userid,))
        cur, dbqerr = mydbfunc(con,cur,command)
        print(cur)
        print(dbqerr)
        print(type(dbqerr))
        print(dbqerr['natstatus'])

        if cur.closed == True:
            if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
                dbqerr['statusdetails']="pf Fetch failed"
            resp = make_response(jsonify(dbqerr), 400)
            return(resp)

    
        #Model to follow in all fetch
        for record in cur:  
            records.append(record[0])        
        print("portfolio details returned for user: "+userid)
    
    return json.dumps(records)


@app.route('/pfdatasave',methods=['GET','POST','OPTIONS'])
#example for model code http://www.postgresqltutorial.com/postgresql-python/transaction/
def pfdatasavee():
    
    if request.method=='OPTIONS':
        print ("inside options")
        return jsonify({'body':'success'})

    elif request.method=='POST':   
        print ("inside pfdatasave")

        print(request.headers)
        payload= request.get_json()
        #payload = request.stream.read().decode('utf8')    
        
        pfdata = payload
        if 'Authorization' in request.headers:
            natjwtfrhead=request.headers.get('Authorization')
            if natjwtfrhead.startswith("Bearer "):
                natjwtfrheadf =  natjwtfrhead[8:-1]
            natjwtdecoded = jwt.decode(natjwtfrheadf, verify=False)
            pfdata['pfuserid']=natjwtdecoded['userid']
        else:
            return jsonify({'natstatus':'error','statusdetails':'Not logged in (authkey missing)'})

        print("pfdata before removing")
        print(pfdata)
        savetype = ""
        if 'pfportfolioid' in pfdata:
            if pfdata.get('pfportfolioid') == "New":
                savetype = "New"
            else:
                savetype = "Old"
        else:
            #if 'pfportfolioid' itself not in the data it is error we shouuld exit
            print('pfportfolioid is not in the messages')
            return jsonify({'natstatus':'error','statusdetails':'Data error (Portfolio id missing)'})

        if 'pfstklist' in pfdata:
            pfstlsdata = pfdata.pop("pfstklist")            
            print("pfstlsdata")
        else:
            pfstlsdata=None
            print("key pfstklist not in the submitted record")
            #return jsonify({'natstatus':'error','statusdetails':'Data error (stocklist missing)'})
        
        if 'pfmflist' in pfdata:
            pfmflsdata = pfdata.pop("pfmflist")
            print("pfmflist")
            print(pfmflsdata)
        else:
            pfmflsdata=None
            print("key pfmflist not in the submitted record")
            #return jsonify({'natstatus':'error','statusdetails':'Data error (mflist missing)'})

        print("after removing")
        print("pfdata")
        print(pfdata)

        ### Prepre DB connection START ###
        conn_string = "host='localhost' dbname='postgres' user='postgres' password='password123'"
        con=psycopg2.connect(conn_string)
        cur = con.cursor()
        ### Prepre DB connection END ###

        savetimestamp = datetime.now()
        pfsavedate=savetimestamp.strftime('%Y%m%d') 
        pfsavetimestamp=savetimestamp.strftime('%Y/%m/%d %H:%M:%S')
        useridstr=pfdata.get('pfuserid')

        if savetype == "New": 
            pfdata['pfoctime']= pfsavetimestamp
            pfdata['pflmtime']= pfsavetimestamp
            print('MAX query')
            command = cur.mogrify("SELECT MAX(pfpfidusrrunno) FROM pfmaindetail where pfuserid = %s",(useridstr,))
            cur, dbqerr = mydbfunc(con,cur,command)
            print(cur)
            print(dbqerr)
            print(type(dbqerr))
            print(dbqerr['natstatus'])

            if cur.closed == True:
                if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
                    dbqerr['statusdetails']="Max Number identification Failed"
                resp = make_response(jsonify(dbqerr), 400)
                return(resp)
            
            for record in cur:
                print(record)

            if record[0]== None:
                pfmainnextmaxval = 1
            else:
                pfmainnextmaxval = record[0] +1

            pfdata['pfpfidusrrunno']=pfmainnextmaxval
            pfdata['pfportfolioid']=useridstr+str(pfmainnextmaxval)
            
            if pfdata.get('pfbeneusers') == None:
                pfdata['pfbeneusers']=useridstr

            pfdatajsondict = json.dumps(pfdata)

            command = cur.mogrify("INSERT INTO pfmaindetail select * from json_populate_record(NULL::pfmaindetail,%s);",(str(pfdatajsondict),))

            cur, dbqerr = mydbfunc(con,cur,command)
            if cur.closed == True:
                if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
                    dbqerr['statusdetails']="main insert  Failed"
                resp = make_response(jsonify(dbqerr), 400)
                return(resp)
    
            pfstlsseqnum=1
            if pfstlsdata!=None:
                for d in pfstlsdata:                
                    d['pfstoctime']= pfsavetimestamp
                    d['pfstlmtime']= pfsavetimestamp
                    d['pfstklistid']='st'+pfdata.get('pfportfolioid')+str(pfstlsseqnum)                
                    d['pfportfolioid']=pfdata.get('pfportfolioid')
                    pfstlsseqnum=pfstlsseqnum+1
                    pfstlsdatajsondict = json.dumps(d)
                    command = cur.mogrify("INSERT INTO pfstklist select * from json_populate_record(NULL::pfstklist,%s);",(str(pfstlsdatajsondict),))
                    print(command)

                    cur, dbqerr = mydbfunc(con,cur,command)
                    if cur.closed == True:
                        if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
                            dbqerr['statusdetails']="stocklist insert  Failed"
                        resp = make_response(jsonify(dbqerr), 400)
                        return(resp)
            else:
                print("done nothing as pfstlsdata is none")

            pfmflsseqnum=1
            if pfmflsdata!=None:
                for d in pfmflsdata:                    
                    d['pfmfoctime']= pfsavetimestamp
                    d['pfmflmtime']= pfsavetimestamp
                    d['pfmflistid']='mf'+pfdata.get('pfportfolioid')+str(pfmflsseqnum)
                    d['pfportfolioid']=pfdata.get('pfportfolioid')
                    pfmflsseqnum=pfmflsseqnum+1
                    pfmflsdatajsondict = json.dumps(d)
                    command = cur.mogrify("INSERT INTO pfmflist select * from json_populate_record(NULL::pfmflist,%s);",(str(pfmflsdatajsondict),))
                    
                    cur, dbqerr = mydbfunc(con,cur,command)
                    if cur.closed == True:
                        if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
                            dbqerr['statusdetails']="mflist insert Failed"
                        resp = make_response(jsonify(dbqerr), 400)
                        return(resp)   
            else:
                print("done nothing as pfmflsdata is none")

            con.commit()    
            cur.close()
            con.close()
            return jsonify({'natstatus':'success','statusdetails':'New portfolio ' + pfdata.get('pfportfolioname') +' created'})

            
            '''
            [{'pfmfnav': '75', 'pfmfpercent': '70', 'pfmfamt': 0, 'pfmffundname': 'MNC', 'pfmfallotedamt': 4121.599999999999}, {'pfmfnav': '66', 'pfmfpercent': '10', 'pfmfamt': 0, 'pfmffundname': 'OII', 'pfmfallotedamt': 588.8000000000001}]

            [{'pfstexchange': 'NSE', 'pfstallotedamt': 588.8000000000001, 'pfstpercent': '10', 'pfstTotUnit': '0', 'pfsttradingsymbl': 'ITC', 'pfstamt': 0, 'pfsttotunit': 0, 'pfstltp': '788'}, {'pfstexchange': 'NSE', 'pfstallotedamt': 588.8000000000001, 'pfstpercent': '10', 'pfstTotUnit': '6', 'pfsttradingsymbl': 'SBIN', 'pfstamt': 0, 'pfsttotunit': 0, 'pfstltp': '89'}]

            {'pfstkamtsplittype': '%', 'pftargetintrate': None, 'pfportfolioname': 'ASDFASDF', 'pfmfamtsplittype': '%', 'pfsummed': 5888, 'pfpurpose': 'ASDFASDF', 'pftargetdt': None, 'pfplannedinvamt': 5888, 'pfstartdt': None, 'pfportfolioid': 'New', 'pfbeneUsers': None, 'pfuserid': None, 'pfinvamtfeq': None}
            '''
        elif savetype == "Old" :
            pfdata['pflmtime']= pfsavetimestamp
            pfdata.get('pfuserid')            
 
            #To update these fields
            # pfportfolioname,pfpurpose,pfbeneusers,pfstartdt,pftargetdt,pftargetintrate,pfplannedinvamt,pfinvamtfeq,pfstkamtsplittype,pfmfamtsplittype,pflmtime

            command = cur.mogrify("SELECT distinct(pfportfolioname) FROM pfmaindetail where pfuserid = %s",(useridstr,))
            cur, dbqerr = mydbfunc(con,cur,command)

            if cur.closed == True:
                if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
                    dbqerr['statusdetails']="Portfolioname fetch Failed"
                resp = make_response(jsonify(dbqerr), 400)
                return(resp)
            

            #Check if the pf name already exits START
            if cur.rowcount == 0:
                dbqerr['statusdetails']="No Portfolioname exists"
                resp = make_response(jsonify(dbqerr), 400)
                return(resp)
            else:
                print("inside else")
                for record in cur:
                    if (pfdata.get('pfportfolioid')==record[0]):
                        dbqerr['statusdetails']="Portfolioname already exists"
                        resp = make_response(jsonify(dbqerr), 400)
                        return(resp)   
            #Check if the pf name already exits START

            #PF details update START

            pfdatajsondict = json.dumps(pfdata)
            command = cur.mogrify("""
                                  update pfmaindetail set(pfportfolioname,pfpurpose,pfbeneusers,pfstartdt,pftargetdt,pftargetintrate,pfplannedinvamt,pfinvamtfeq,pfstkamtsplittype,pfmfamtsplittype,pflmtime) = 
                                  (select pfportfolioname,pfpurpose,pfbeneusers,pfstartdt,pftargetdt,pftargetintrate,pfplannedinvamt,pfinvamtfeq,pfstkamtsplittype,pfmfamtsplittype,pflmtime from json_to_record (%s)
                                  AS (pfportfolioname varchar(50),pfpurpose varchar(600),pfbeneusers varchar(40),pfstartdt date,pftargetdt date,pftargetintrate numeric(5,2),pfplannedinvamt numeric(16,5),pfinvamtfeq varchar(15),pfstkamtsplittype varchar(10),pfmfamtsplittype varchar(10),pflmtime timestamp))
                                  where pfportfolioid = %s and pfuserid = %s;
                                  """,(str(pfdatajsondict),pfdata.get('pfportfolioid'),useridstr,))
            
            cur, dbqerr = mydbfunc(con,cur,command)

            if cur.closed == True:
                if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
                    dbqerr['statusdetails']="main update  Failed"
                resp = make_response(jsonify(dbqerr), 400)
                return(resp)

            #PF details update END

            ###PF stock details update START###

            #Remove all the existing records START
            command = cur.mogrify("DELETE FROM pfstklist WHERE pfportfolioid = %s;",(pfdata.get('pfportfolioid'),))
            print(command)
            cur, dbqerr = mydbfunc(con,cur,command)
            if cur.closed == True:
                if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
                    dbqerr['statusdetails']="stocklist deletion  Failed"
                resp = make_response(jsonify(dbqerr), 400)
                return(resp)
            #Remove all the existing records END

            #Insertion of stocklist records START
            pfstlsseqnum=1
            if pfstlsdata!=None:
                for d in pfstlsdata:                
                    print("pfstlsdata else inside for")
                    print(d)
                    d['pfstoctime']= pfsavetimestamp
                    d['pfstlmtime']= pfsavetimestamp
                    d['pfstklistid']='st'+pfdata.get('pfportfolioid')+str(pfstlsseqnum)
                    d['pfportfolioid']=pfdata.get('pfportfolioid')
                    pfstlsseqnum=pfstlsseqnum+1
                    pfstlsdatajsondict = json.dumps(d)
                    command = cur.mogrify("INSERT INTO pfstklist select * from json_populate_record(NULL::pfstklist,%s);",(str(pfstlsdatajsondict),))
                    print(command)
                    cur, dbqerr = mydbfunc(con,cur,command)
                    if cur.closed == True:
                        if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
                            dbqerr['statusdetails']="stocklist insert  Failed"
                        resp = make_response(jsonify(dbqerr), 400)
                        return(resp)
            else:
                print("done nothing as pfstlsdata is none")
            #Insertion of stocklist records END
            ###PF stock details update END###

            ###PF MF details update START###

            #Remove all the existing MF list records START
            command = cur.mogrify("DELETE FROM pfmflist WHERE pfportfolioid = %s;",(pfdata.get('pfportfolioid'),))
            cur, dbqerr = mydbfunc(con,cur,command)
            if cur.closed == True:
                if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
                    dbqerr['statusdetails']="mflist deletion  Failed"
                resp = make_response(jsonify(dbqerr), 400)
                return(resp)
            #Remove all the existing MF list records END
            pfmflsseqnum=1
            if pfmflsdata!=None:
                for d in pfmflsdata:                
                    print("pfmflsdata inside for")
                    print(d)
                    d['pfmfoctime']= pfsavetimestamp
                    d['pfmflmtime']= pfsavetimestamp
                    d['pfmflistid']='mf'+pfdata.get('pfportfolioid')+str(pfmflsseqnum)
                    d['pfportfolioid']=pfdata.get('pfportfolioid')
                    pfmflsseqnum=pfmflsseqnum+1
                    pfmflsdatajsondict = json.dumps(d)
                    command = cur.mogrify("INSERT INTO pfmflist select * from json_populate_record(NULL::pfmflist,%s);",(str(pfmflsdatajsondict),))
                    print(command)                
                    cur, dbqerr = mydbfunc(con,cur,command)
                    if cur.closed == True:
                        if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
                            dbqerr['statusdetails']="mflist insert Failed"
                        resp = make_response(jsonify(dbqerr), 400)
                        return(resp)
            else:
                print("done nothing as pfmflsdata is none") 
            ###PF MF details update END###
            con.commit()    
            cur.close()
            con.close()
            return jsonify({'natstatus':'success','statusdetails':'Portfolio ' + pfdata.get('pfportfolioname') +' Updated'})


@app.route('/onlypf',methods=['GET','POST','OPTIONS'])
def onlypff():
    records=[]
    
    if 'Authorization' in request.headers:
        natjwtfrhead=request.headers.get('Authorization')
        if natjwtfrhead.startswith("Bearer "):
            natjwtfrheadf =  natjwtfrhead[8:-1]
        natjwtdecoded = jwt.decode(natjwtfrheadf, verify=False)
        userid=natjwtdecoded['userid']
        if  (not userid) or (userid ==""):
            dbqerr['natstatus'] == "error"
            dbqerr['statusdetails']="No user id in request"
            resp = make_response(jsonify(dbqerr), 400)
            return(resp)
        conn_string = "host='localhost' dbname='postgres' user='postgres' password='password123'"
        con=psycopg2.connect(conn_string)
        cur = con.cursor()
        #cur.execute("select row_to_json(art) from (select a.*, (select json_agg(b) from (select * from pfstklist where pfportfolioid = a.pfportfolioid ) as b) as pfstklist, (select json_agg(c) from (select * from pfmflist where pfportfolioid = a.pfportfolioid ) as c) as pfmflist from pfmaindetail as a where pfuserid =%s ) art",(userid,))
        command = cur.mogrify("select pfportfolioname from pfmaindetail;")
        cur, dbqerr = mydbfunc(con,cur,command)
        print(cur)
        print(dbqerr)
        print(type(dbqerr))
        print(dbqerr['natstatus'])

        if cur.closed == True:
            if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
                dbqerr['statusdetails']="pf Fetch failed"
            resp = make_response(jsonify(dbqerr), 400)
            return(resp)

    
        #Model to follow in all fetch
        for record in cur:  
            records.append(record[0])        
        print("portfolio name only returned for user: "+userid)
    
    return json.dumps(records)



def mydbfunc(con,cur,command):
    try:
        cur.execute(command)            
        myerror={'natstatus':'success','statusdetails':''}
    except psycopg2.Error as e:
        print(e)
        myerror= {'natstatus':'error','statusdetails':''}
    except psycopg2.Warning as e:
        print(e)
        myerror={'natstatus':'warning','statusdetails':''}
        #myerror = {'natstatus':'warning','statusdetails':e}
    finally:
        if myerror['natstatus'] != "success":    
            con.rollback()
            cur.close()
            con.close()
            
    return cur,myerror   
