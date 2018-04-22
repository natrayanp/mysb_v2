from pf import app
from pf import dbfunc as db
from pf import jwtdecodenoverify as jwtnoverify
#from order import dbfunc as db
#from order import jwtdecodenoverify as jwtnoverify


#from order import app
from flask import request, make_response, jsonify, Response, redirect
from datetime import datetime
from order import dbfunc as db
from order import jwtdecodenoverify as jwtnoverify
from dateutil import tz
from datetime import datetime
from datetime import date
from multiprocessing import Process

import psycopg2
import json
import jwt
import time

@app.route('/mforderdatafetch',methods=['GET','OPTIONS'])
def mforderdatafetch():
#This is called by fund data fetch service
    if request.method=='OPTIONS':
        print("inside pforderdatafetch options")
        return make_response(jsonify('inside FUNDDATAFETCH options'), 200)  

    elif request.method=='GET':
        print("inside pforderdatafetch GET")
        print((request))        
        print(request.headers)
        userid,entityid=jwtnoverify.validatetoken(request)
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        print(userid,entityid)
        print('after')
        
        con,cur=db.mydbopncon()
        
        print(con)
        print(cur)
        
        #cur.execute("select row_to_json(art) from (select a.*, (select json_agg(b) from (select * from pfstklist where pfportfolioid = a.pfportfolioid ) as b) as pfstklist, (select json_agg(c) from (select * from pfmflist where pfportfolioid = a.pfportfolioid ) as c) as pfmflist from pfmaindetail as a where pfuserid =%s ) art",(userid,))
        #command = cur.mogrify("select row_to_json(art) from (select a.*,(select json_agg(b) from (select * from webapp.pfstklist where pfportfolioid = a.pfportfolioid ) as b) as pfstklist, (select json_agg(c) from (select c.*,(select json_agg(d) from (select * from webapp.pfmforlist where orormflistid = c.ormflistid AND ormffndstatus='INCART' AND entityid=%s) as d) as ormffundorderlists from webapp.pfmflist c where orportfolioid = a.pfportfolioid ) as c) as pfmflist from webapp.pfmaindetail as a where pfuserid =%s AND entityid=%s) art",(entityid,userid,entityid,))
        command = cur.mogrify(
            """
        	WITH portport as (select ororportfolioid,orormflistid,orormfpflistid from webapp.pfmforlist where ormffndstatus = 'INCART' AND ororpfuserid = %s AND entityid = %s) 
            select row_to_json(art) from (
            select a.*,
            (select json_agg(b) from (select * from webapp.pfstklist where pfportfolioid = a.pfportfolioid ) as b) as pfstklist, 
            (select json_agg(c) from (select c.*,(select json_agg(d) from (select * from webapp.pfmforlist where orormflistid in (SELECT distinct orormflistid FROM PORTPORT) AND ororportfolioid =a.pfportfolioid AND orormflistid=c.ormflistid AND ormffndstatus = 'INCART' AND entityid = %s ORDER BY ormffundordelstrtyp) as d) as ormffundorderlists 
            from webapp.pfmflist c where ormflistid in (SELECT distinct orormflistid FROM portport) AND  entityid = %s AND orportfolioid =a .pfportfolioid ) as c) as pfmflist 
	        from webapp.pfmaindetail as a where pfuserid = %s AND entityid = %s AND pfportfolioid IN (SELECT distinct ororportfolioid FROM portport) ORDER BY pfportfolioid  ) art
            """,(userid,entityid,entityid,entityid,userid,entityid,))

        cur, dbqerr = db.mydbfunc(con,cur,command)
        print("#########################################3")
        print(command)
        print("#########################################3")
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
        records=[]
        for record in cur:  
            records.append(record[0])           



        print("portfolio details returned for user: "+userid)
        
        
        resp = json.dumps(records)
    
    return resp



@app.route('/mfordersave',methods=['GET','POST','OPTIONS'])
#example for model code http://www.postgresqltutorial.com/postgresql-python/transaction/
def mfordersave():
    
    if request.method=='OPTIONS':
        print ("inside mfordersave options")
        return jsonify({'body':'success'})

    elif request.method=='POST':   
        print ("inside mfordersave post")

        print(request.headers)
        payload= request.get_json()
        #payload = request.stream.read().decode('utf8')    
        
        pfdatas = payload
        print(pfdatas)
        
        userid,entityid=jwtnoverify.validatetoken(request)
        con,cur=db.mydbopncon()

        command = cur.mogrify("BEGIN;")
        cur, dbqerr = db.mydbfunc(con,cur,command)
        if cur.closed == True:
            if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
                dbqerr['statusdetails']="DB query failed, BEING failed"
            resp = make_response(jsonify(dbqerr), 400)
            return(resp)

        savetimestamp = datetime.now()
        pfsavedate=savetimestamp.strftime('%Y%m%d') 
        pfsavetimestamp=savetimestamp.strftime('%Y/%m/%d %H:%M:%S')


        for pfdata in pfdatas:
            pfmflsdatalist=[]
            pfmforlsdatalist=[]
            print("pfdata before removing")
            print(pfdata)
            savetype = ""
            if 'pfportfolioid' in pfdata:
                if pfdata.get('pfportfolioid') == "NEW":
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

            if'pfscreen' in pfdata:
                screenid= pfdata.get('pfscreen')
                if screenid == "pfs":
                    filterstr="NEW"
                elif screenid == "ord":
                    filterstr="INCART"
            else:
                screenid=None
                print("key screenid not in the submitted record")       


            print("after removing")
            print("pfdata")
            print(pfdata)
            
            print("pfsavetimestamp1")
            print("pfsavetimestamp1")
            #useridstr=pfdata.get('pfuserid')
            useridstr=userid
            pfdata['pfuserid']=userid

            if savetype == "New": 
                #No New portfolio should come here
                pass
            elif savetype == "Old" :
                print('inside old')
                pfdata['pflmtime']= pfsavetimestamp
                pfdata.get('pfuserid')            

                #If request is from pfscreen then we update pf details, if it is from order screen skip this.
                
                ###PF stock details update START###
                    #NO STOCK DETAILS FOR THIS FUNCTION TO HANDLE
                ###PF stock details update END###

                ###PF MF details update START###

                if pfmflsdata!=None:
                    for d in pfmflsdata:  
                        print("pfmflsdata inside for")
                        print(d)
                        d['ormfoctime']= pfsavetimestamp
                        d['ormflmtime']= pfsavetimestamp

                        if(d['ormflistid']==""):
                            #New fund getting added to the PF
                            command = cur.mogrify("SELECT MAX(ormfseqnum) FROM webapp.pfmflist where orportfolioid = %s and entityid =%s;",(pfdata.get('pfportfolioid'),entityid,))
                            print(command)
                            cur, dbqerr = db.mydbfunc(con,cur,command)
                                                
                            if cur.closed == True:
                                if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
                                    dbqerr['statusdetails']="Fund MAX sequence failed"
                                resp = make_response(jsonify(dbqerr), 400)
                                return(resp)

                            #Model to follow in all fetch
                            records=[]
                            for record in cur:  
                                records.append(record[0])
                            print("iam printing records to see")
                            print(records)
                            
                            if(records[0] == None):
                                pfmflsseqnum=1
                            else:
                                if(type(records[0])=="Decimal"):
                                    pfmflsseqnum = int(Decimal(records[0]))+1                                
                                else:
                                    pfmflsseqnum=records[0]+1

                            d['ormflistid']='mf'+pfdata.get('pfportfolioid')+str(pfmflsseqnum)
                            d['orportfolioid']=pfdata.get('pfportfolioid')
                            d['entityid']=entityid
                            d['ormfseqnum'] = str(pfmflsseqnum)
                            d['orpfuserid']=pfdata.get('pfuserid')
                            pfmflsdatalist.append(d['ormflistid'])
                            

                            if 'ormffundorderlists' in d:
                                pfmflsordata = d.pop("ormffundorderlists")
                                print("ormffundorderlists old")
                                print(pfmflsordata)
                            else:
                                pfmflsordata=None
                                print("key ormffundorderlists not in the submitted record")

                            pfmflsdatajsondict = json.dumps(d)
                            command = cur.mogrify("INSERT INTO webapp.pfmflist select * from json_populate_record(NULL::webapp.pfmflist,%s) where entityid = %s;",(str(pfmflsdatajsondict),entityid,))
                            print(command)                
                            cur, dbqerr = db.mydbfunc(con,cur,command)
                            if cur.closed == True:
                                if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
                                    dbqerr['statusdetails']="mflist insert Failed"
                                resp = make_response(jsonify(dbqerr), 400)
                                return(resp)

                            pfmforlsseqnum=1
                            if pfmflsordata != None:
                                for e in pfmflsordata: 
                                    print("PRINTING e")
                                    print(e)                                           
                                    e['ormfoctime']= pfsavetimestamp
                                    e['ormflmtime']= pfsavetimestamp
                                    e['entityid']=entityid
                                    #e['orormfpflistid']= "or"+d.get('ormflistid')+str(pfmforlsseqnum)
                                    e['ororportfolioid']=d.get('orportfolioid')
                                    e['ororpfuserid']=d.get('orpfuserid')
                                    e['orormffundname']=d.get('ormffundname')
                                    e['orormffndcode']=d.get('ormffndcode')
                                    e['orormflistid']= d.get('ormflistid') 
                                    
                                    if(e.get('ormffundordelsstdt')==0):
                                        if (e['ormffundordelstrtyp']=='One Time'):
                                            print("inside if")
                                        else:
                                            dbqerr={}
                                            if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
                                                dbqerr['statusdetails']="SIP START DATE is Mandatory"
                                            resp = make_response(jsonify(dbqerr), 400)
                                            return(resp)
                                        
                                    
                                    #For new SIP or onetime record for the fund
                                    if(e['orormfpflistid'] ==""):
                                        e['orormfpflistid']= "or"+d.get('ormflistid')+str(pfmforlsseqnum)                                                                 
                                        e['orormfseqnum'] = pfmforlsseqnum
                                        pfmforlsdatalist.append(e['orormfpflistid'])
                                        pfmforlsseqnum = pfmforlsseqnum+1
                                        pfmflsordatajsondict = json.dumps(e)

                                        command = cur.mogrify("INSERT INTO webapp.pfmforlist select * from json_populate_record(NULL::webapp.pfmforlist,%s) where entityid = %s;",(str(pfmflsordatajsondict),entityid,))
                                        print(command)
                                        cur, dbqerr = db.mydbfunc(con,cur,command)
                                        if cur.closed == True:
                                            if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
                                                dbqerr['statusdetails']="mflist details insert Failed"
                                            resp = make_response(jsonify(dbqerr), 400)
                                            return(resp)
                                    else:
                                        #For existing SIP or onetime record for the fund
                                        pass
                                        #'''
                                        #This condition doesn't come for new fund insert itself so commenting.
                                        #command = cur.mogrify("UPDATE webapp.pfmforlist select * from json_populate_record(NULL::webapp.pfmforlist,%s) where orormfpflistid = %s and entityid = %s",(str(pfmflsordatajsondict),e.get('orormfpflistid'),entityid,))
                                        
                                        #cur, dbqerr = db.mydbfunc(con,cur,command)
                                        #if cur.closed == True:
                                        #    if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
                                        #        dbqerr['statusdetails']="mflist details insert Failed"
                                        #    resp = make_response(jsonify(dbqerr), 400)
                                        #    return(resp)
                                        #'''
                            else:
                                pass
                        else:
                            #fund is existing so we have to update
                            print("existing fund upate")
                            d['entityid']=entityid
                            d['orpfuserid']=pfdata.get('pfuserid')
                            pfmflsdatalist.append(d['ormflistid'])

                            if 'ormffundorderlists' in d:
                                pfmflsordata = d.pop("ormffundorderlists")
                                print("ormffundorderlists old")
                                print(pfmflsordata)
                            else:
                                pfmflsordata=None
                                print("key ormffundorderlists not in the submitted record")

                            pfmflsdatajsondict = json.dumps(d)
                            #command = cur.mogrify("UPDATE webapp.pfmflist select * from json_populate_record(NULL::webapp.pfmflist,%s) WHERE ormflistid =%s AND entityid = %s;",(str(pfmflsdatajsondict),d.get('ormflistid'),entityid,))
                            
                            #donot update if the fund is fixed : START
                            if(d['ormffndnameedit'] == 'fixed'):
                                command = cur.mogrify("""
                                            UPDATE webapp.pfmflist set(ormffundname,ormffndcode,ormffndnameedit,ormfdathold,ormflmtime) = 
                                            (select ormffundname,ormffndcode,ormffndnameedit,ormfdathold,ormflmtime from json_to_record (%s)
                                            AS (ormffundname varchar(100),ormffndcode varchar(100),ormffndnameedit varchar(100),ormfdathold text,ormflmtime timestamp))
                                            WHERE ormflistid =%s AND entityid = %s;
                                        """,(str(pfmflsdatajsondict),d.get('ormflistid'),entityid,))                       
                                print(command)                
                                cur, dbqerr = db.mydbfunc(con,cur,command)
                                if cur.closed == True:
                                    if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
                                        dbqerr['statusdetails']="mflist insert Failed"
                                    resp = make_response(jsonify(dbqerr), 400)
                                    return(resp)
                            #donot update if the fund is fixed : END

                            #pfmforlsseqnum=1
                            if pfmflsordata != None:
                                for e in pfmflsordata: 
                                    print("PRINTING e")
                                    print(e)                                           
                                    e['ormfoctime']= pfsavetimestamp
                                    e['ormflmtime']= pfsavetimestamp
                                    #e['orormfpflistid']= "or"+d.get('ormflistid')+str(pfmforlsseqnum)
                                    e['orormffundname']=d.get('ormffundname')
                                    e['orormffndcode']=d.get('ormffndcode')
                                    e['entityid']=entityid

                                    #For new SIP or onetime record for the fund
                                    if(e['orormfpflistid'] ==""):                                    
                                        command = cur.mogrify("SELECT MAX(orormfseqnum) FROM webapp.pfmforlist where orormflistid = %s and entityid =%s;",(d.get('ormflistid'),entityid,))
                                        print(command)
                                        cur, dbqerr = db.mydbfunc(con,cur,command)
                                                            
                                        if cur.closed == True:
                                            if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
                                                dbqerr['statusdetails']="Fund MAX sequence failed"
                                            resp = make_response(jsonify(dbqerr), 400)
                                            return(resp)

                                        #Model to follow in all fetch
                                        records=[]
                                        for record in cur:  
                                            records.append(record[0])
                                        print("iam printing records to see")
                                        print(type(records[0]))

                                        if(records[0] == None):
                                            pfmforlsseqnum=1
                                        else:
                                            if(type(records[0])=="Decimal"):
                                                pfmforlsseqnum = int(Decimal(records[0]))+1
                                                
                                            else:
                                                pfmforlsseqnum=records[0]+1
                                        print(pfmforlsseqnum)
                                        print(type(pfmforlsseqnum))
                                        e['orormfpflistid']= "or"+d.get('ormflistid')+str(pfmforlsseqnum)
                                        e['orormflistid']= d.get('ormflistid')
                                        e['orormfseqnum'] = str(pfmforlsseqnum)
                                        e['ororportfolioid']=d.get('orportfolioid')
                                        e['ororpfuserid']=d.get('orpfuserid')
                                        pfmforlsdatalist.append(e['orormfpflistid'])
                                        
                                        pfmforlsseqnum = pfmforlsseqnum+1
                                        print(e)
                                        pfmflsordatajsondict = json.dumps(e)

                                        command = cur.mogrify("INSERT INTO webapp.pfmforlist select * from json_populate_record(NULL::webapp.pfmforlist,%s) where entityid = %s;",(str(pfmflsordatajsondict),entityid,))
                                        print(command)
                                        cur, dbqerr = db.mydbfunc(con,cur,command)
                                        if cur.closed == True:
                                            if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
                                                dbqerr['statusdetails']="mflist details insert Failed"
                                            resp = make_response(jsonify(dbqerr), 400)
                                            return(resp)
                                    else:
                                        #For existing SIP or onetime record for the fund

                                        pfmforlsdatalist.append(e['orormfpflistid'])
                                        pfmflsordatajsondict = json.dumps(e)                                    
                                        
                                        #Record which are only editable to be updated.
                                        if(e['ormffndstatus']=='INCART'):   
                                            command = cur.mogrify("""
                                                        UPDATE webapp.pfmforlist set(orormffundname,orormffndcode,ormffundordelsfreq,ormffundordelsstdt,ormffundordelsamt,ormfsipinstal,ormfsipendt,ormfsipdthold,ormfselctedsip,ormffndstatus,ormflmtime) = 
                                                        (select orormffundname,orormffndcode,ormffundordelsfreq,ormffundordelsstdt,ormffundordelsamt,ormfsipinstal,ormfsipendt,ormfsipdthold,ormfselctedsip,ormffndstatus,ormflmtime from json_to_record (%s)
                                                        AS (orormffundname varchar(100),orormffndcode varchar(100),ormffundordelsfreq varchar(20),ormffundordelsstdt varchar(11),ormffundordelsamt numeric(16,5),ormfsipinstal numeric(3),ormfsipendt date,ormfsipdthold text,ormfselctedsip text,ormffndstatus varchar(10),ormflmtime timestamp))
                                                        WHERE orormfpflistid = %s AND entityid = %s;
                                                    """,(str(pfmflsordatajsondict),e.get('orormfpflistid'),entityid,))


                                            cur, dbqerr = db.mydbfunc(con,cur,command)
                                            if cur.closed == True:
                                                if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
                                                    dbqerr['statusdetails']="mflist details insert Failed"
                                                resp = make_response(jsonify(dbqerr), 400)
                                                return(resp)
                                        else:
                                            pass
                            else:
                                pass
                    
                else:
                    print("done nothing as pfmflsdata is none") 

            #do the clean up of fund sip or oneitme records removed: START
            str2=tuple(pfmflsdatalist)
            print(pfmflsdatalist)
            print(str2)   

            #str3 = "','".join(pfmforlsdatalist)
            #str4 = "'" + str3 + "'"
            str4=tuple(pfmforlsdatalist)
            print(pfmforlsdatalist)
            print(str4)

            if pfmforlsdatalist:
                #Delete the records (SIP or One time records) that are deleted from a fund
                print("inside if")
                command = cur.mogrify("DELETE FROM webapp.pfmforlist where orormfpflistid NOT IN %s AND entityid =%s AND ororpfuserid = %s AND ororportfolioid = %s AND ormffndstatus = %s;",(str4,entityid,userid,pfdata.get('pfportfolioid'),filterstr,))
                print(command)
            else:
                #Delete all the records as all records (SIP or One time records) are deleted for a fund.  
                # But exclude ( this condition ormffndstatus = 'New') already executed order records.
                print("inside else")
                command = cur.mogrify("DELETE FROM webapp.pfmforlist where entityid =%s AND ororpfuserid = %s AND ororportfolioid = %s  AND ormffndstatus = %s;",(entityid,userid,pfdata.get('pfportfolioid'),filterstr,))
                print(command)            
            cur, dbqerr = db.mydbfunc(con,cur,command)
                                
            if cur.closed == True:
                if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
                    dbqerr['statusdetails']="Fund MAX sequence failed"
                resp = make_response(jsonify(dbqerr), 400)
                return(resp)

            #do the clean up of fund sip or oneitme records removed: END
        
            #do the clean up of funds removed: START
            if pfmflsdatalist:                
                command = cur.mogrify("DELETE FROM webapp.pfmflist where ormflistid NOT IN %s AND entityid =%s AND orpfuserid=%s AND orportfolioid= %s;",(str2,entityid,userid,pfdata.get('pfportfolioid'),))
                print(command)
            else:
                command = cur.mogrify("DELETE FROM webapp.pfmflist where entityid =%s AND orpfuserid=%s AND orportfolioid= %s;",(entityid,userid,pfdata.get('pfportfolioid'),))
                print(command)

            cur, dbqerr = db.mydbfunc(con,cur,command)
                                
            if cur.closed == True:
                if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
                    dbqerr['statusdetails']="Fund MAX sequence failed"
                resp = make_response(jsonify(dbqerr), 400)
                return(resp)
            
            #remove the fund where we don't have the any entry for order :START
            if pfmflsdatalist:
                command = cur.mogrify("DELETE FROM webapp.pfmflist where ormflistid IN (SELECT A.ormflistid FROM webapp.pfmflist A LEFT JOIN webapp.pfmforlist B ON A.ormflistid = B.orormflistid WHERE B.orormflistid IS NULL AND A.ormflistid IN %s AND A.entityid = %s) AND entityid =%s AND orpfuserid=%s AND orportfolioid= %s;",(str2,entityid,entityid,userid,pfdata.get('pfportfolioid'),))
                cur, dbqerr = db.mydbfunc(con,cur,command)

                if cur.closed == True:
                    if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
                        dbqerr['statusdetails']="Fund MAX sequence failed"
                    resp = make_response(jsonify(dbqerr), 400)
                    return(resp)
            #remove the fund where we don't have the any entry for order :START
   
            #do the clean up of funds removed: END 
            ###PF MF details update END###

        print("All done and starting cleanups")

        # POST UPDATES FOR ORDER SCREEN : START
        '''
        if screenid == "ord":
            pass
        else:
            pass
        '''
        # POST UPDATES FOR ORDER SCREEN : END


        #POST UPDATES COMMON:START
        # Fund edit/delete allowed : START
        #If atleast one of the order is not new, we should not allow the fund to be removed and edited
        #in this case we mark ormffndnameedit as fixed    
        
        command = cur.mogrify("UPDATE webapp.pfmflist SET ormffndnameedit = 'fixed' WHERE ormflistid in (SELECT distinct orormflistid FROM webapp.pfmforlist WHERE UPPER(ormffndstatus) != 'NEW' and ororpfuserid = %s AND entityid = %s) AND 0 < (SELECT COUNT( distinct orormflistid) FROM webapp.pfmforlist WHERE UPPER(ormffndstatus) != 'NEW' and ororpfuserid = %s AND entityid = %s);",(userid,entityid,userid,entityid,))
        print(command)

        cur, dbqerr = db.mydbfunc(con,cur,command)
                            
        if cur.closed == True:
            if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
                dbqerr['statusdetails']="Fund MAX sequence failed"
            resp = make_response(jsonify(dbqerr), 400)
            return(resp)
        # Fund edit/delete allowed : END

        #POST UPDATES COMMON:END

    con.commit()
    print('order details save successful')
    '''
    #fetch to retun saved data: START
    command = cur.mogrify(
        """
        WITH portport as (select ororportfolioid,orormflistid,orormfpflistid from webapp.pfmforlist where ormffndstatus = 'INCART' AND ororpfuserid = %s AND entityid = %s) 
        select row_to_json(art) from (
        select a.*,
        (select json_agg(b) from (select * from webapp.pfstklist where pfportfolioid = a.pfportfolioid ) as b) as pfstklist, 
        (select json_agg(c) from (select c.*,(select json_agg(d) from (select * from webapp.pfmforlist where orormflistid in (SELECT distinct orormflistid FROM PORTPORT) AND ororportfolioid =a.pfportfolioid AND orormflistid=c.ormflistid AND ormffndstatus = 'INCART' AND entityid = %s ORDER BY ormffundordelstrtyp) as d) as ormffundorderlists 
        from webapp.pfmflist c where ormflistid in (SELECT distinct orormflistid FROM portport) AND  entityid = %s AND orportfolioid =a .pfportfolioid ) as c) as pfmflist 
        from webapp.pfmaindetail as a where pfuserid = %s AND entityid = %s AND pfportfolioid IN (SELECT distinct ororportfolioid FROM portport) ORDER BY pfportfolioid  ) art
        """,(userid,entityid,entityid,entityid,userid,entityid,))

    cur, dbqerr = db.mydbfunc(con,cur,command)
    print("#########################################3")
    print(command)
    print("#########################################3")
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
    records=[]
    for record in cur:  
        records.append(record[0])           
    #fetch to retun saved data: END

    cur.close()
    con.close()

    print("portfolio details returned for user: "+userid)
    print(records)
    resp = json.dumps(records)
    
    return resp
    '''





    

    #clearuppostsave(pfmflsdatalist,pfmforlsdatalist,entityid,userid,pfdata)
    cur.close()
    con.close()
    return jsonify({'natstatus':'success','statusdetails':'Order details for ' + userid +' Saved/Updated'})    