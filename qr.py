import os
from PIL import Image
import urllib3
from pyzbar.pyzbar import decode
import pygoqrme
from twilio.rest import Client
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from os.path import basename
import imaplib
import email.header
import sys

cwd = os.getcwd()
account_sid = 'account_sid'
auth_token = 'auth_token'
client = Client(account_sid, auth_token)



dict_of_emails = {
	"name_friend1": [],
	"name_friend2": [],
	"name_friend2": [],
	"Kellen": [],
}

for item in dict_of_emails:
	new_directory = os.path.join(cwd, item)
	if not os.path.exists(new_directory):
		os.makedirs(new_directory)

def makeQR(colour: str, text: str, path: str):
	qr = pygoqrme.Api(color = colour)
	qr.text(text)
	qr.save(path)
	print("QR made")


def decodeQR(file:str):
	img = Image.open(file)
	img.show()
	d = decode(img)
	print(d[0].data)


def textME(txt):
	message = client.messages.create(
						 body=txt,
						 from_='from#',
						 to='to#'
					 )

	print(message.sid)





def send_mail(send_from: str, subject: str, text: str, 
	send_to: list, files= None):

	send_to= default_address if not send_to else send_to

	msg = MIMEMultipart()
	msg['From'] = send_from
	msg['To'] = ', '.join(send_to)  
	msg['Subject'] = subject

	msg.attach(MIMEText(text))

	for f in files or []:
		with open(f, "rb") as fil: 
			ext = f.split('.')[-1:]
			attachedfile = MIMEApplication(fil.read(), _subtype = ext)
			attachedfile.add_header(
				'content-disposition', 'attachment', filename=basename(f) )
		msg.attach(attachedfile)


	smtp = smtplib.SMTP(host="smtp.gmail.com", port= 587) 
	smtp.starttls()
	smtp.login("email","password")
	smtp.sendmail(send_from, send_to, msg.as_string())
	smtp.close()




# Your IMAP Settings

def downloadAttachments(subject: str):
	host = 'imap.gmail.com'
	user = 'email@gmail.com'
	password = 'password'

	# Connect to the server
	print('Connecting to ' + host)
	mailBox = imaplib.IMAP4_SSL(host)

	# Login to our account
	mailBox.login(user, password)

	boxList = mailBox.list()
	# print(boxList)

	mailBox.select()
	searchQuery = '(SUBJECT "' +subject +'")'

	result, data = mailBox.uid('search', None, searchQuery)
	ids = data[0]
	# list of uids
	id_list = ids.split()

	i = len(id_list)
	for x in range(i):
		latest_email_uid = id_list[x]
		if(i > 15 and x < i-5):
			temp = "\ ".strip()+"\ ".strip()+'Deleted'
			print(temp)
			mailBox.uid('STORE', latest_email_uid, "+FLAGS", "(\\Deleted)")
		else:
			# fetch the email body (RFC822) for the given ID
			result, email_data = mailBox.uid('fetch', latest_email_uid, '(RFC822)')

			# I think I am fetching a bit too much here...

			raw_email = email_data[0][1]

			# converts byte literal to string removing b''
			raw_email_string = raw_email.decode('utf-8')
			email_message = email.message_from_string(raw_email_string)

			#message_ids = str(email_message).split("Message-ID: <")[1].split(">")[0]
			from_email = str(email_message).split(" <")[1].split(">\n")[0]
			subject = str(email_message).split("Subject: ", 1)[1].split("\nTo:", 1)[0]
		   	#print(from_email + str(x))
			#print(str(email_message))
			# downloading attachments
			for item in dict_of_emails:
				#print(from_email)
				temp = []
				if item.lower() in from_email.lower():
					#print(subject)
					dict_of_emails[item].append(email_message)
				#print(email_message.walk())
	mailBox.expunge()
	for item in dict_of_emails:
		if len(dict_of_emails[item]) > 0:

			dict_of_emails[item] = dict_of_emails[item][-1]
			#print("NEW: \t"+str(dict_of_emails[item]).split("Date: ")[1].split("(PST)")[0])
			#print(str(dict_of_emails[item]).split("Subject: ", 1)[1].split("\nTo:", 1)[0])
			#print(dict_of_emails[item])


			for part in dict_of_emails[item].walk():
								# this part comes from the snipped I don't understand yet... 
					if part.get_content_maintype() == 'multipart':
						continue
					if part.get('Content-Disposition') is None:
						continue
					fileName = part.get_filename()

					if bool(fileName):
						filePath = os.path.join(cwd, item)
						length = len(next(os.walk(filePath))[2])
						#print(length)
						txt = os.path.join(filePath, "txt.txt")
						filePath = os.path.join(filePath, "qrcode"+str(length)+".png")
						if not os.path.isfile(txt):
							print("hi")
							fil = open(txt, "w")
							fil.write(str(dict_of_emails[item]).split("Message-ID: <")[1].split(">")[0])
							fil.close()

							if not os.path.isfile(filePath) :
								fp = open(filePath, 'wb')
								fp.write(part.get_payload(decode=True))
								fp.close() 
						else:
							fil = open(txt, "r")
							result = fil.read()
							fil.close()
							print(result)
							print(str(dict_of_emails[item]).split("Message-ID: <")[1].split(">")[0] + "\t!")
							print(result == str(dict_of_emails[item]).split("Message-ID: <")[1].split(">")[0])
							if result != str(dict_of_emails[item]).split("Message-ID: <")[1].split(">")[0]:
								print(result)
								fil = open(txt, "w")
								fil.write(str(dict_of_emails[item]).split("Message-ID: <")[1].split(">")[0])
								fil.close()



							
						#print(filePath)

								if not os.path.isfile(filePath) :
									fp = open(filePath, 'wb')
									fp.write(part.get_payload(decode=True))
									fp.close() 
		#print(subject)
		#print(str(email_message).split("Date: ")[1].split("\nContent")[0])
		#print(latest_email_uid.decode("utf-8"))

		  
		#print('Downloaded "{file}" from email titled "{subject}" with UID {uid}.'.format(file=fileName, subject=subject, uid=latest_email_uid.decode('utf-8')))
	print(dict_of_emails)
	mailBox.close()
	mailBox.logout()


for i in range(17):
	makeQR("128-"+str(i*15)+"-"+str(i*30),"test", 'images/qr'+str(i)+'.png')
	decodeQR(cwd+"\images\qr"+str(i)+".png")
	send_mail("testemail@gmail.com", "test", str(i), ["testemail@gmail.com"], [cwd+"\images\qr"+str(i)+".png"])
downloadAttachments("test")
#textME("done")

