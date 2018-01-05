from Mandate_Creation import app
#from .hello_world import app
from flask import request, make_response, jsonify, Response, redirect
from Mandate_Creation import settings

import requests
import json
import zeep

@app.route('/mandatecreation',methods=['GET','POST','OPTIONS'])
def create_mandate_bse():
	if request.method=='OPTIONS':
		print ("inside custcreation options")
		return 'inside custcreation options'

	elif request.method=='GET':
		'''
		Creates mandate for user for a specific amount 
		Called before creating an SIP transaction on BSEStar because 
			every SIP transaction requires a mandate
		'''

		## initialise the zeep client for wsdl
		client = zeep.Client(wsdl=settings.WSDL_UPLOAD_URL[settings.LIVE])
		set_soap_logging()

		## get the password
		#check if we already have the password if yes use it else get the password
		pass_dict = soap_get_password_upload(client)
		
		## prepare the mandate record 
		#bse_mandate = prepare_mandate_param(client_code, amount)
		bse_mandate = prepare_mandate_param('client_code', 1234)

		## post the mandate creation request
		mandate_id = soap_create_mandate(client, bse_mandate, pass_dict)
		return mandate_id
		
	return ("success")

# prepare the string that will be sent as param for user creation in bse
def prepare_mandate_param(client_code, amount):
	# extract the records from the table
	#info = Info.objects.get(id=client_code)
	#bank = BankDetail.objects.get(user=client_code)
	
	# make the list that will be used to create param
	param_list = [
		('MEMBERCODE', settings.MEMBERID[settings.LIVE]),
		('CLIENTCODE', client_code),
		('AMOUNT', amount),
		('IFSCCODE', 'ICIC0003964'),
		('ACCOUNTNUMBER', '1234567654'),
		('MANDATETYPE', 'X'),
	]

	# prepare the param field to be returned
	mandate_param = ''
	for param in param_list:
		mandate_param = mandate_param + '|' + str(param[1])
	# print user_param
	print('print the mandate')
	print(mandate_param[1:])
	return mandate_param[1:]


## fire SOAP query to create a new mandate on bsestar
def soap_create_mandate(client, mandate_param, pass_dict):
	method_url = METHOD_UPLOAD_URL[settings.LIVE] + 'MFAPI'
	header_value = soap_set_wsa_headers(method_url, SVC_UPLOAD_URL[settings.LIVE])
	response = client.service.MFAPI(
		'06',
		settings.USERID[settings.LIVE],
		pass_dict['password'],
		mandate_param,
		_soapheaders=[header_value]
	)
	
	## this is a good place to put in a slack alert

	response = response.split('|')
	status = response[0]
	if (status == '100'):
		# Mandate creation successful, so save it in table
		from users.models import Mandate, BankDetail
		mandate_values = mandate_param.split('|')
		mandate_id = int(response[2])
		bank = BankDetail.objects.get(user_id=int(mandate_values[1]))

		mandate = Mandate.objects.create(
            user = Info.objects.get(id=int(mandate_values[1])),
            bank = bank,
            id = mandate_id,
            amount = int(mandate_values[2]),
            status = '2',
        )
		if (bank.branch.ifsc_code != mandate_values[3]):
			# raise error that banks dont match
			raise Exception(
				"BSE error 651: Mandate created for a bank that doesnt match with user's bank"
			)
		return mandate_id
	else:
		raise Exception(
			"BSE error 651: Mandate creation unsuccessful: %s" % response[1]
		)



## fire SOAP query to get password for Upload API endpoint
## used by all functions except create_transaction_bse() and cancel_transaction_bse()
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
		return pass_dict
	else:
		raise Exception(
			"BSE error 640: Login unsuccessful for upload API endpoint"
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
