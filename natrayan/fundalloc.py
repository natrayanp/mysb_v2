from natrayan import app
from flask import redirect, request, jsonify
#from flask import request, make_response, jsonify, Response, redirect
from datetime import datetime

import psycopg2
import json
import jwt


@app.route('/getfundaloc',methods=['GET','POST','OPTIONS'])
def getfundaloc():
    if request.method=='OPTIONS':
        print ("inside options")
        return jsonify({'body':'success'})

    elif request.method=='GET':   
        records=[]
        print('inside inside gettfunaloc')
        
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

            #This is to be moved to a configurable place
            conn_string = "host='localhost' dbname='postgres' user='postgres' password='password123'"
            #This is to be moved to a configurable place
            con=psycopg2.connect(conn_string)
            cur = con.cursor()

            command = cur.mogrify("select pfportfolioid,pfportfolioname from pfmaindetail where pfuserid =%s;",(userid,))
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
                print('inside for')
                print(record)             
                records.append(record)

            pftotallist=records 
            print('pftotallist')
            print(pftotallist)
            print(type(pftotallist))
            #print("portfolio details returned for user: "+userid)
            
            for x in pftotallist:

                if ('AB00121') in x:
                    print('insider true')
                else:
                    print('inside else')


            command = cur.mogrify("select pfportfolioid,pfportfolioname,alocpfallocated,alocpfusedtoday,alocpflastupdt from aloclist where pfportfolioid in (select pfportfolioid from pfmaindetail where pfuserid =%s );",(userid,) )
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
            
            allocpflist=[]
            fulllist=[]
            dummy=[]     
            print(record)
            #Model to follow in all fetch
            for record in cur: 
                dummy=record[0:2]
                allocpflist.append(dummy)
                dummy=[]           
                allocpflist.append(record)
            #allocpflist = records
            print('allocpflist')
            print(allocpflist)
            print(type(allocpflist))
            print('fulllist')
            print(fulllist)
            print(type(fulllist))
            #Get the missing portfolios for insert
            diflist=set(pftotallist).difference(allocpflist)
            print('diflist')
            print(diflist)
            #Assumption of diflist is to have any record that has diff name as well
            s = set()
            if(diflist):
                for pfrec in diflist:
                    (npfportfolioid,npfportfolioname) = pfrec                    
                    '''
                    s.add((pfrec[0],pfrec[1]))
                    print("start#############################") 
                    print(s)
                    print("#############################") 
                    '''
                    print(npfportfolioid)
                    print(npfportfolioname)                    
                    command = cur.mogrify("INSERT INTO aloclist (pfportfolioid, pfportfolioname,alocpfallocated,alocpfusedtoday,alocpflastupdt,alococtime,aloclmtime) VALUES (%s,%s,0,0,CURRENT_DATE,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP) ON CONFLICT (pfportfolioid) DO UPDATE SET pfportfolioname = %s;",(npfportfolioid,npfportfolioname,npfportfolioname,))
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
                    con.commit()                  
                    print(cur)
                    print('consider insert or update is successful')
                    

            else:
                print('No diff list')
            

            command = cur.mogrify("UPDATE aloclist SET alocpfallocated =alocpfusedtoday + alocpfallocated, alocpfusedtoday = 0, alocpflastupdt = CURRENT_DATE, aloclmtime = CURRENT_TIMESTAMP WHERE pfportfolioid IN (SELECT pfportfolioid FROM aloclist WHERE alocpflastupdt != CURRENT_DATE);")
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
            else:
                con.commit()

            command = cur.mogrify("select json_agg(c) from (select pfportfolioid,pfportfolioname,alocpfallocated,alocpfusedtoday,alocpfnewallocated,alocpftotal from aloclist where pfportfolioid in (select pfportfolioid from pfmaindetail where pfuserid =%s )) as c;",(userid,) )
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
            else:
                pass
            
            print(cur)
            for record in cur:  
                print('inside final json')
                print(record[0])             

            '''
            pftotallist

            #find records that are not in allocpflist but in pftotallist
            #insert missing records
            #return the records from alloclisttable
            '''     
        return json.dumps(record[0])




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