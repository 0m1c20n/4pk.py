import configparser
import getpass
import sys

from gpapi.googleplay import GooglePlayAPI, RequestError, LoginError, SecurityCheckError
from urllib.parse import urlparse, parse_qs


def logo():
	print('\033[91m'+'''

  _  _         _                  
 | || |       | |                 
 | || |_ _ __ | | __  _ __  _   _ 
 |__   _| '_ \| |/ / | '_ \| | | |
    | | | |_) |   < _| |_) | |_| |
    |_| | .__/|_|\_(_) .__/ \__, |
        | |          | |     __/ |
        |_|          |_|    |___/ 

                '''+'\033[0m')


if __name__ == '__main__':
	logo()
	locale = input('Enter your region (i.e.: es_ES): ')
	device_codename = input('Enter a device codename: ')
	try:
		server = GooglePlayAPI(locale=locale, timezone='CET', device_codename=device_codename)
	except Exception:
		message = 'Device not recognized, you can see valid codenames in device_codenames file.'
		print('\033[91m'+message+'\033[0m')
		sys.exit()
	config = configparser.ConfigParser()
	config.read('4pk.conf')
	
	gsfid = token = None
	if config['Credentials']['id']:
		gsfid = int(config['Credentials']['id'])
	if config['Credentials']['token']:
		token = config['Credentials']['token']
	try:
		server.login(gsfId=gsfid,authSubToken=token)
	except OSError:
		print('\033[93m'+'Connection error, please check your internet connection.'+'\033[0m')
		sys.exit()
	except LoginError:
		print('\033[93m'+'Not possible to login with id and token.'+'\033[0m')
		email = input('Enter Gmail address: ')
		password = getpass.getpass('Password: ')
		try:
			server.login(email=email,password=password)
		except LoginError:
			message = 'Login failed.'
			print('\033[91m'+message+'\033[0m')
			sys.exit()
		except SecurityCheckError:
			message = 'Security error, unlock your account here: https://accounts.google.com/DisplayUnlockCaptcha'
			print('\033[91m'+message+'\033[0m')
			sys.exit()
		else:
			config.set('Credentials','id',str(server.gsfId))
			config.set('Credentials','token',server.authSubToken)
			with open('4pk.py','w') as configfile:
				config.write(configfile)
		
	print('\033[92m'+'Logged in successfully'+'\033[0m')
	app_url = input('Enter application url: ')
	docid = parse_qs(urlparse(app_url).query)['id'][0]
	try:
		app = server.download(docid)
	except Exception:
		pass
	else:
		print('Downloading application ...')
		with open('apks/'+docid + '.apk', 'wb') as apk_file:
			for chunk in app.get('file').get('data'):
				apk_file.write(chunk)
		print('\033[92m'+'APK saved in apks/'+docid+'.apk'+'\033[0m')