from customercreationapi import app
#from .hello_world import app
from flask import request, make_response, jsonify, Response, redirect
from customercreationapi import settings
from datetime import datetime

import requests
import json
import zeep

@app.route('/custcreation',methods=['GET','POST','OPTIONS'])
def create_user_bse():
	if request.method=='OPTIONS':
		print ("inside custcreation options")
		return 'inside custcreation options'

	elif request.method=='POST':
		print("inside REGISTRATIONDETAILSFETCH GET")

		print((request))        
		#userid,entityid=jwtnoverify.validatetoken(request)
		print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
		payload= request.get_json()
		#payload=json.loads(payload)
		print(payload)
		
		#clientdata,fatcadata=custdatavalidation(payload)
		#reqdataifsc=payload[''ifsc']
		## initialise the zeep client for order wsdl
		client = zeep.Client(wsdl=settings.WSDL_UPLOAD_URL[settings.LIVE])
		set_soap_logging()

		## get the password 
		pass_dict = soap_get_password_upload(client)
		## prepare the user record 
		#client_code='1234test'
		#payload=request.get_json()

		bse_user = prepare_user_param(payload)
		## post the user creation request
		user_response = soap_create_user(client, bse_user, pass_dict)
		## TODO: Log the soap request and response post the user creation request
		if user_response['bsesttuscode'] == '100':
			#pass_dict = soap_get_password_upload(client)
			bse_fatca = prepare_fatca_param(payload)
			fatca_response = soap_create_fatca(client, bse_fatca, pass_dict)
			## TODO: Log the soap request and response post the fatca creation request
			if fatca_response['bsesttuscode'] == '100':
				return make_response(jsonify({'statuscode': fatca_response['bsesttuscode'], 'statusmessage': "User and Fatca record created successfully"}),200)
			else:
				return make_response(jsonify({'statuscode': fatca_response['bsesttuscode'], 'statusmessage': fatca_response['bsesttusmsg']}),400)
		else:
			return make_response(jsonify({'statuscode': user_response['bsesttuscode'], 'statusmessage': user_response['bsesttusmsg']}),400)

		'''
		pass_dict = soap_get_password_upload(client)
		bse_fatca = prepare_fatca_param(client_code)
		fatca_response = soap_create_fatca(client, bse_fatca, pass_dict)
		## TODO: Log the soap request and response post the fatca creation request
		
		return ("success")
		'''

# prepare the string that will be sent as param for user creation in bse
def prepare_user_param(payload):
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
	d=payload
	print(type(d))
	print( d['clientcode'])
	
	param_list = [
		('CODE', d['clientcode']),
		('HOLDING', d['clientholding']),
		('TAXSTATUS', d['clienttaxstatus']),
		('OCCUPATIONCODE', d['clientoccupationcode']),
		('APPNAME1', d['clientappname1']),
		('APPNAME2', d['clientappname2']),
		('APPNAME3', d['clientappname3']),
		('DOB', d['clientdob']),  							#to change the format
		('GENDER', d['clientgender']),						
		('FATHER/HUSBAND/gurdian', d['clientguardian']),
		('PAN', d['clientpan']),
		('NOMINEE', d['clientnominee']),
		('NOMINEE_RELATION', d['clientnomineerelation']),
		('GUARDIANPAN', d['clientguardianpan']),
		('TYPE', d['clienttype']),
		('DEFAULTDP', d['clientdefaultdp']),
		('CDSLDPID', d['clientcdsldpid']),
		('CDSLCLTID', d['clientcdslcltid']),
		('NSDLDPID', d['clientnsdldpid']),
		('NSDLCLTID', d['clientnsdlcltid']),
		('ACCTYPE_1', d['clientacctype1']),
		('ACCNO_1', d['clientaccno1']),
		('MICRNO_1', d['clientmicrno1']),
		('NEFT/IFSCCODE_1', d['clientifsccode1']),
		('default_bank_flag_1', d['defaultbankflag1']),
		('ACCTYPE_2', d['clientacctype2']),
		('ACCNO_2', d['clientaccno2']),
		('MICRNO_2', d['clientmicrno2']),
		('NEFT/IFSCCODE_2', d['clientifsccode2']),
		('default_bank_flag_2', d['defaultbankflag2']),
		('ACCTYPE_3', d['clientacctype3']),
		('ACCNO_3', d['clientaccno3']),
		('MICRNO_3', d['clientmicrno3']),
		('NEFT/IFSCCODE_3', d['clientifsccode3']),
		('default_bank_flag_3', d['defaultbankflag3']),
		('ACCTYPE_4', d['clientacctype4']),
		('ACCNO_4', d['clientaccno4']),
		('MICRNO_4', d['clientmicrno4']),
		('NEFT/IFSCCODE_4', d['clientifsccode4']),
		('default_bank_flag_4', d['defaultbankflag4']),
		('ACCTYPE_5', d['clientacctype5']),
		('ACCNO_5', d['clientaccno5']),
		('MICRNO_5', d['clientmicrno5']),
		('NEFT/IFSCCODE_5', d['clientifsccode5']),
		('default_bank_flag_5', d['defaultbankflag5']),
		('CHEQUENAME', d['clientchequename5']),
		('ADD1', d['clientadd1'] ),
		('ADD2', d['clientadd2']),
		('ADD3', d['clientadd3']),
		('CITY', d['clientcity']),
		('STATE', d['clientstate']),
		('PINCODE', d['clientpincode']),
		('COUNTRY', d['clientcountry']),
		('RESIPHONE', d['clientresiphone']),
		('RESIFAX', d['clientresifax']),
		('OFFICEPHONE', d['clientofficephone']),
		('OFFICEFAX', d['clientofficefax']),
		('EMAIL', d['clientemail']),
		('COMMMODE',d['clientcommmode']),
		('DIVPAYMODE', d['clientdivpaymode']),
		('PAN2', d['clientpan2']),
		('PAN3', d['clientpan3']),
		('MAPINNO', d['mapinno']),
		('CM_FORADD1', d['cm_foradd1']),
		('CM_FORADD2', d['cm_foradd2']),
		('CM_FORADD3', d['cm_foradd3']),
		('CM_FORCITY', d['cm_forcity']),
		('CM_FORPINCODE', d['cm_forpincode']),
		('CM_FORSTATE', d['cm_forstate']),
		('CM_FORCOUNTRY', d['cm_forcountry']),
		('CM_FORRESIPHONE', d['cm_forresiphone']),
		('CM_FORRESIFAX', d['cm_forresifax']),
		('CM_FOROFFPHONE', d['cm_foroffphone']),
		('CM_FOROFFFAX', d['cm_forofffax']),
		('CM_MOBILE', d['cm_mobile'])
	]

	'''
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
	'''

	# prepare the param field to be returned
	user_param = ''
	for param in param_list:
		user_param = user_param + '|' + str(param[1])
	# print user_param
	return user_param[1:]


# prepare the string that will be sent as param for fatca creation in bse
def prepare_fatca_param(payload):
	'''
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
	'''
	
	# make the list that will be used to create param

	d=payload

	param_list = [
		('PAN_RP', d['pan_rp']),
		('PEKRN', d['pekrn']),
		('INV_NAME', d['inv_name']),
		('DOB', d['dob']),
		('FR_NAME', d['fr_name']),
		('SP_NAME', d['sp_name']),
		('TAX_STATUS', d['tax_status']),
		('DATA_SRC', d['data_src']),
		('ADDR_TYPE', d['addr_type']),
		('PO_BIR_INC', d['po_bir_inc']),
		('CO_BIR_INC', d['co_bir_inc']),
		('TAX_RES1', d['tax_res1']),
		('TPIN1', d['tpin1']),
		('ID1_TYPE', d['id1_type']),
		('TAX_RES2', d['tax_res2']),
		('TPIN2', d['tpin2']),
		('ID2_TYPE', d['id2_type']),
		('TAX_RES3', d['tax_res3']),
		('TPIN3', d['tpin3']),
		('ID3_TYPE', d['id3_type']),
		('TAX_RES4', d['tax_res4']),
		('TPIN4', d['tpin4']),
		('ID4_TYPE', d['id4_type']),
		('SRCE_WEALT', d['srce_wealt']),
		('CORP_SERVS', d['corp_servs']),
		('INC_SLAB', d['inc_slab']),
		('NET_WORTH', d['net_worth']),
		('NW_DATE', d['nw_date']),
		('PEP_FLAG', d['pep_flag']),
		('OCC_CODE', d['occ_code']),
		('OCC_TYPE', d['occ_type']),
		('EXEMP_CODE', d['exemp_code']),
		('FFI_DRNFE', d['ffi_drnfe']),
		('GIIN_NO', d['giin_no']),
		('SPR_ENTITY', d['spr_entity']),
		('GIIN_NA', d['giin_na']),
		('GIIN_EXEMC', d['giin_exemc']),
		('NFFE_CATG', d['nffe_catg']),
		('ACT_NFE_SC', d['act_nfe_sc']),
		('NATURE_BUS', d['nature_bus']),
		('REL_LISTED', d['rel_listed']),
		('EXCH_NAME', d['exch_name']),
		('UBO_APPL', d['ubo_appl']),
		('UBO_COUNT', d['ubo_count']),
		('UBO_NAME', d['ubo_name']),
		('UBO_PAN', d['ubo_pan']),
		('UBO_NATION', d['ubo_nation']),
		('UBO_ADD1', d['ubo_add1']),
		('UBO_ADD2', d['ubo_add2']),
		('UBO_ADD3', d['ubo_add3']),
		('UBO_CITY', d['ubo_city']),
		('UBO_PIN', d['ubo_pin']),
		('UBO_STATE', d['ubo_state']),
		('UBO_CNTRY', d['ubo_cntry']),
		('UBO_ADD_TY', d['ubo_add_ty']),
		('UBO_CTR', d['ubo_ctr']),
		('UBO_TIN', d['ubo_tin']),
		('UBO_ID_TY', d['ubo_id_ty']),
		('UBO_COB', d['ubo_cob']),
		('UBO_DOB', d['ubo_dob']),
		('UBO_GENDER', d['ubo_gender']),
		('UBO_FR_NAM', d['ubo_fr_nam']),
		('UBO_OCC', d['ubo_occ']),
		('UBO_OCC_TY', d['ubo_occ_ty']),
		('UBO_TEL', d['ubo_tel']),
		('UBO_MOBILE', d['ubo_mobile']),
		('UBO_CODE', d['ubo_code']),
		('UBO_HOL_PC', d['ubo_hol_pc']),
		('SDF_FLAG', d['sdf_flag']),
		('UBO_DF', d['ubo_df']),
		('AADHAAR_RP', d['aadhaar_rp']),
		('NEW_CHANGE', d['new_change']),
		('LOG_NAMe',d['log_name']),
		('DOC1', d['filler1']),
		('DOC2', d['filler2'])
	]



	'''
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
	'''
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
		return {'bsesttuscode': response[0], 'bsesttusmsg': response[1],'stcdtoreturn':200}
		
	else:		
		raise Exception(
			"BSE error 644: User creation unsuccessful: %s" % response[1]
		)
		return {'bsesttuscode': response[0], 'bsesttusmsg': response[1],'stcdtoreturn':400}


## fire SOAP query to craete fatca record of user on bsestar
def soap_create_fatca(client, fatca_param, pass_dict):
	method_url = settings.METHOD_UPLOAD_URL[settings.LIVE] + 'MFAPI'
	header_value = soap_set_wsa_headers(method_url, settings.SVC_UPLOAD_URL[settings.LIVE])
	response = client.service.MFAPI(
		'01',
		settings.USERID[settings.LIVE],
		pass_dict['password'],
		fatca_param,
		_soapheaders=[header_value]
	)
	
	## this is a good place to put in a slack alert

	response = response.split('|')
	status = response[0]
	if (status == '100'):
		# Fatca creation successful
		return {'bsesttuscode': response[0], 'bsesttusmsg': response[1],'stcdtoreturn':200}
		
	else:
		raise Exception(
			"BSE error 645: Fatca creation unsuccessful: %s" % response[1]
		)
		return {'bsesttuscode': response[0], 'bsesttusmsg': response[1],'stcdtoreturn':400}

	

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




'''
def custdatavalidation(jsonload):
#Does the validation of the json payload and split them to cust data and fatca data
	print('inside validate and split to cust and fatca data')

	jsonloadcpy=jsonload

		# some fields require processing
	## address field can be 40 chars as per BSE but RTA is truncating it to 30 chars and showing that in account statement which is confusing customers, so reducing the length to 30 chars
	
	
	
	validatedcode['clientcode'] = jsonload.clientcode
	validatedcode['clientholding'] = jsonload.clientholding
	validatedcode['clienttaxstatus'] = jsonload.clienttaxstatus
	validatedcode['clientoccupationcode'] = jsonload.clientoccupationcode
	validatedcode['clientappname1'] = appname1
	validatedcode['clientappname2'] = ''
	validatedcode['clientappname3'] = ''
	validatedcode['clientdob'] = jsonload.clientdob
	validatedcode['clientgender'] = jsonload.clientgender
	validatedcode['clientguardian'] = jsonload.clientguardian
	validatedcode['clientpan'] = jsonload.clientpan
	validatedcode['clientnominee'] = jsonload.clientnominee
	validatedcode['clientnomineerelation'] = jsonload.clientnomineerelation
	validatedcode['clientguardianpan'] = jsonload.clientguardianpan
	validatedcode['clienttype'] = jsonload.clienttype
	validatedcode['clientdefaultdp'] = jsonload.clientdefaultdp
	validatedcode['clientcdsldpid'] = jsonload.clientcdsldpid
	validatedcode['clientcdslcltid'] = jsonload.clientcdslcltid
	validatedcode['clientnsdldpid'] = jsonload.clientnsdldpid
	validatedcode['clientnsdlcltid'] = jsonload.clientnsdlcltid
	validatedcode['clientacctype1'] = jsonload.clientacctype1
	validatedcode['clientaccno1'] = jsonload.clientaccno1
	validatedcode['clientmicrno1'] = jsonload.clientmicrno1
	validatedcode['clientifsccode1'] = jsonload.clientifsccode1
	validatedcode['defaultbankflag1'] = jsonload.defaultbankflag1
	validatedcode['clientacctype2'] = jsonload.clientacctype2
	validatedcode['clientaccno2'] = jsonload.clientaccno2
	validatedcode['clientmicrno2'] = jsonload.clientmicrno2
	validatedcode['clientifsccode2'] = jsonload.clientifsccode2
	validatedcode['defaultbankflag2'] = jsonload.defaultbankflag2
	validatedcode['clientacctype3'] = jsonload.clientacctype3
	validatedcode['clientaccno3'] = jsonload.clientaccno3
	validatedcode['clientmicrno3'] = jsonload.clientmicrno3
	validatedcode['clientifsccode3'] = jsonload.clientifsccode3
	validatedcode['defaultbankflag3'] = jsonload.defaultbankflag3
	validatedcode['clientacctype4'] = jsonload.clientacctype4
	validatedcode['clientaccno4'] = jsonload.clientaccno4
	validatedcode['clientmicrno4'] = jsonload.clientmicrno4
	validatedcode['clientifsccode4'] = jsonload.clientifsccode4
	validatedcode['defaultbankflag4'] = jsonload.defaultbankflag4
	validatedcode['clientacctype5'] = jsonload.clientacctype5
	validatedcode['clientaccno5'] = jsonload.clientaccno5
	validatedcode['clientmicrno5'] = jsonload.clientmicrno5
	validatedcode['clientifsccode5'] = jsonload.clientifsccode5
	validatedcode['defaultbankflag5'] = jsonload.defaultbankflag5
	validatedcode['clientchequename5'] = jsonload.clientchequename5
	validatedcode['clientadd1'] = jsonload.clientadd1
	validatedcode['clientadd2'] = jsonload.clientadd2
	validatedcode['clientadd3'] = jsonload.clientadd3
	validatedcode['clientcity'] = jsonload.clientcity
	validatedcode['clientstate'] = jsonload.clientstate
	validatedcode['clientpincode'] = jsonload.clientpincode
	validatedcode['clientcountry'] = jsonload.clientcountry
	validatedcode['clientresiphone'] = jsonload.clientresiphone
	validatedcode['clientresifax'] = jsonload.clientresifax
	validatedcode['clientofficephone'] = jsonload.clientofficephone
	validatedcode['clientofficefax'] = jsonload.clientofficefax
	validatedcode['clientemail'] = jsonload.clientemail
	validatedcode['clientcommmode'] = jsonload.clientcommmode
	validatedcode['clientdivpaymode'] = jsonload.clientdivpaymode
	validatedcode['clientpan2'] = jsonload.clientpan2
	validatedcode['clientpan3'] = jsonload.clientpan3
	validatedcode['mapinno'] = jsonload.mapinno
	validatedcode['cm_foradd1'] = jsonload.cm_foradd1
	validatedcode['cm_foradd2'] = jsonload.cm_foradd2
	validatedcode['cm_foradd3'] = jsonload.cm_foradd3
	validatedcode['cm_forcity'] = jsonload.cm_forcity
	validatedcode['cm_forpincode'] = jsonload.cm_forpincode
	validatedcode['cm_forstate'] = jsonload.cm_forstate
	validatedcode['cm_forcountry'] = jsonload.cm_forcountry
	validatedcode['cm_forresiphone'] = jsonload.cm_forresiphone
	validatedcode['cm_forresifax'] = jsonload.cm_forresifax
	validatedcode['cm_foroffphone'] = jsonload.cm_foroffphone
	validatedcode['cm_forofffax'] = jsonload.cm_forofffax
	validatedcode['cm_mobile'] = jsonload.cm_mobile

	print(json.loads(validatecode))

	'''
