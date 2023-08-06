import instaloader
import user_agent
import mechanize
import requests
import random
import secrets
import time
import uuid
import json
import os
import re
from user_agent import generate_user_agent
from instaloader import Instaloader
from random import choice
from uuid import uuid4

uid = uuid4()
class instagram:
	def login(username,password):
		url = 'https://i.instagram.com/api/v1/accounts/login/'
		headers = {
			'User-Agent': 'Instagram 113.0.0.39.122 Android (24/5.0; 515dpi; 1440x2416; huawei/google; Nexus 6P; angler; angler; en_US)',
			'Accept': "*/*",
			'Cookie': 'missing',
			'Accept-Encoding': 'gzip, deflate',
			'Accept-Language': 'en-US',
			'X-IG-Capabilities': '3brTvw==',
			'X-IG-Connection-Type': 'WIFI',
			'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
			'Host': 'i.instagram.com'
		}
		data = {
			'uuid': uid,
			'password': password,
			'username': username,
			'device_id': uid,
			'from_reg': 'false',
			'_csrftoken': 'missing',
			'login_attempt_countn': '0'
		}
		req = requests.post(url,headers=headers,data=data).text
		if 'logged_in_user' in req:
			return {'status': 'True', 'message': 'Login True'}
		elif 'check your username' in req:
			return {'status': 'False', 'message': 'Not Found Username'}
		elif 'challenge_required' in req:
			return {'status': 'False', 'message': 'Secure'}
		elif 'Please wait a few minutes' in req:
			return {'status': 'False', 'message': 'Block Ip'}
		else:
			return {'status': 'False', 'message': 'Error'}
	def account(username,password):
		name = "TELEGRAM : @ZERTOOLS"
		hosturl = "https://www.instagram.com/"
		createurl = "https://www.instagram.com/accounts/web_create_ajax/attempt/"
		ageurl = "https://www.instagram.com/web/consent/check_age_eligibility/"
		sendurl = "https://i.instagram.com/api/v1/accounts/send_verify_email/"
		checkcodeurl = "https://i.instagram.com/api/v1/accounts/check_confirmation_code/"
		createacc = "https://www.instagram.com/accounts/web_create_ajax/"
		session = requests.Session()
		session.headers = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36', 'Referer': hosturl}
		session.proxies = {'http': requests.get("https://gimmeproxy.com/api/getProxy").json()['curl']}
		reqB = session.get(hosturl)
		session.headers.update({'X-CSRFToken': reqB.cookies['csrftoken']})
		rem = requests.get("https://10minutemail.net/address.api.php")
		qwe=rem.json()['mail_get_mail'],rem.cookies['PHPSESSID']
		maile=qwe[0]
		mailss=qwe[1]
		data = {'enc_password':'#PWD_INSTAGRAM_BROWSER:0:&:'+password,'email':maile,'username':username,'first_name':name,'client_id':'','seamless_login_enabled':'1','opt_into_one_tap':'false',}
		reg1 = session.post(url=createurl,data=data,allow_redirects=True)
		if (reg1.json()['status'] == 'ok'):
			True
		else:
			return {"result": "False" , "message": "username or password Error"}
		data2 = {'day':'2','month':'2','year':'1983',}
		reqA = session.post(url=ageurl,data=data2,allow_redirects=True)
		if(reqA.json()['status'] == 'ok'):
			True
		else:
			return {"result": "False" , "message": "Error Send Date"}
		sendcode = session.post(url=sendurl,data={'device_id': '','email': maile},allow_redirects=True)
		if(sendcode.json()['status'] == 'ok'):
			True
		else:
			return {"result": "False" , "message": "Error Send Code"}
		while 1:
			rei = requests.get("https://10minutemail.net/address.api.php",cookies={"PHPSESSID":mailss})
			inbox=rei.json()['mail_list'][0]['subject']
			if "Instagram" in inbox:
				code = inbox.split(" is")[0]
				True
				break	 
			else:
				True
				continue
		confirmation = session.post(url=checkcodeurl,data={'code': code,'device_id': '','email': maile})
		if confirmation.json()['status'] == "ok":
			signup_code = confirmation.json()['signup_code']
			True
			create = session.post(
			url=createacc,
			data={
					'enc_password': '#PWD_INSTAGRAM_BROWSER:0:&:'+password,
					'email': maile,
					'username': username,
					'first_name': name,
					'month': '4',
					'day': '4',
					'year': '1963',
					'client_id': '',
					'seamless_login_enabled': '1',
					'tos_version': 'row',
					'force_sign_up_code': signup_code})
			if '"account_created": false' in create.text:
				return {'status': 'False', 'message': 'Username Or Password Error'}
			else:
				return {'status': 'True', 'message': 'True Create', 'data': {'username': f'username', 'password': f'password', 'email': f'maile'}}
		else:
			return {'status': 'False', 'message': 'Error Get SignUp Code'}
	def sessionid(username,password):
		uid = uuid4()
		url = 'https://i.instagram.com/api/v1/accounts/login/'
		headers = {
			'User-Agent' : 'Instagram 113.0.0.39.122 Android (24/5.0; 515dpi; 1440x2416; huawei/google; Nexus 6P; angler; angler; en_US)',  'Accept':'*/*',
			'Cookie':'missing',
			'Accept-Encoding':'gzip, deflate',
			'Accept-Language':'en-US',
			'X-IG-Capabilities':'3brTvw==',
			'X-IG-Connection-Type':'WIFI',
			'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
			'Host':'i.instagram.com'
		}
		data = {
			'uuid':uid,
			'password':password,
			'username':username,
			'device_id':uid,
			'from_reg':'false',
			'_csrftoken':'missing',
			'login_attempt_countn':'0'
		}
		req_login = requests.post(url, headers=headers, data=data)
		if 'logged_in_user' in req_login.text:
			get_sessions = req_login.cookies["sessionid"]
			sessionid = get_sessions.split('%3AA')[0]
			return sessionid
		elif 'check your username' in req_login.text:
			return {'status': 'False', 'message': 'Not Found Username'}
		elif 'challenge_required' in req_login.text:
			return {'status': 'False', 'message': 'Secure'}
		elif 'Please wait a few minutes' in req_login.text:
			return {'status': 'False', 'message': 'Block Ip'}
		elif '"user":true,"authenticated":false' in req_login.text:
			return {'status': 'False', 'message': 'Worng Password !'}
		elif '"authenticated":false,' in req_login.text:
			return {'status': 'False', 'message': 'Worng Username or Password !'}
		else:
			return {'status': 'False', 'message': 'Error'}
	def login_sessionid(session):
		url = "https://i.instagram.com/api/v1/accounts/current_user/?edit=true"
		headers = {
			'X-IG-Connection-Type': 'WIFI',
			'X-IG-Capabilities': '3brTBw==',
			'User-Agent': str(generate_user_agent()),
			'Accept-Language': 'en-US',
			 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
			'Accept-Encoding': 'gzip, deflate',
			'Host': 'i.instagram.com',
			'Connection': 'keep-alive',
			'Accept': '*/*'}
		cookies = {"sessionid": str(session)}
		res = requests.post(url, headers=headers, cookies=cookies).json()
		if str('message') in res:
			return {'status': 'False', 'message': 'False Sessionid'}
		else:
			return {'status': 'Success', 'message': 'Login True', 'Sessionid': session}
	def send_email(username):
		uid = uuid4()
		url1 = "https://i.instagram.com/api/v1/accounts/send_recovery_flow_email/"
		headers1 = {
			'X-Ig-Www-Claim': '0',
			'X-Ig-Connection-Type': 'WIFI',
			'X-Ig-Capabilities': '3brTv10=',
			'X-Ig-App-Id': '567067343352427',
			'User-Agent': 'Instagram 219.0.0.12.117 Android (25/7.1.2; 240dpi; 1280x720; samsung; SM-G977N; beyond1q; qcom; en_US; 346138365)',
			'Accept-Language': 'en-US',
			'X-Mid': 'YjKpKwABAAEBChfhQ0jDY79zjPt4',
			'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
			'Content-Length': '674',
			'Accept-Encoding': 'gzip, deflate'
		}
		data1 = {
			"adid": uid,
			"query": str(username),
			"guid": uid,
			"device_id": uid,
			"waterfall_id": uid
		}
		req1 = requests.post(url=url1, headers=headers1, data=data1)
		if "email" in req1.text:
			email = req1.json()["email"]
			return {'status': 'True', 'message': f'Done Send Rest to {email}'}
	def send_phone(username):
		uid = uuid4()
		url2 = "https://i.instagram.com/api/v1/users/lookup_phone/"
		headers2 = {
			'X-Ig-Www-Claim': '0',
			'X-Ig-Connection-Type': 'WIFI',
			'X-Ig-Capabilities': '3brTv10=',
			'X-Ig-App-Id': '567067343352427',
			'User-Agent': 'Instagram 219.0.0.12.117 Android (25/7.1.2; 240dpi; 1280x720; samsung; SM-G977N; beyond1q; qcom; en_US; 346138365)',
			'Accept-Language': 'en-US',
			'X-Mid': 'YjKpKwABAAEBChfhQ0jDY79zjPt4',
			'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
			'Content-Length': '674',
			'Accept-Encoding': 'gzip, deflate'
		}
		data2 = {
			"supports_sms_code": "true",
			"guid": uid,
			"device_id": uid,
			"query": str(username),
			"android_build_type": "release",
			"waterfall_id": uid,
			"use_whatsapp": "false"
		}
		req2 = requesrs.post(url=url2, headers=headers2, data=data2)
		if "phone_number" in req2.text:
		      phone = req2.json()["phone_number"]
		      return {'status': 'True', 'message': f'Done Send Rest to {phone}'}
	def rest(user):
		global username
		username = user
		if username[0] == '@':
			return {'status': 'False', 'message': 'False Username'}
		url = "https://i.instagram.com/api/v1/users/lookup/"
		headers = {
			'X-Ig-Www-Claim': '0',
			'X-Ig-Connection-Type': 'WIFI',
			'X-Ig-Capabilities': '3brTv10=',
			'X-Ig-App-Id': '567067343352427',
			'User-Agent': 'Instagram 219.0.0.12.117 Android (25/7.1.2; 240dpi; 1280x720; samsung; SM-G977N; beyond1q; qcom; en_US; 346138365)',
			'Accept-Language': 'en-US',
			'X-Mid': 'YjKpKwABAAEBChfhQ0jDY79zjPt4',
			'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
			'Content-Length': '674',
			'Accept-Encoding': 'gzip, deflate'
		}
		data = {
			"phone_id": uid,
			"q": username,
			"guid": uid,
			"device_id": uid,
			"android_build_type": "release",
			"waterfall_id": uid,
			"directly_sign_in": "true",
			"is_wa_installed": "false"
		}
		req = requests.post(url=url, headers=headers, data=data)
		try:
			if '"user":{"pk"' not in req.text:
				user_id = req.json()["user"]["pk"]
				return {'status':'False', 'message':'Username Not Found'}
			elif '"can_email_reset":true' and '"can_sms_reset":true' in req.text:
				c = input("{'status':'True', 'message':'Send Rest To Gmail Enter 1', 'message': 'message':'Send Rest To Phone Number Enter 2', 'Enter': ")
				if c == "1":
					return instagram.send_email(username)
				elif c == "2":
					return instagram.send_phone(username)
			elif '"can_email_reset":true' in req.text:
				return instagram.send_email(username)
			elif '"can_sms_reset":true' in req.text:
				return instagram.send_phone(username)
			else:
				return {'status': 'False', 'message': 'False'}
		except:
			return {'status': 'False', 'message': 'Please wait a few minutes before you try again.'}
	def gmail(email):
		user = email.split('@gmail.com')[0]
		url = 'https://android.clients.google.com/setup/checkavail'
		headers = {
		'Content-Length':'98',
		'Content-Type':'text/plain; charset=UTF-8',
		'Host':'android.clients.google.com',
		'Connection':'Keep-Alive',
		'user-agent':'GoogleLoginService/1.3(m0 JSS15J)',}
		data = json.dumps({
		'username':str(email),
		'version':'3',
		'firstName':'ZERTOOLS',
		'lastName':'@ZERTOOLS' })
		res = requests.post(url,data=data,headers=headers)
		if res.json()['status'] == 'SUCCESS':
			return f'+ AVAILABLE ACCOUNT :\n+ GMAIL : {email}\n+ USERNAME : {user}\n+ BY : @ZERTOOLS'
		else:			
			return f'- NOT AVAILABLE GMAIL : {email}'
	def check(email):
		user = email.split('@gmail.com')[0]
		uid = uuid4()
		url = 'https://i.instagram.com/api/v1/accounts/login/'
		headers = {
			'User-Agent':'Instagram 113.0.0.39.122 Android (24/5.0; 515dpi; 1440x2416; huawei/google; Nexus 6P; angler; angler; en_US)',  'Accept':'*/*',
			'Cookie':'missing',
			'Accept-Encoding':'gzip, deflate',
			'Accept-Language':'en-US',
			'X-IG-Capabilities':'3brTvw==',
			'X-IG-Connection-Type':'WIFI',
			'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
			'Host':'i.instagram.com'
		}
		data = {
			'uuid':uid,
			'password':'@ZERTOOLS',
			'username':user,
			'device_id':uid,
			'from_reg':'false',
			'_csrftoken':'missing',
			'login_attempt_countn':'0'
		}
		req = requests.post(url, headers=headers, data=data).json()
		if req['message'] == 'The password you entered is incorrect. Please try again.':
			return f'+ AVAILABLE ACCOUNT IN INSTAGRAM : {email}'
		else:
			return f'- NOT AVAILABLE INSTAGRAM : {email}'
	def info(username):
		L = instaloader.Instaloader()
		profile = instaloader.Profile.from_username(L.context, username)
		followers = profile.followers
		following = profile.followees
		id = profile.userid
		iok = requests.get(f"https://o7aa.pythonanywhere.com/?id={id}").json()
		data = str(iok['data'])
		return f'+ USERNAME : {username}\n+ FOLLOWERS : {followers}\n+ FOLLOWING : {following}\n+ ID : {id}\n+ DATA : {data}\n+ TELEGRAM : @ZERTOOLS'

class email:
	def gmail(email):
		url = 'https://android.clients.google.com/setup/checkavail'
		headers = {
		'Content-Length':'98',
		'Content-Type':'text/plain; charset=UTF-8',
		'Host':'android.clients.google.com',
		'Connection':'Keep-Alive',
		'user-agent':'GoogleLoginService/1.3(m0 JSS15J)',}
		data = json.dumps({
		'username':str(email),
		'version':'3',
		'firstName':'ZERTOOLS',
		'lastName':'@ZERTOOLS' })
		req = requests.post(url,data=data,headers=headers)
		if req.json()['status'] == 'SUCCESS':
			return {'status': 'True' , 'message': {'data': {'email': f'{email}'}}}
		else:			
			return {'status': 'False' , 'message': 'Not Available'}
	def hotmail(email):
		url = "https://odc.officeapps.live.com/odc/emailhrd/getidp?hm=0&emailAddress="+str(email)+"&_=1604288577990"	
		headers = {
		"Accept": "*/*",
		"Content-Type": "application/x-www-form-urlencoded",
		"User-Agent": (generate_user_agent()),
		"Connection": "close",
		"Host": "odc.officeapps.live.com",
		"Accept-Encoding": "gzip, deflate",
		"Referer": "https://odc.officeapps.live.com/odc/v2.0/hrd?rs=ar-sa&Ver=16&app=23&p=6&hm=0",
		"Accept-Language": "ar,en-US;q=0.9,en;q=0.8",
		"canary": "BCfKjqOECfmW44Z3Ca7vFrgp9j3V8GQHKh6NnEESrE13SEY/4jyexVZ4Yi8CjAmQtj2uPFZjPt1jjwp8O5MXQ5GelodAON4Jo11skSWTQRzz6nMVUHqa8t1kVadhXFeFk5AsckPKs8yXhk7k4Sdb5jUSpgjQtU2Ydt1wgf3HEwB1VQr+iShzRD0R6C0zHNwmHRnIatjfk0QJpOFHl2zH3uGtioL4SSusd2CO8l4XcCClKmeHJS8U3uyIMJQ8L+tb:2:3c",
		"uaid": "d06e1498e7ed4def9078bd46883f187b",
		"Cookie": "xid=d491738a-bb3d-4bd6-b6ba-f22f032d6e67&&RD00155D6F8815&354"}	
		req = requests.post(url, data="", headers=headers).text
		if "Neither" in req:		
			return {'status': 'True' , 'message': {'data': {'email': f'{email}'}}}
		else:			
			return {'status': 'False' , 'message': 'Not Available'}
	def outlook(email):
		url = "https://odc.officeapps.live.com/odc/emailhrd/getidp?hm=0&emailAddress="+str(email)+"&_=1604288577990"	
		headers = {
		"Accept": "*/*",
		"Content-Type": "application/x-www-form-urlencoded",
		"User-Agent": (generate_user_agent()),
		"Connection": "close",
		"Host": "odc.officeapps.live.com",
		"Accept-Encoding": "gzip, deflate",
		"Referer": "https://odc.officeapps.live.com/odc/v2.0/hrd?rs=ar-sa&Ver=16&app=23&p=6&hm=0",
		"Accept-Language": "ar,en-US;q=0.9,en;q=0.8",
		"canary": "BCfKjqOECfmW44Z3Ca7vFrgp9j3V8GQHKh6NnEESrE13SEY/4jyexVZ4Yi8CjAmQtj2uPFZjPt1jjwp8O5MXQ5GelodAON4Jo11skSWTQRzz6nMVUHqa8t1kVadhXFeFk5AsckPKs8yXhk7k4Sdb5jUSpgjQtU2Ydt1wgf3HEwB1VQr+iShzRD0R6C0zHNwmHRnIatjfk0QJpOFHl2zH3uGtioL4SSusd2CO8l4XcCClKmeHJS8U3uyIMJQ8L+tb:2:3c",
		"uaid": "d06e1498e7ed4def9078bd46883f187b",
		"Cookie": "xid=d491738a-bb3d-4bd6-b6ba-f22f032d6e67&&RD00155D6F8815&354"}
		req = requests.post(url, data="", headers=headers).text
		if "Neither" in req:		
			return {'status': 'True' , 'message': {'data': {'email': f'{email}'}}}
		else:
			return {'status': 'False' , 'message': 'Not Available'}
	def mailru(email):
		url = "https://account.mail.ru/api/v1/user/exists"		
		headers = {
		"User-Agent": (generate_user_agent())}
		data = {'email': str(email)}
		req = requests.post(url, data=data, headers=headers)		
		if str(req.json()['body']['exists']) == False:
			return {'result': 'True' , 'message': "Successful" , 'data': {"email": email}}
		else:
			return {'result': 'False' , 'message': 'Error'}
	def yahoo(email):
		email = str(email)
		email = email.split('@')[0]
		url = "https://login.yahoo.com/account/module/create?validateField=userId"
		headers = {
		'accept': '*/*',
		'accept-encoding': 'gzip, deflate, br',
		'accept-language': 'ar,en-US;q=0.9,en;q=0.8',
		'content-length': '7423',
		'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
		'cookie': 'PH=l=en-JO; cmp=t=1649967133&j=0; OTH=v=1&d=eyJraWQiOiIwMTY0MGY5MDNhMjRlMWMxZjA5N2ViZGEyZDA5YjE5NmM5ZGUzZWQ5IiwiYWxnIjoiUlMyNTYifQ.eyJjdSI6eyJndWlkIjoiUVM0Uk1FNVM1NTdEQlg2TTdOVFFRUTdHTlUiLCJwZXJzaXN0ZW50Ijp0cnVlLCJzaWQiOiJERWI2ZmRZN1BwQVUifX0.qS4v0LTtpXd4vhydwS6vpL9MANSOMDMZEYWffFSxshbnuwRCzeUzJbwM2p7nPMwYV96yEFCkM0B8Lo--XHoBQvQszdP_-M-HuzLttwUwkzkqDpZyo6Lzm5bAnbh6B3P-kTcNBHlCoSg9N-SExB0OrppOO2gONQqoR25mLHXhhnY; A1=d=AQABBB409GECEJnQ0nfMctyiH6Cq-PmrCeMFEgEABgLQWWIzY2Jcb2UB_eMBAAcIHjT0YfmrCeMID9DBO57ZmNoDBDj1XbSi9wkBBwoB3w&S=AQAAAjb2LJb55ay2ij3P5hQhTG8; A3=d=AQABBB409GECEJnQ0nfMctyiH6Cq-PmrCeMFEgEABgLQWWIzY2Jcb2UB_eMBAAcIHjT0YfmrCeMID9DBO57ZmNoDBDj1XbSi9wkBBwoB3w&S=AQAAAjb2LJb55ay2ij3P5hQhTG8; B=e62dbv5gv8d0u&b=4&d=6ZQJIRhtYFgpJyr7JyZD&s=1a&i=0ME7ntmY2gMEOPVdtKL3; GUC=AQEABgJiWdBjM0Id8gRd; FS=v=1&d=Sloq608oHDIvM2JuXcI4Gn9LK3_mICxQM3wH9IpTUuhixjO_VCNu~A; F=d=Gd70Kyk9vQ--; A1S=d=AQABBB409GECEJnQ0nfMctyiH6Cq-PmrCeMFEgEABgLQWWIzY2Jcb2UB_eMBAAcIHjT0YfmrCeMID9DBO57ZmNoDBDj1XbSi9wkBBwoB3w&S=AQAAAjb2LJb55ay2ij3P5hQhTG8&j=WORLD; AS=v=1&s=Cgvhb3Xg&d=A627bc5c4|SI2GnZf.2Sr3BNg89zpo_CsNpKuGFl4HUY7VHVfbraWyc8Ii93qDVlDfOt1BfiR7XCEZ21NvQDWrQraqbYJyOJYpsIH0OvCsxXiN8AGzuKcqHrgfGUtOZZrzS7O.VkvbdCiSNYD_w9OB6ML3Y8NMOiMYT_MiAgefNsF_54dXFyJdm4rdq1W.bJhN_PLPvnrKNDEd7saaFV3TnLk.b.kYolEgMoWWAkD71Of5UCjkqQNaQk8RIunPxxXkRXHZwr1ypRWsnBEuqv5oQrEDCiqHFvF8u25Ofg2gKdnPDbFeJ9RleaTB45uuY5sZUv1mdsokSKD6_ahRvGkWfTnrPZzt6E28PE28s0fooo2qY3yUltuO1w.xKUCKkKbWJQyjxXpqTm3hgOwJ66.3I2TIf5r0vA0r43pnZVLl2rttIk4R1ABgy9Wy7OOqga8ZVE3o1l0hHz419cDgN1Hzb0Fexz..nP9ME4F7VWfn8oo.k9pMZYDtHhRMM1kGGmsex0pBbD.QdtUhpuVR4oHP_U7ap4DOcKCGYp2XVml6Z.9xRcb3m_VOukhZ1zwEpcjT6xXJAjZ7AgfC3l7QBLw2NnD0Mtuqh35qDDEABh4dM.YlhgT72EYqSbl8MnvZ7W1q0bk3SMaqQdwbAGle4W1j_uPr0yu90HSPNKzeQ2K5GsPumTtVNzT353rVPBfwGAIDMe1wqR5csd8SV4iFjZ8Y6r..RZT_XsKxT2JOL1QhaTFkx0INLwy88kv._Vv_cBMwcEYUz0LQ9OLwajl6R7b5AYwwk.B4EXpf7DzynJaWtaerDs461oLGbqD_ljVUdWAy.U5mcYXnWqzqseI7fC6W4HvXdAaCIC2qmrAgjow9hJqXDIvkXODlsrZ.usoNnX44L7X8ybtYCKvH4RcQttBv6b0X2jcI~A|B627bc602|8.xHz7z.2TpHZLxVO1hodGUaeVUeU4gERiIt7J2uXM7cv4.YcovtTNaxgcIeRQzeGiqrbxcu1WyDHogAGcIglonu5OSTNDoMeCDAxtZH1Od166YwYdZDIzr0hcNc_epXkOw1KoLhXbyBR5MCTGhdrG0BJoG5njJC9n5N2JJx2P0aWBC9bPoIThLWGi9Wf8wfI4MP3mhqA9lF2eFUkQEX6A2CiocpPLhQbmtgRKbVM1Q3ncBSeVaKuhQOqNcvHOqCSLgppcJg2sBtkJLzet12UCSy8JORfHf6Dc3DMT8QgifRRoGTBoAGs_SOI6hOcNExCo9D5ImvN.lKHPMymFxqnW4pVaq2PBcY7f2t4xNLcqBYPV.O2TCmgvni7WYaq7A0zYaQCJWFcBkzB4BcXX19s8Eeidj213exUfkBq8zgrPQsB0IPQD0KCe.LXf6hNY1dr4vp1rTBLRchdHhzbM2upz50JIDW87taVyq.ZU04zTTOg4KQwv9Hn9poWN_Y2VeiU68nclbo60iQRPXCa5mqucblBHNAxUHuGNiUlD5xYj3N2W.oiUMs7_9esA3eOUubDjN8vj_FAqE9IKrJqNiyOkWOniHFTJ77toR.uk1PW8Bo21lZocUzsa1s9WdzLC5HusiiMErYDEnMdRIyu8_.ZxCeKhvNbi8cbSI3.ZentJbZMr1y5sZrarxJCGi1OGoUBEuHWbaZsRASqKJMiX4I95kvg.aFU6XlIQCbKbVyJPCnf7lMb0bEsP6oYnEiqlME_r8ejtGRi9Nu1vgt5HvJaEjwOlYHZnmO21kqttxWUkhORs_He7F81_HHtWVAez1R6a2WP3qh1MT14ppKSBr6851gallOGB0AJOi2P.9vJaPSwzunhCFzWdpgLH9rx4LTKgseKH1NLyrsvKnmf.AMPdYnZR1NBJSvBJ9kknOWSXWyNFcfOgVyUaHzJKMG.QF.JC3DqEcIsJCW7w12wCyb422YcTwgWhUK1I19S8w9HjhiYg--~A',
		'origin': 'https://login.yahoo.com',
		'referer': 'https://login.yahoo.com/account/create?.intl=xa&.lang=ar&src=ym&specId=yidregsimplified&activity=mail-direct&pspid=959521375&.done=https%3A%2F%2Fmail.yahoo.com%2Fm%2F%3F.intl%3Dxa%26.lang%3Dar&done=https%3A%2F%2Fmail.yahoo.com%2Fm%2F%3F.intl%3Dxa%26.lang%3Dar&intl=xa&context=reg',
		'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
		'sec-ch-ua-mobile': '?0',
		'sec-ch-ua-platform': '"Windows"',
		'sec-fetch-dest': 'empty',
		'sec-fetch-mode': 'cors',
		'sec-fetch-site': 'same-origin',
		'user-agent': (generate_user_agent()),}		
		data = {
	    'browser-fp-data': '{"language":"ar","colorDepth":24,"deviceMemory":4,"pixelRatio":1,"hardwareConcurrency":4,"timezoneOffset":-180,"timezone":"Asia/Riyadh","sessionStorage":1,"localStorage":1,"indexedDb":1,"openDatabase":1,"cpuClass":"unknown","platform":"Win32","doNotTrack":"unknown","plugins":{"count":5,"hash":"2c14024bf8584c3f7f63f24ea490e812"},"canvas":"canvas winding:yes~canvas","webgl":1,"webglVendorAndRenderer":"Google Inc. (Intel)~ANGLE (Intel, Intel(R) HD Graphics 4600 Direct3D11 vs_5_0 ps_5_0, D3D11)","adBlock":0,"hasLiedLanguages":0,"hasLiedResolution":0,"hasLiedOs":0,"hasLiedBrowser":0,"touchSupport":{"points":0,"event":0,"start":0},"fonts":{"count":48,"hash":"62d5bbf307ed9e959ad3d5ad6ccd3951"},"audio":"124.04347527516074","resolution":{"w":"1366","h":"768"},"availableResolution":{"w":"728","h":"1366"},"ts":{"serve":1652192386973,"render":1652192386434}}',
	    'specId': 'yidregsimplified',
	    'crumb': 'IHW88p4nwpv',
	    'acrumb': 'Cgvhb3Xg',
	    'userid-domain': 'yahoo',
	    'userId': (email),
	    'password': '@DHTools',}		
		req = requests.post(url,headers=headers,data=data).text 	
		if "userId" in req:	
			return {'status': 'False' , 'message': 'Not Available'}
		else:		
			return {'status': 'True' , 'message': {'data': {'email': f'{email}'}}}
	def aol(email):
		email = str(email)
		email = email.split('@')[0]
		url = 'https://login.aol.com/account/module/create?validateField=yid'	
		headers = {
		'accept': '*/*',
		'accept-encoding': 'gzip, deflate, br',
		'accept-language': 'ar,en-US;q=0.9,en;q=0.8',
		'content-length': '18023',
		'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
		'cookie': 'A1=d=AQABBGBeeWICEBR5epkCARe46kFw6ViOQ_AFEgEBAQGvemKDYgAAAAAA_eMAAA&S=AQAAAp3JQ6CyW2qRJcMsBzHGVvU; A3=d=AQABBGBeeWICEBR5epkCARe46kFw6ViOQ_AFEgEBAQGvemKDYgAAAAAA_eMAAA&S=AQAAAp3JQ6CyW2qRJcMsBzHGVvU; A1S=d=AQABBGBeeWICEBR5epkCARe46kFw6ViOQ_AFEgEBAQGvemKDYgAAAAAA_eMAAA&S=AQAAAp3JQ6CyW2qRJcMsBzHGVvU&j=WORLD; GUC=AQEBAQFieq9ig0IfzwR5; rxx=2bkczirpbih.2q6rpdsb&v=1; AS=v=1&s=JYNxcuAB&d=A627ab0eb|5n7NNlX.2Tqja_1ZC6lprFtAflUVdSswdgLRxIPQFqE9yPLfNXNQGllEgjcaz2MSyNOF0HA9XirM0hGhPu6hRyuyv6NS5uzzU2MRaRQf.1YBAQ8FypG1m_xQXAtuSInDrAwsMOptRW4zfkTgorDT4mTAhLg6RTvtz.RlGfCdtaQ4BBDOfp7jAYaYk.VJlzoY75HEqitjywIRo5cxa2LE6o5SUyxNOi7S_X3k_SPXAVdV.Pie3M8oZSqscWmfYaFDf586bpqdXlRbtd9NfqqCnsm39F_qAPBPvWHWieu4eZ4Guhk.MRMp7Daew_rlTFks0DO5LZYOCyO3RrW3LO3QaHRTvTBTaXP4RsdfXTOXPejofBwqmWSbUlACa4xD1EKndabLWQmEoy1AEUMoSbwgJMxI_j7xuQHqBgjCanjm8A6GOXCZKM44DjwdQdaMnR6GrHEfBfKds9z.7gjHKBoZ2jkWj7Hk7hPMzDGRBkqU.TWCGZRumYVYV8blYxEIS.H9qySKbh3SBBI8MIgkMqBNciHX3QnqQrc_CuA1uBOx7GHKgnI7pemzJnVMGwyYsAGU4UQRwAVGcDrHZH76hH..grS5ceMIZJSVt6nAcvYiTMElRUgLqk4RORTkyF9XbLMB9_U2I_ZVaERHP3X7j7f77RdHq2UlR68eZ_G5RY6ZrgfwFvy1Ptrd9WdFYaab69sfGI8SVXk2dtdR5udVorhaBdtoNxJ5PIy0Ue_qMPhxcsw4VzSExlyyNSaF0SFoSH5fK8kFVQ0IIBIWO_d0ik6d9azkHxffaa7MJpjYfsHmHpERb2hEkyr7uJzTQTf0H8NBfQdcQD8P9ja69DD7Ahdacge_a9D4QGaLgMvQi481iZMNd5Dy46uoeco5T.slB_psK4WxbBJgP7p6hgyb_wkDzvUhd_3ym5sQe1cBySzHgXSMyzsEurBQZKaMHv9302Cj6iNUZ2jjtMkAVdsh~A|B627ab2cd|x0gk8rH.2TpbbztShpG57nIccQOKaEGxqulmFIimnSbIetxQBy35pQAyeLh0g4kZXfUcZ8gS0KtJhnntdd169n74ag_k2YnldeTcAixJ8Oe1U9eEwr4TEKjAn5ew0omTSMojewjLD76vbkEv.zZYyCrRxd5vfs3vmQxAV_f6Y0sOWtsUeIu3OvEzUyK.1trUfGvmn7d3hvyFbF.OTRqd._NMsXRn2QVZ.T5RjYrog5983WaKy_9x1YPoBUNH4QPKi0zZBP9iMgx8Tlsrxhn4zs9Zyr3IiqPFbxjEuBh4G78xoEv7z6_PrYOwB37XEbTdaaeXyPFsSGhZf4bQovQopXVbHe.9nbDzDYkfdXD6d9wmf6jvSEex9a9eEu8Z.14NuIQZJcy_c6_PP5H0eXQAWO6LOsW7CtqdeDlLd74M9jUU5yseMxzkN0HSawwGQ.HU.XZFjoOjowHAX1bsDGRuWObSamI1LdvanTCHZZ6TICNO8lT9GjBWDYK.h6.ojgs.tCAAXzYPMf6UOHvrjtlwaCmODGFlndZMASPIp9IyDMRT9gC52spPRpBQJZOpJUt8YDEY6zKB5r2SsHH.ssGgtrnS3tlCg6rx8k.wEakhoSpj2ezEMO4IAODDXV0paODum6McXkpaxliXReHLYdtXIM9t5smt_PeP92ttd69oDB.zVFsEms7tdF1SQWbmUF.4plddWEwfn6FNVdj7TpJvpTAxjaso_xliccUrnkpUGvH1IUv11w4Pok0k92JLzk2AXJ5Ak_5R51n2X_Oc88nJKif3EZK7ly7lgMXtWaURJx2Zj4.88SxdyHNtRzmHFvkAwmxtDmjgj5OCF7m38h.4TZuT3.D3c7uhs0XPEZARricsnApvw1dUBRY0E3vvSU.S_4zHPhWn7BHQz1nySvei.tQaogRmeBpFHvzS3QNKSWksRu1w7T8O2RDtnr7pzs5VzPifkiXOKw--~A',
		'origin': 'https://login.aol.com',
		'referer': 'https://login.aol.com/account/module/create?validateField=yid%5C',
		'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
		'sec-ch-ua-mobile': '?0',
		'sec-ch-ua-platform': '"Windows"',
		'sec-fetch-dest': 'empty',
		'sec-fetch-mode': 'cors',
		'sec-fetch-site': 'same-origin',
		'user-agent': (generate_user_agent()),
		'x-requested-with': 'XMLHttpRequest',}
		data = {
		'browser-fp-data': '{"language":"ar","colorDepth":24,"deviceMemory":4,"pixelRatio":1,"hardwareConcurrency":4,"timezoneOffset":-180,"timezone":"Asia/Riyadh","sessionStorage":1,"localStorage":1,"indexedDb":1,"openDatabase":1,"cpuClass":"unknown","platform":"Win32","doNotTrack":"unknown","plugins":{"count":5,"hash":"2c14024bf8584c3f7f63f24ea490e812"},"canvas":"canvas winding:yes~canvas","webgl":1,"webglVendorAndRenderer":"Google Inc. (Intel)~ANGLE (Intel, Intel(R) HD Graphics 4600 Direct3D11 vs_5_0 ps_5_0, D3D11)","adBlock":0,"hasLiedLanguages":0,"hasLiedResolution":0,"hasLiedOs":0,"hasLiedBrowser":0,"touchSupport":{"points":0,"event":0,"start":0},"fonts":{"count":48,"hash":"62d5bbf307ed9e959ad3d5ad6ccd3951"},"audio":"124.04347527516074","resolution":{"w":"1366","h":"768"},"availableResolution":{"w":"728","h":"1366"},"ts":{"serve":1652124464147,"render":1652124464497}}',
		'specId': 'yidReg',
		'crumb': 'YLO.LxuwQbD',
		'acrumb': 'JYNxcuAB',
		'done': 'https://www.aol.com',
		'tos0': 'oath_freereg|us|en-US',
		'yid': (email),
		'password': '@DHTools',
		'shortCountryCode': 'US'}
		req = requests.post(url,headers=headers,data=data).text 	
		if '"yid"' in req:			
			return {'status': 'False' , 'message': 'Not Available'}
		else:			
			return {'status': 'True' , 'message': {'data': {'email': f'{email}'}}}
	def twiter(email):
		rs = requests.Session()
		url = f"https://api.twitter.com/i/users/email_available.json?email={email}"
		rs.headers = {
		'User-Agent': generate_user_agent(),
		'Host':"api.twitter.com",
		'Accept':"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",}
		res = rs.get(url).json()
		if res['valid'] == True:
			return {'status': 'True' , 'message': {'data': {'email': f'{email}'}}}
		else:
			return {'status': 'False' , 'message': 'Not Available'}

class login:
	def instagram(username, password):
		uid = uuid4()
		url = 'https://i.instagram.com/api/v1/accounts/login/'
		headers = {
			'User-Agent' : 'Instagram 113.0.0.39.122 Android (24/5.0; 515dpi; 1440x2416; huawei/google; Nexus 6P; angler; angler; en_US)',  'Accept':'*/*',
			'Cookie':'missing',
			'Accept-Encoding':'gzip, deflate',
			'Accept-Language':'en-US',
			'X-IG-Capabilities':'3brTvw==',
			'X-IG-Connection-Type':'WIFI',
			'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
			'Host':'i.instagram.com'
		}
		data = {
			'uuid':uid,
			'password':password,
			'username':username,
			'device_id':uid,
			'from_reg':'false',
			'_csrftoken':'missing',
			'login_attempt_countn':'0'
		}
		req_login = requests.post(url, headers=headers, data=data)
		if 'logged_in_user' in req_login.text:
			return {'status': 'True', 'message': 'Login True'}
		elif 'check your username' in req_login.text:
			return {'status': 'False', 'message': 'Not Found Username'}
		elif 'challenge_required' in req_login.text:
			return {'status': 'False', 'message': 'Secure'}
		elif 'Please wait a few minutes' in req_login.text:
			return {'status': 'False', 'message': 'Block Ip'}
		else:
			return {'status': 'False', 'message': 'Error'}
	def facebook(email,password):
		url = "https://b-graph.facebook.com/auth/login"
		headers = {
		"authorization": "OAuth 200424423651082|2a9918c6bcd75b94cefcbb5635c6ad16",
		"user-agent": "Dalvik/2.1.0 (Linux; U; Android 10; BLA-L29 Build/HUAWEIBLA-L29S) [FBAN/MessengerLite;FBAV/305.0.0.7.106;FBPN/com.facebook.mlite;FBLC/ar_PS;FBBV/372376702;FBCR/Ooredoo;FBMF/HUAWEI;FBBD/HUAWEI;FBDV/BLA-L29;FBSV/10;FBCA/arm64-v8a:null;FBDM/{density=3.0,width=1080,height=2040};]"}
		data = f"email={email}&password={password}&credentials_type=password&error_detail_type=button_with_disabled&format=json&device_id={uuid.uuid4()}&generate_session_cookies=1&generate_analytics_claim=1&generate_machine_id=1&method=POST"
		res = requests.post(url, data=data, headers=headers).json()
		if list(res)[0] == "session_key":
			return {'status': 'True', 'message': 'True Login', 'data': {'secret': res["secret"] , 'id': res["uid"] , 'access_token': res["access_token"]}}
		else:
			try:
				return {'status': 'False', 'message': res["error"]["error_user_title"]}
			except:
				return {'status': 'False'}
	def twiter(username,password):
		url = 'https://twitter.com/sessions'			
		headers = {
		    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
		    'Accept-Encoding': 'gzip, deflate, br',
		    'Accept-Language': 'ar,en-US;q=0.7,en;q=0.3',
		    'Content-Length': '901',
		    'Content-Type': 'application/x-www-form-urlencoded',
		    'Host': 'twitter.com',
		    'Origin': 'https://twitter.com',
		    'Referer': 'https://twitter.com/login?lang=ar',
		    'TE': 'Trailers',
		    'Upgrade-Insecure-Requests': '1',
		    'User-Agent': generate_user_agent()}	
		data = {
		    'redirect_after_login': '/',
		    'remember_me': '1',
		    'authenticity_token': '10908ac0975311eb868c135992f7d397',
		    'wfa': '1',
		    'ui_metrics': '{\"rf\":{\"ab4c9cdc2d5d097a5b2ccee53072aff6d2b5b13f71cef1a233ff378523d85df3\":1,\"a51091a0c1e2864360d289e822acd0aa011b3c4cabba8a9bb010341e5f31c2d2\":84,\"a8d0bb821f997487272cd2b3121307ff1e2e13576a153c3ba61aab86c3064650\":-1,\"aecae417e3f9939c1163cbe2bde001c0484c0aa326b8aa3d2143e3a5038a00f9\":84},\"s\":\"MwhiG0C4XblDIuWnq4rc5-Ua8dvIM0Z5pOdEjuEZhWsl90uNoC_UbskKKH7nds_Qdv8yCm9Np0hTMJEaLH8ngeOQc5G9TA0q__LH7_UyHq8ZpV2ZyoY7FLtB-1-Vcv6gKo40yLb4XslpzJwMsnkzFlB8YYFRhf6crKeuqMC-86h3xytWcTuX9Hvk7f5xBWleKfUBkUTzQTwfq4PFpzm2CCyVNWfs-dmsED7ofFV6fRZjsYoqYbvPn7XhWO1Ixf11Xn5njCWtMZOoOExZNkU-9CGJjW_ywDxzs6Q-VZdXGqqS7cjOzD5TdDhAbzCWScfhqXpFQKmWnxbdNEgQ871dhAAAAXiqazyE\"}',
		    'session[username_or_email]':username,
		    'session[password]':password}		
		try:
			req = requests.post(url,headers=headers,data=data)
			if ("ct0") in req.cookies:
				return {'status': 'True', 'message': 'Login True', 'data': {'username': username ,'password': password}}		
			else:
				return {'status': 'False', 'message': "False Login"}
		except requests.exceptions.ConnectionError:
			return {'status': 'False'}
		except KeyboardInterrupt:
			return {'status': 'False'}

class snapchat:
	def account(email,password,user):
		m = requests.get(f"https://tufaah1.osc-fr1.scalingo.io/snapchat_register/?user={user}&email={email}&password={password}")
		if "{'error': 'Password must be at least 8 chars', 'ok': False}" in m.text:
			return {"result": "False" , "message": "Password must be at least 8 chars"}
		elif m.json()["ok"]==True:
			return {"result": "True" , "message": "Successful Create" , "data": {"username": user , "password": password , "email": email}}
		elif m.json()["error"]=="Taken user":
			return {"result": "False" , "message": "Taken User"}
		elif m.json()["error"]=="Wrong email":
			return {"result": "False" , "message": "Error Email"}

class pythonanywhere:
	def account():
		password = '@ZERTOOLS'
		us = 'qwertyuiopasdfghjklzxcvbnm123456789'
		usn = '56'
		num = int("".join(random.choice(usn) for i in range(1)))
		user = str("".join(random.choice(us) for i in range(num)))
		email = user+"@ZER.TOOLS"
		url = "https://www.pythonanywhere.com/registration/register/beginner/"
		headers = {
			'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
			'Accept-Encoding':'gzip, deflate, br',
			'Accept-Language':'ar,en-US;q=0.9,en;q=0.8',
			'Cache-Control':'max-age=0',
			'Connection':'keep-alive',
			'Content-Length':'205',
			'Content-Type':'application/x-www-form-urlencoded',
			'Cookie':'cookie_warning_seen=True; csrftoken=TkHTqOWVKR3iSlaa8dUlu4aCJDHmxI4jN3qWLMXcvIoDfQ7cPcfpGGlALFjP8jsM; sessionid=v4lws3sng81oi16u22dfcpy88cmvfx85; _ga=GA1.1.1238304792.1644655935; _gid=GA1.1.1486788854.1644655935',
			'Host':'www.pythonanywhere.com',
			'Origin':'https://www.pythonanywhere.com',
			'Referer':'https://www.pythonanywhere.com/registration/register/beginner/',
			'sec-ch-ua':'" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
			'sec-ch-ua-mobile':'?0',
			'sec-ch-ua-platform':'"Windows"',
			'Sec-Fetch-Dest':'document',
			'Sec-Fetch-Mode':'navigate',
			'Sec-Fetch-Site':'same-origin',
			'Sec-Fetch-User':'?1',
			'Upgrade-Insecure-Requests':'1',
			'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36'
		}
		data = { 
				'csrfmiddlewaretoken':'D9GVdvDO2ryrW7ZazDaFlKVxTSLJUzbfxSpYytE5NiTMjCWcgCvJxm6vVUncvazI',
			'username': user,
			'email': email,
			'password1': password,
			'password2': password,
			'tos': 'on',
			'recaptcha_response_token_v3': ''
		}
		m = requests.post(url,headers=headers,data=data).text
		if "This username is already taken. Please choose another" in m:
			return {"result": "False" , "message": "Taken User"}
		elif "Please enter a valid email address." in m:
			return {"result": "False" , "message": "Email Error"}
		elif "Dashboard" in m:
			return {"result": "True" , "message": "Successful Create" , "data": {"username": user , "password": password , "email": email}}
		else:
			return {"result": 'False' , "message": "Blocked Please Wait 5 minute"}

class proxy:
	def get_proxy():
		req = requests.get('https://gimmeproxy.com/api/getProxy')
		if '"protocol"' in req.text or '"ip"' in req.text or '"port"' in req.text:
			if str(req.json()['protocol']) == 'socks5':
				proxy = str(req.json()['curl'])
				return {'status': 'True', 'message': {'Proxy': f'{proxy}'}}
			else:
				return {'status': 'False', 'message': {'proxy': 'Bad'}}
		else:
			return {'status': 'False', 'message': {'Protocol': 'Bad'}}
	def csrf_token():
		headers = {"User-Agent": str(generate_user_agent())}
		r = requests.Session()
		url = "https://www.instagram.com/"
		data = r.get(url,headers=headers).content
		token = re.findall('{"config":{"csrf_token":"(.*)","viewer"', str(data))[0]
		return {'status': 'True', 'message': {'csrf_token': f'{token}'}}
	def get_user_agent():
		agent = os.system('ua')
		return agent

class visa:
	def card(card):
		visaa = '5491840818844437|06|2026|214'
		visa = card
		url = "https://checker.visatk.com/ccn1/alien07.php"
		headers = {
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
			'Accept-Encoding': 'gzip, deflate, br',
			'Accept-Language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
			'Connection': 'keep-alive',
			'Content-Length': '57',
			'Content-Type': 'application/x-www-form-urlencoded',
			'Cookie': '__gads=ID=42ac6c196f03a9b4-2279e5ef3fcd001d:T=1645035753:RT=1645035753:S=ALNI_MZL7kDSE4lwgNP0MHtSLy_PyyPW3w; PHPSESSID=tdsh3u2p5niangsvip3gvvbc12',
			'Host': 'checker.visatk.com',
			'Origin': 'https://checker.visatk.com',
			'Referer': 'https://checker.visatk.com/ccn1/',
			'sec-ch-ua': '"Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
			'sec-ch-ua-mobile': '?1',
			'sec-ch-ua-platform': '"Android"',
			'Sec-Fetch-Dest': 'empty',
			'Sec-Fetch-Mode': 'cors',
			'Sec-Fetch-Site': 'same-origin',
			'User-Agent': str(generate_user_agent)
		}
		data = {
			'ajax': '1',
			'do': 'check',
			'cclist': visa
		}
		req = requests.post(url, headers=headers, data=data)
		if '"error":0' in req.text:
			mny = req.text.split("[Charge :<font color=green>")[1]
			flos = mny.split("</font>] [BIN:")[0]
			message = {'status': 'True', 'message': {'Many': f'{flos}', 'Card': f'{visa}'}}
			return message
		elif 'Many' in req.text:
			mny = req.text.split("Many': '")[1]
			flos = mny.split("',")[0]
			message = {'status': 'True', 'message': {'Many': f'{flos}', 'Card': f'{visa}'}}
			return message
		else:
			return {'status': 'False', 'message': 'False Visa'}

class users:
	def telegram(user):
		req = requests.get(f"https://t.me/{user}").text
		if 'tgme_username_link' in req:
			return {'message': {'username': f'{user}', 'message': f'Available Username : {user}'}}
		else:
			return {'message': {'username': f'{user}', 'message': f'Not Available Username : {user}'}}
	def instagram(user):
		url = f'https://www.instagram.com/{user}/'
		insta = requests.get(url).status_code
		if insta == 404:
			return {'message': {'username': f'{user}', 'message': f'Available Username : {user}'}}
		else:
			return {'message': {'username': f'{user}', 'message': f'Not Available Username : {user}'}}
	def tiktok(user):
		tiktok = {
			'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
			'accept-encoding': 'gzip, deflate, br',
			'accept-language': 'en-US,en;q=0.9,ar;q=0.8',
			'cache-control': 'max-age=0',
			'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
			'sec-ch-ua-mobile': '?0',
			'sec-fetch-dest': 'document',
			'sec-fetch-mode': 'navigate',
			'sec-fetch-site': 'same-origin',
			'sec-fetch-user': '?1',
			'upgrade-insecure-requests': '1',
			'user-agent': 'Mozilla/5.0(Windows NT 10.0;Win64;x64) AppleWebKit/537.36(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
		}
		url = f'https://www.tiktok.com/@{user}?'
		tik = requests.get(url, headers=tiktok).status_code
		if tik == 404:
			return {'message': {'username': f'{user}', 'message': f'Available Username : {user}'}}
		else:
			return {'message': {'username': f'{user}', 'message': f'Not Available Username : {user}'}}

class send:
	def followers(user):
		email = "qwertyuiopasdfghjklzxcvbnm1234567890"
		us = str(''.join((random.choice(email) for i in range(7))))
		gmail = us+"@gmail.com"
		url = "https://core.poprey.com/api/create_test_order_v2.php"
		data = {
			"service":"Followers",
			"email":str(gmail),
			"username":str(user),
			"system":"Instagram",
			"count":"10",
			"type":"t1",
		}
		req = requests.post(url, data=data).text
		if str("In the past 24 hours you've already used the free test.") in str(req):
			return {'status': 'False', 'message': 'Try After 24 Hours !'}
		if str('{"result":"Ok",') in str(req):
			return {'status': 'True', 'message': 'Done Send 10 Followers', 'username': f'{user}'}
		if str('open your profile') in str(req):
			return {'status': 'False', 'message': 'Username Error'}
		if str('{"result":"Error","error_code":"303","text":"Free test is only for new clients and those who make purchases."}') in str(req):
			return {'status': 'False', 'message': "Please Add a New Account"}