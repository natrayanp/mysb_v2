from allprocessing import app
from flask import jsonify

import psycopg2


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