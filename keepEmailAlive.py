import emailHelper

f = open("config.txt", "r")
lines = f.read().splitlines()
f.close()

emailfrom = "bucknellscanner@gmail.com"
emailto = "bucknellscanner@gmail.com"
fileToSend = None
eventName = "Keep Alive"
username = lines[0].split(":")[1]
password = lines[1].split(":")[1]
emailHelper.sendEmail(emailfrom, emailto, fileToSend, eventName, username, password)
