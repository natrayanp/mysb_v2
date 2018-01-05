from Customer_Creation import app
#from .hello_world import app
from flask import request, make_response, jsonify, Response, redirect
from Customer_Creation import settings

import requests
import json
import zeep

@app.route('/custcreation',methods=['GET','POST','OPTIONS'])
def create_user_bse():
	if request.method=='OPTIONS':
		print ("inside custcreation options")
		return 'inside custcreation options'

	elif request.method=='GET':
		## initialise the zeep client for order wsdl
		client = zeep.Client(wsdl=settings.WSDL_UPLOAD_URL[settings.LIVE])
		set_soap_logging()

		## get the password 
		pass_dict = soap_get_password_upload(client)
		## prepare the user record 
		client_code='1234test'
		bse_user = prepare_user_param(client_code)
		## post the user creation request
		user_response = soap_create_user(client, bse_user, pass_dict)
		## TODO: Log the soap request and response post the user creation request

		pass_dict = soap_get_password_upload(client)
		bse_fatca = prepare_fatca_param(client_code)
		fatca_response = soap_create_fatca(client, bse_fatca, pass_dict)
		## TODO: Log the soap request and response post the fatca creation request
		
	return ("success")

# prepare the string that will be sent as param for user creation in bse
def prepare_user_param(client_code):
	# extract the records from the table
	#info = Info.objects.get(id=client_code)
	#kyc = KycDetail.objects.get(user=client_code)
	#bank = BankDetail.objects.get(user=client_code)
	
	# some fields require processing
	## address field can be 40 chars as per BSE but RTA is truncating it to 30 chars and showing that in account statement which is confusing customers, so reducing the length to 30 chars
	'''
	add1 = kyc.address[:30]
	if (len(kyc.address) > 30):
		add2 = kyc.address[30:60]
		if (len(kyc.address) > 60):
			add3 = kyc.address[60:90]
		else:
			add3 = ''
	else:
		add2 = add3 = ''
	appname1 = kyc.first_name
	if (kyc.middle_name != ''):
		appname1 = appname1 + ' ' + kyc.middle_name
	if (kyc.last_name != ''):
		appname1 = appname1 + ' ' + kyc.last_name
	appname1 = appname1[:70]
	
	ifsc_code = bank.branch.ifsc_code
	'''
	# make the list that will be used to create param
	param_list = [
		('CODE', 'NAT1234'),
		('HOLDING', 'SI'),
		('TAXSTATUS', '01'),
		('OCCUPATIONCODE', '01'),
		('APPNAME1', 'appname1'),
		('APPNAME2', ''),
		('APPNAME3', ''),
		('DOB', '04/10/1980'),
		('GENDER', 'M'),
		('FATHER/HUSBAND/gurdian', ''),
		('PAN', 'ARYNJ1340H'),
		('NOMINEE', ''),
		('NOMINEE_RELATION', ''),
		('GUARDIANPAN', ''),
		('TYPE', 'P'),
		('DEFAULTDP', ''),
		('CDSLDPID', ''),
		('CDSLCLTID', ''),
		('NSDLDPID', ''),
		('NSDLCLTID', ''),
		('ACCTYPE_1', 'SB'),
		('ACCNO_1', '1234567654'),
		('MICRNO_1', ''),
		('NEFT/IFSCCODE_1', 'ICIC0006036'),
		('default_bank_flag_1', 'Y'),
		('ACCTYPE_2', ''),
		('ACCNO_2', ''),
		('MICRNO_2', ''),
		('NEFT/IFSCCODE_2', ''),
		('default_bank_flag_2', ''),
		('ACCTYPE_3', ''),
		('ACCNO_3', ''),
		('MICRNO_3', ''),
		('NEFT/IFSCCODE_3', ''),
		('default_bank_flag_3', ''),
		('ACCTYPE_4', ''),
		('ACCNO_4', ''),
		('MICRNO_4', ''),
		('NEFT/IFSCCODE_4', ''),
		('default_bank_flag_4', ''),
		('ACCTYPE_5', ''),
		('ACCNO_5', ''),
		('MICRNO_5', ''),
		('NEFT/IFSCCODE_5', ''),
		('default_bank_flag_5', ''),
		('CHEQUENAME', ''),
		('ADD1', 'add1'),
		('ADD2', 'add2'),
		('ADD3', 'add3'),
		('CITY', 'city'),
		('STATE', 'TN'),
		('PINCODE', '600032'),
		('COUNTRY', 'India'),
		('RESIPHONE', ''),
		('RESIFAX', ''),
		('OFFICEPHONE', ''),
		('OFFICEFAX', ''),
		('EMAIL', 'email@gmail.com'),
		('COMMMODE', 'M'),
		('DIVPAYMODE', '02'),
		('PAN2', ''),
		('PAN3', ''),
		('MAPINNO', ''),
		('CM_FORADD1', ''),
		('CM_FORADD2', ''),
		('CM_FORADD3', ''),
		('CM_FORCITY', ''),
		('CM_FORPINCODE', ''),
		('CM_FORSTATE', ''),
		('CM_FORCOUNTRY', ''),
		('CM_FORRESIPHONE', ''),
		('CM_FORRESIFAX', ''),
		('CM_FOROFFPHONE', ''),
		('CM_FOROFFFAX', ''),
		('CM_MOBILE', '9677628897'),
	]

	# prepare the param field to be returned
	user_param = ''
	for param in param_list:
		user_param = user_param + '|' + str(param[1])
	# print user_param
	return user_param[1:]


# prepare the string that will be sent as param for fatca creation in bse
def prepare_fatca_param(client_code):
	# extract the records from the table
	kyc = KycDetail.objects.get(user=client_code)
	
	# some fields require processing
	inv_name = kyc.first_name
	if (kyc.middle_name != ''):
		inv_name = inv_name + ' ' + kyc.middle_name
	if (kyc.last_name != ''):
		inv_name = inv_name + ' ' + kyc.last_name
	inv_name = inv_name[:70]
	if kyc.occ_code == '01':
		srce_wealt = '02'
		occ_type = 'B'
	else:
		srce_wealt = '01'
		occ_type = 'S'

	# make the list that will be used to create param
	param_list = [
		('PAN_RP', 'ARYNJ1340H'),
		('PEKRN', ''),
		('INV_NAME', 'appname1'),
		('DOB', ''),
		('FR_NAME', ''),
		('SP_NAME', ''),
		('TAX_STATUS', '1'),
		('DATA_SRC', 'E'),
		('ADDR_TYPE', '1'),
		('PO_BIR_INC', 'IN'),
		('CO_BIR_INC', 'IN'),
		('TAX_RES1', 'IN'),
		('TPIN1', 'ARYNJ1340H'),
		('ID1_TYPE', 'C'),
		('TAX_RES2', ''),
		('TPIN2', ''),
		('ID2_TYPE', ''),
		('TAX_RES3', ''),
		('TPIN3', ''),
		('ID3_TYPE', ''),
		('TAX_RES4', ''),
		('TPIN4', ''),
		('ID4_TYPE', ''),
		('SRCE_WEALT', '01'),
		('CORP_SERVS', ''),
		('INC_SLAB', '32'),
		('NET_WORTH', ''),
		('NW_DATE', ''),
		('PEP_FLAG', 'N'),
		('OCC_CODE', '03'),
		('OCC_TYPE', 'Service'),
		('EXEMP_CODE', ''),
		('FFI_DRNFE', ''),
		('GIIN_NO', ''),
		('SPR_ENTITY', ''),
		('GIIN_NA', ''),
		('GIIN_EXEMC', ''),
		('NFFE_CATG', ''),
		('ACT_NFE_SC', ''),
		('NATURE_BUS', ''),
		('REL_LISTED', ''),
		('EXCH_NAME', 'O'),
		('UBO_APPL', 'N'),
		('UBO_COUNT', ''),
		('UBO_NAME', ''),
		('UBO_PAN', ''),
		('UBO_NATION', ''),
		('UBO_ADD1', ''),
		('UBO_ADD2', ''),
		('UBO_ADD3', ''),
		('UBO_CITY', ''),
		('UBO_PIN', ''),
		('UBO_STATE', ''),
		('UBO_CNTRY', ''),
		('UBO_ADD_TY', ''),
		('UBO_CTR', ''),
		('UBO_TIN', ''),
		('UBO_ID_TY', ''),
		('UBO_COB', ''),
		('UBO_DOB', ''),
		('UBO_GENDER', ''),
		('UBO_FR_NAM', ''),
		('UBO_OCC', ''),
		('UBO_OCC_TY', ''),
		('UBO_TEL', ''),
		('UBO_MOBILE', ''),
		('UBO_CODE', ''),
		('UBO_HOL_PC', ''),
		('SDF_FLAG', ''),
		('UBO_DF', ''),
		('AADHAAR_RP', ''),
		('NEW_CHANGE', 'N'),
		('LOG_NAME','NAT1234'),
		('DOC1', ''),
		('DOC2', ''),
	]

	# prepare the param field to be returned
	fatca_param = ''
	for param in param_list:
		fatca_param = fatca_param + '|' + str(param[1])
	# print fatca_param
	return fatca_param[1:]

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
		print('#################')
		print(pass_dict)
		print('#################')
		return pass_dict
	else:
		raise Exception(
			"BSE error 640: Login unsuccessful for upload API endpoint"
		)

## fire SOAP query to create a new user on bsestar
def soap_create_user(client, user_param, pass_dict):
	method_url = settings.METHOD_UPLOAD_URL[settings.LIVE] + 'MFAPI'
	header_value = soap_set_wsa_headers(method_url, settings.SVC_UPLOAD_URL[settings.LIVE])
	response = client.service.MFAPI(
		'02',
		settings.USERID[settings.LIVE],
		pass_dict['password'],
		user_param,
		_soapheaders=[header_value]
	)
	
	## this is a good place to put in a slack alert

	response = response.split('|')
	status = response[0]
	if (status == '100'):
		# User creation successful
		pass
	else:
		raise Exception(
			"BSE error 644: User creation unsuccessful: %s" % response[1]
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
