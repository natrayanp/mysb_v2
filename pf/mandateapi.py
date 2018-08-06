from pf import app
from flask import request, make_response, jsonify, Response, redirect
from pf import settings
from datetime import datetime

import requests
from multiprocessing import Process
from multiprocessing import Pool
import json
import zeep

#@app.route('/mandate',methods=['GET','POST','OPTIONS'])
#def mandate():
def mandate(payloaddata):
	'''
	if request.method=='OPTIONS':
		print ("inside mandate options")
		return 'inside mandate options'

	elif request.method=='POST':
		print("inside mandate POST")

		print((request))        
		#userid,entityid=jwtnoverify.validatetoken(request)
		print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
		payloaddata = request.get_json()
		#payload=json.loads(payload)
	'''
	
	payload = payloaddata['data']
	operation = payloaddata['operation']
	bse_orders = payload
	print(operation)
	print(payload)
	
	## initialise the zeep client for order wsdl
	client = zeep.Client(wsdl=settings.WSDL_UPLOAD_URL[settings.LIVE])
	set_soap_logging()

	## get the password 
	pass_dict = soap_get_password_upload(client)

	for bse_order in bse_orders:
		bse_order['password'] = pass_dict['password']
		bse_order['pass_key'] = pass_dict['passkey']
		
	print(bse_orders)
	
	print("mandate multiprocessing starts")
	pool = Pool(processes=10)
	result = pool.map_async(send_one_mandate, bse_orders)
	print(result)
	result.wait()    
	print(result.get())
	mand_resp = result.get()
	pool.close()
	pool.join()    
	print('all done')
	print("mand_resp")
	print(mand_resp)
	return mand_resp

def send_one_mandate(bseorders):
	bse_mandate = prepare_mandate_param(bseorders)
	client = zeep.Client(wsdl=settings.WSDL_UPLOAD_URL[settings.LIVE])
	## post the mandate creation request
	bse_resp = soap_post_mandate(client, bse_mandate, bseorders['password'])
	if bse_resp['bsestatus'] == '100':
		mandate_resp = {'trans_code': 'NEW', 'order_type': 'mandcreate', 'int_mandate_id': bseorders['internalid'], 'bse_mandate_id': bse_resp['bsemandateid'],'bse_remarks': bse_resp['bserespmsg'], 'success_flag': bse_resp['bsestatus']}
	else:
		mandate_resp = {'trans_code': 'NEW', 'order_type': 'mandcreate', 'int_mandate_id': bseorders['internalid'], 'bse_mandate_id': '','bse_remarks': bse_resp['bserespmsg'], 'success_flag': bse_resp['bsestatus']}
	print("mandate response")
	print(mandate_resp)
	print('****************************')
	return mandate_resp

# prepare the string that will be sent as param for mandate creation in bse
def prepare_mandate_param(payload):
	# make the list that will be used to create param
	d=payload
	print(type(d))
	print( d['clientcode'])
	
	param_list = [
		('CLIENTCODE', d['clientcode']),
		('AMOUNT', d['amount']),
		('MANDATETYPE', d['mandatetype']),
		('ACCOUNTNUMBER', d['accountno']),
		('ACCOUNTTYPE', d['actype']),
		('IFSCCODE', d['ifsccode']),
		('MICRCODE', '' if d['micrcode'] == None else d['micrcode']),
		('STARTDATE', d['startdate']),
		('ENDDATE', d['enddate'])
	]

	# prepare the param field to be returned
	mandate_param = ''
	for param in param_list:
		mandate_param = mandate_param + '|' + str(param[1])
	# print mandate_param
	return mandate_param[1:]

## fire SOAP query to create a new mandate on bsestarmf
def soap_post_mandate(client, bse_mandate,passw):
	method_url = settings.METHOD_UPLOAD_URL[settings.LIVE] + 'MFAPI'
	header_value = soap_set_wsa_headers(method_url, settings.SVC_UPLOAD_URL[settings.LIVE])
	response = client.service.MFAPI(
		'06',
		settings.USERID[settings.LIVE],
		passw,
		bse_mandate,
		_soapheaders=[header_value]
	)
	
	response = response.split('|')
	print(response)
	status = response[0]
	if status == '100':
		return {'bsestatus': response[0], 'bserespmsg': response[1], 'bsemandateid': response[2]}
	else:
		return {'bsestatus': response[0], 'bserespmsg': response[1], 'bsemandateid': ''}


## fire SOAP query to get password for endpoint
def soap_get_password_upload(client):
	method_url = settings.METHOD_UPLOAD_URL[settings.LIVE] + 'getPassword'
	svc_url = settings.SVC_UPLOAD_URL[settings.LIVE]
	header_value = soap_set_wsa_headers(method_url, svc_url)
	response = client.service.getPassword(
		MemberId=settings.MEMBERID[settings.LIVE], 
		UserId=settings.USERID[settings.LIVE],
		Password=settings.PASSWORD[settings.LIVE], 
		PassKey=settings.PASSKEY[settings.LIVE], 
		_soapheaders=[header_value]
	)
	print
	response = response.split('|')
	status = response[0]
	if (status == '100'):
		# login successful
		pass_dict = {'password': response[1], 'passkey': settings.PASSKEY[settings.LIVE]}
		print('#################')
		print(pass_dict)
		print('#################')
		return pass_dict
	else:
		raise Exception(
			"BSE error 640: Login unsuccessful for upload API endpoint"
		)





#################################################################
#################################################################
########### THIS IS NOT WORKING CHECKING WITH BSE ###############
#################################################################
#################################################################

@app.route('/mandatestatus',methods=['GET','POST','OPTIONS'])
def mandatestatus():
	
	if request.method=='OPTIONS':
		print ("inside mandate options")
		return 'inside mandate options'

	elif request.method=='POST':
		print("inside mandate POST")

		print((request))        
		#userid,entityid=jwtnoverify.validatetoken(request)
		print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
		payloaddata = request.get_json()
		#payload=json.loads(payload)		

		client = zeep.Client(wsdl=settings.WSDL_MANDATESTAT_URL[settings.LIVE])
		set_soap_logging()

		## get the password 
		pass_dict = soap_get_mand_password_upload(client)
		print(pass_dict)
		'''
		data_to_bse = {
			'ClientCode': 'A000000001',
			'Date': '28/07/2018',
			'RegnNo': '129438',
			'SystematicPlanType': 'SIP'
		}
		'''
		data_to_bse = {
			'ClientCode': 'A000000001',
			'FromDate': '01/01/2018',
			'MandateId':'BSE000000018169',
			'ToDate': '01/08/2018'
		}
		#472199

		soap_rsp = soap_mandate_status(client, data_to_bse, pass_dict)
		#soap_rsp = soap_child_order_status(client, data_to_bse, pass_dict)

		print(soap_rsp)
		return "ok"


def soap_get_mand_password_upload(client):
	method_url = settings.METHOD_MANDATESTAT_URL[settings.LIVE] + 'getPassword'   #For Mandate status
	#method_url = settings.METHOD_MANDATESTAT_URL[settings.LIVE] + 'GetPasswordForChildOrder'  #For ChildORders
	svc_url = settings.SVC_MANDATESTAT_URL[settings.LIVE]
	header_value = soap_set_wsa_headers(method_url, svc_url)
	response = client.service.getPassword(
		#RequestType = 'MANDATE',
		MemberId=settings.MEMBERID[settings.LIVE], 
		UserId=settings.USERID[settings.LIVE],
		Password=settings.PASSWORD[settings.LIVE], 
		PassKey=settings.PASSKEY[settings.LIVE], 
		_soapheaders=[header_value]
	)
	print (response)
	response = response.split('|')
	status = response[0]
	if (status == '100'):
		# login successful
		pass_dict = {'password': response[1], 'passkey': settings.PASSKEY[settings.LIVE]}
		print('#################')
		print(pass_dict)
		print('#################')
		return pass_dict
	else:
		raise Exception(
			"BSE error 640: Login unsuccessful for upload API endpoint"
		)


def soap_mandate_status(client, payload, pass_dict):
    method_url = settings.METHOD_MANDATESTAT_URL[settings.LIVE] + 'MandateDetails'
    svc_url = settings.SVC_MANDATESTAT_URL[settings.LIVE]
    header_value = soap_set_wsa_headers(method_url, svc_url)
    #logout_url = 'http://localhost:8000/orpost'
	
    response = client.service.MandateDetails({
        'FromDate':payload['FromDate'],
        'ToDate':payload['ToDate'],
        'MemberCode':settings.MEMBERID[settings.LIVE],
        'ClientCode': payload['ClientCode'],
        'MandateId':payload['MandateId'],
        'EncryptedPassword': pass_dict['password']
        },
        #settings.MEMBERID[settings.LIVE]+'|'+client_code+'|'+logout_url,
        _soapheaders=[header_value]
    )
    print(response)

    return response

def soap_child_order_status(client, payload, pass_dict):
    method_url = settings.METHOD_MANDATESTAT_URL[settings.LIVE] + 'ChildOrderDetails'
    svc_url = settings.SVC_MANDATESTAT_URL[settings.LIVE]
    header_value = soap_set_wsa_headers(method_url, svc_url)
    #logout_url = 'http://localhost:8000/orpost'
    print(pass_dict['password'])
    response = client.service.ChildOrderDetails({
        'ClientCode': payload['ClientCode'],
        'Date':payload['Date'],
        'EncryptedPassword': pass_dict['password'],
        'RegnNo':payload['RegnNo'],
        'MemberCode':settings.MEMBERID[settings.LIVE],
        'SystematicPlanType':payload['SystematicPlanType']
        },
        #settings.MEMBERID[settings.LIVE]+'|'+client_code+'|'+logout_url,
        _soapheaders=[header_value]
    )
    print(response)

    return response

#################################################################
#################################################################
######## THIS IS NOT WORKING CHECKING WITH BSE: END #############
#################################################################
#################################################################






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

	################ HELPER SOAP FUNCTIONS

# every soap query to bse must have wsa headers set 
def soap_set_wsa_headers(method_url, svc_url):
	print(method_url)
	print(svc_url)
	header = zeep.xsd.Element("None", zeep.xsd.ComplexType([
		zeep.xsd.Element('{http://www.w3.org/2005/08/addressing}Action', zeep.xsd.String()),
		zeep.xsd.Element('{http://www.w3.org/2005/08/addressing}To', zeep.xsd.String())
		])
	)
	header_value = header(Action=method_url, To=svc_url)
	return header_value