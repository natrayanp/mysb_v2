from pf import app
from pf import dbfunc as db
from pf import jwtdecodenoverify as jwtnoverify

from flask import request, make_response, jsonify, Response, redirect
from datetime import datetime
from order import dbfunc as db
from order import jwtdecodenoverify as jwtnoverify
from dateutil import tz
from datetime import datetime
from datetime import date
from pf import settings
from multiprocessing import Process
from multiprocessing import Pool

import requests
import json
import zeep

#@app.route('/orderapi',methods=['GET','POST','OPTIONS'])
#def place_order_bse():
def place_order_bse(jsondata):
    '''
    if request.method=='OPTIONS':
        print ("inside orderapi options")
        return 'inside orderapi options'

    elif request.method=='POST':
        print("inside orderapi POST")

        print((request))        
        #userid,entityid=jwtnoverify.validatetoken(request)
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        payload= request.get_json()
        #payload=json.loads(payload)
        print(payload)
        bse_order = json.loads(payload)
        '''
    bse_orders=json.loads(jsondata)
    print("insde bse order")
    print(bse_orders)

    client = zeep.Client(wsdl=settings.WSDL_ORDER_URL[settings.LIVE])
    set_soap_logging()

    ## get the password 
    global pass_dict
    pass_dict = soap_get_password_order(client)

    print(bse_orders)
    print("ontime multiprocessing starts")
    pool = Pool(processes=10)
    result = pool.map_async(send_one_order, bse_orders)
    result.wait()        
    print("end with ontime")
    print(result.get())
    order_resp = result.get()
    pool.close()
    pool.join()
    
    return order_resp


def send_one_order(bse_order):
    print(bse_order)

    bse_order['user_id'] = settings.USERID[settings.LIVE]
    bse_order['member_id'] = settings.MEMBERID[settings.LIVE]
    bse_order['password'] = pass_dict['password']
    bse_order['pass_key'] = pass_dict['passkey']
    

    ## prepare order, post it to BSE and save response
    ## for lumpsum transaction 
    if (bse_order['mfor_ordertype'] == 'OneTime'):
        ## prepare the transaction record
        #bse_order = prepare_order(transaction, pass_dict)
        ## post the transaction
        print('****************************')
        print("before delete")
        print(bse_order)

        del bse_order['mfor_ordertype']
        
        print("after delete")
        print(bse_order)
        
        order_resp = soap_post_onetime_order(client, bse_order)
        
        print("order id")
        print(order_resp)
        print('****************************')
    

    elif(bse_order.order_type == 'SIP'):
        ## since xsip orders cannot be placed in off-market hours, 
        ## placing a lumpsum order instead 
        #bse_order = prepare_xsip_order(transaction, pass_dict)
        ## post the transaction
        order_resp = soap_post_xsip_order(client, bse_order)

    else:
        '''
        raise Exception(
            "Internal error 630: Invalid order_type in transaction"
        )
        '''
        order_resp  = {
            'trans_code' : bse_order['trans_code'],
            'trans_no' : bse_order['trans_no'],
            'order_id' : bse_order['order_id'],
            'user_id' : bse_order['user_id'],
            'member_id' : bse_order['member_id'],
            'client_code' : bse_order['client_code'],
            'bse_remarks' : 'order not sent to BSE due to internal errors',
            'success_flag' :100,
            'order_type' : '',
        }
    return order_resp

def soap_get_password_order(client):
    method_url = settings.METHOD_ORDER_URL[settings.LIVE] + 'getPassword'
    svc_url = settings.SVC_ORDER_URL[settings.LIVE]
    print(method_url)
    print(svc_url)
    header_value = soap_set_wsa_headers(method_url, svc_url)
    print("reached here")
    response = client.service.getPassword(
        UserId=settings.USERID[settings.LIVE], 
        Password=settings.PASSWORD[settings.LIVE], 
        PassKey=settings.PASSKEY[settings.LIVE], 
        _soapheaders=[header_value]
    )
    
    response = response.split('|')
    status = response[0]
    if (status == '100'):
        pass_dict = {'password': response[1], 'passkey': settings.PASSKEY[settings.LIVE]}
        return pass_dict
    else:
        raise Exception(
            "BSE error 640: Login unsuccessful for Order API endpoint"
        )


# set logging such that its easy to debug soap queries
def set_soap_logging():
	import logging.config
	logging.config.dictConfig({
		'version': 1,
	    'formatters': {
	        'verbose': {
	            'format': '%(name)s: %(message)s'
	        }
	    },
	    'handlers': {
	        'console': {
	            'level': 'DEBUG',
	            'class': 'logging.StreamHandler',
	            'formatter': 'verbose',
	        },
	    },
	    'loggers': {
	        'zeep.transports': {
	            'level': 'DEBUG',
	            'propagate': True,
	            'handlers': ['console'],
	        },
	    }
	})


## fire SOAP query to post the order 
def soap_post_onetime_order(client, bse_order):
    method_url = settings.METHOD_ORDER_URL[settings.LIVE] + 'orderEntryParam'
    header_value = soap_set_wsa_headers(method_url, settings.SVC_ORDER_URL[settings.LIVE])
    response = client.service.orderEntryParam(
        bse_order['trans_code'],
        bse_order['trans_no'],
        bse_order['order_id'],
        bse_order['user_id'],
        bse_order['member_id'],
        bse_order['client_code'],
        bse_order['scheme_cd'],
        bse_order['buy_sell'],
        bse_order['buy_sell_type'],
        bse_order['dptxn_mode'],
        bse_order['order_amt'],
        bse_order['order_qty'],
        bse_order['all_redeem'],
        bse_order['folio_no'],
        bse_order['remarks'],
        bse_order['kyc_status'],
        bse_order['internal_transaction'],
        bse_order['subbr_code'],
        bse_order['euin'],
        bse_order['euin_flg'],
        bse_order['min_redeem'],
        bse_order['dpc_flg'],
        bse_order['ipadd'],
        bse_order['password'],
        bse_order['pass_key'],
        bse_order['subbr_arn'],
        bse_order['param2'],
        bse_order['param3'],
        _soapheaders=[header_value]
    )

    ## this is a good place to put in a slack alert

    response = response.split('|')
    print(response)
    ## store the order response in a table
    order_resp= store_order_response(response, 'OneTime')
    
    status = order_resp['success_flag']
    if (status == '0'):
        # order successful
        print("order successful")
    else:
        print("order failure")
        
        '''
        raise Exception(
            "BSE error 641: %s" % response[6]
        )
        '''
    return order_resp


## fire SOAP query to post the XSIP order 
def soap_post_xsip_order(client, bse_order):
    method_url = settings.METHOD_ORDER_URL[settings.LIVE] + 'xsipOrderEntryParam'
    header_value = soap_set_wsa_headers(method_url, settings.SVC_ORDER_URL[settings.LIVE])
    response = client.service.xsipOrderEntryParam(
        bse_order.trans_code,
        bse_order.trans_no,
        bse_order.scheme_cd,
        bse_order.member_id,
        bse_order.client_code,
        bse_order.user_id,
        bse_order.int_ref_no,
        bse_order.trans_mode,
        bse_order.dp_txn,
        bse_order.start_date,
        bse_order.freq_type,
        bse_order.freq_allowed,
        bse_order.inst_amt,
        bse_order.num_inst,
        bse_order.remarks,
        bse_order.folio_no,
        bse_order.first_order_flag,
        bse_order.brokerage,
        bse_order.mandate_id,
        # '',
        bse_order.sub_br_code,
        bse_order.euin,
        bse_order.euin_val,
        bse_order.dpc,
        bse_order.xsip_reg_id,
        bse_order.ip_add,
        bse_order.password,
        bse_order.pass_key,
        bse_order.param1,
        # bse_order.mandate_id,
        bse_order.param2,
        bse_order.param3,
        _soapheaders=[header_value]
    )

    ## this is a good place to put in a slack alert

    response = response.split('|')
    ## store the order response in a table
    order_id = store_order_response(response, 'SIP')
    status = response[7]
    if (status == '0'):
        # order successful
        return order_id
    else:
        raise Exception(
            "BSE error 642: %s" % response[6]
        )




# store response to order entry from bse 
def store_order_response(response, order_type):
## lumpsum order 
    if (order_type == 'OneTime'):
        trans_response = {
            'trans_code' : response[0],
            'trans_no' : response[1],
            'order_id' : response[2],
            'user_id' : response[3],
            'member_id' : response[4],
            'client_code' : response[5],
            'bse_remarks' : response[6],
            'success_flag' : response[7],
            'order_type' : 'OneTime',
        }
    ## SIP order  
    elif (order_type == 'SIP'):
        trans_response = {
            'trans_code' : response[0],
            'trans_no' : response[1],
            'member_id' : response[2],
            'client_code' : response[3],
            'user_id' : response[4],
            'order_id' : response[5],
            'bse_remarks' : response[6],
            'success_flag' : response[7],
            'order_type' : 'SIP',
        }
    #trans_response.save()
    return trans_response

# every soap query to bse must have wsa headers set 
def soap_set_wsa_headers(method_url, svc_url):    

    header = zeep.xsd.Element('{http://test.python-zeep.org}auth', zeep.xsd.ComplexType([
        zeep.xsd.Element('{http://www.w3.org/2005/08/addressing}Action', zeep.xsd.String()),
        zeep.xsd.Element('{http://www.w3.org/2005/08/addressing}To', zeep.xsd.String())
        ])
    )
    header_value = header(Action=method_url, To=svc_url)
    
    
    return header_value
