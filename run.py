from flask import Flask, request, render_template, redirect
import json
import csv
import os
import datetime
import time
from emailHelper import sendEmail, testValidEmail
from werkzeug.utils import secure_filename

app = Flask(__name__)

##################
##              ##
## HELPER FNCTS ##
##              ##
##################

def getCsvFileNames():
    fileNames = []
    for fileName in os.listdir(os.getcwd() + "/events"):
        if (".csv" in fileName):
            if ("AllUsers" not in fileName):
                fileNames += [fileName[:-4]]
    return fileNames

def getAuthorizedUserIds():
    f = open('authorized_users.txt', 'r')
    users = f.read().splitlines()
    f.close()
    return users

def getAuthorizedEmailers():
    f = open('approved_emailers.txt', 'r')
    emailers = f.read().splitlines()
    f.close()
    return emailers

def get_date_21_years_ago(d):
    try:
        return d.replace(year = d.year - 21)
    except ValueError:
        return d + (datetime.date(d.year - 21, 1, 1) - datetime.date(d.year, 1, 1))

def testIfAuthUser(user):
    f = open(os.getcwd() + "/authorized_users.txt")
    users = f.read().splitlines()
    f.close()
    print(user, str(users))
    return user in users

def testIfAdmin(user):
    f = open(os.getcwd() + "/admins.txt")
    users = f.read().splitlines()
    f.close()
    return user in users

def testIfAuthEmail(to):
    f = open('approved_emailers.txt', 'r')
    emailers = f.read().splitlines()
    f.close()
    return to in emailers

def testIfInt(string):
    try:
        int(string)
        return True
    except:
        return False

# returns the dictionary of all students for testing
# example {student_id: [dob, name]
def makeStudentsDict(filename="AllUsers.csv"):
    d = {}
    f = open(filename)
    lines = f.read().splitlines()
    f.close()
    for line in lines:
        idNum = ""
        dob = ['3000', '12', '25']
        name = ""
        items = line.split(",")
        for item in items:
            if len(item) == 8 and testIfInt(item):
                idNum = item
            elif all(x.isalpha() or x.isspace() or x in " -.()'" for x in item):
                if len(item) > 0:
                    if item[0].isupper():
                        item = item.replace("'", "`")
                        name += item + " "
            elif "/" in item:
                try:
                    parts = item.split("/")
                    dob = [parts[2],parts[0],parts[1]]

                except:
                    pass
            elif "-" in item:
                try:
                    parts = item.split("-")
                    month_number = datetime.datetime.strptime(parts[1], '%b').month
                    dob = [parts[2],month,parts[1]]
                except:
                    pass
        if not idNum == "":
            d[idNum] = [datetime.datetime.strptime(dob[0] + " " + dob[1] + " " + dob[2], "%Y %m %d"), name]
    return d

# Checks if the student being scanned is over 21 and returns an appropriate string
def check21(studentId):
    try:
        studentBirthday = studentsDict[studentId][0];
        studentName = studentsDict[studentId][1];
    except:
        print(str(studentId) + " is an unknown ID")
        return "Unknown student. Please check state ID."
    date_21_years_ago = get_date_21_years_ago(datetime.datetime.now())
    if (time.mktime(studentBirthday.timetuple())) == time.mktime(datetime.datetime.strptime("3000 12 25", "%Y %m %d").timetuple()):
        print(str(studentId) + " is an unknown ID")
        return "Unknown student. Please check state ID."
    elif (studentBirthday < date_21_years_ago):
        print(studentName + "is OVER 21.")
        return studentName + "is OVER 21.";
    else:
        print(studentName + "is UNDER 21.")
        return studentName + "is UNDER 21.";

def allowed_filename(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in set(['csv'])

def getIdFromName(name):
    for student_id in studentsDict:
        if name in studentsDict[student_id][1]:
            return student_id
    return ""

#################
##             ##
## APP ROUTING ##
##             ##
#################

@app.route("/")
def index():
    fileNames = getCsvFileNames()
    return render_template('index.html', fileNames = fileNames)

@app.route("/admin/")
def admin():
    return render_template('admin.html')

@app.route("/refresh-student-information/")
def refreshStudentDict():
    global studentsDict
    studentsDict = makeStudentsDict()
    return render_template('admin.html')


#################
##             ##
##  MAIN PAGE  ##
##             ##
#################

# Takes the id to scan and returns the boolean for
# if id is 21+ and the total number of ids scanned
@app.route('/save-id-to-csv/', methods=['POST'])
def saveIdToCsv():
    studentId = request.form["scannedId"]
    fname = request.form["fileName"].replace("/", "-")
    outFile = "events/" + fname + ".csv"
    authUserId = request.form['id']
    if testIfAuthUser(authUserId):
        f = open(outFile, 'r')
        text = f.read()
        f.close()

        if (not len(studentId) == 8) or (not testIfInt(studentId)):
            return str(["Malformed ID. Please try again or check state ID.", str(len(text.splitlines()))])

        if studentId in text:
            return str(["Card already scanned.", str(len(text.splitlines()))])

        f = open(outFile, "a")
        f.write(str(studentId) + "\n")
        f.close()
        return str([check21(studentId), str(len(text.splitlines())+1)])
    return str(["How did you get here...", "9001"])

# Returns the list of available event names
@app.route('/event-file-names-request/', methods=['POST'])
def eventFileNamesRequest():
    authUserId = request.form["id"]
    if testIfAuthUser(authUserId):
        return str([x.replace("'", "") for x in getCsvFileNames()])
    return "false"

# Opens a new output file if one does not exist
@app.route('/make-new-outfile/', methods=['POST'])
def makeNewOutfile():
    authUserId = request.form["id"]
    fileName = request.form["fileName"].replace("/", "-").replace('"', "").replace("'", "")
    if testIfAuthUser(authUserId):
        outFile = "events/" + fileName + ".csv"
        if not os.path.isfile(os.getcwd() + "/" + outFile):
            f = open(outFile, "a+")
            f.write("")
            f.close()
            return "true"
        return "duplicate"
    return "false"

# returns the list of ids from the requested event
@app.route('/open-old-outfile/', methods=['POST'])
def openOldOutfile():
    authUserId = request.form["id"]
    fileName = request.form["fileName"].replace("/", "-")
    if testIfAuthUser(authUserId):
        outFile = "events/" + fileName + ".csv"
        f = open(outFile, "r")
        ids = f.read().splitlines()
        f.close()
        return str(ids)
    return "false"

# Returns the list of allowable email addresses
@app.route('/emailer-name-request/', methods=['POST'])
def emailerNameRequest():
    authUserId = request.form['authUserId']
    if testIfAuthUser(authUserId):
        f = open("approved_emailers.txt", "r")
        names = f.read().splitlines()
        f.close()
        return str(names)
    return "false"

# Sends an email if the user is valid and the destination is valid
@app.route('/send-email/', methods=['POST'])
def sendAttendence():
    authUserId = request.form['authUserId']
    to = request.form["toAddr"]
    fileName = "events/" + request.form["fileName"] + ".csv"
    eventName = request.form['eventName']
    if testIfAuthUser(authUserId):
        if testIfAuthEmail(to):
            sendEmail("bucknelleventscanner@gmail.com", to+"@bucknell.edu", fileName, eventName, 'bucknellscanner', 'Uptown2017')
            os.remove(fileName)  # still debating this line here...
            print(authUserId + " sent an email to " + to + " for " + eventName + " with file " + fileName)
            return "true"
        print("FAILED, bad email address: " + authUserId + " sent an email to " + to + " for " + eventName + " with file " + fileName)
        return "false"
    print("FAILED, USER NOT AUTHORIZED: " + authUserId + " sent an email to " + to + " for " + eventName + " with file " + fileName)
    return "false"

# Tests if the user is allowed on this page
@app.route('/test-approved-user/', methods=['POST'])
def testUser():
    user = request.form['id']
    f = open(os.getcwd() + "/authorized_users.txt")
    users = f.read().splitlines()
    f.close()
    if user in users:
        return 'true'
    else:
        return 'false'

############################
##                        ##
## BEGIND ADMIN FUNCTIONS ##
##                        ##
############################

# Determins if the person loggin in to the admin page is allowed to access the page
@app.route('/test-if-admin/', methods=['POST'])
def testIfAdminServerFnct():
    user = request.form['id']
    f = open(os.getcwd() + "/admins.txt")
    admins = f.read().splitlines()
    f.close()
    if user in admins:
        return 'true'
    else:
        return 'false'

# Adds a new authorized scanner user
@app.route('/add-new-admin/', methods=['POST'])
def addNewAdmin():
    id = request.form['id']
    adminUserId = request.form['adminUserId']
    if testIfAdmin(adminUserId):
        f = open('admins.txt', 'r')
        ids = f.read().splitlines()
        f.close()
        if id not in ids:
            f = open('admins.txt', 'a')
            f.write(id + "\n")
            f.close()
            return id
        return "User already has access"
    return "false"

# Adds a new authorized scanner user
@app.route('/add-new-authorized-student/', methods=['POST'])
def addNewAuthStudent():
    id = request.form['id']
    adminUserId = request.form['adminUserId']
    if testIfAdmin(adminUserId):
        f = open('authorized_users.txt', 'r')
        ids = f.read().splitlines()
        f.close()
        if id not in ids:
            f = open('authorized_users.txt', 'a')
            f.write(id + "\n")
            f.close()
            return id
        return "User already has access"
    return "false"

# Adds a new valid email address to get student lists after events
@app.route('/add-new-authorized-emailer/', methods=['POST'])
def addNewEmailer():
    email = request.form['email']
    adminUserId = request.form['adminUserId']
    if testIfAdmin(adminUserId):
        f = open('approved_emailers.txt', 'r')
        emailAddresses = f.read().splitlines()
        f.close()
        if email not in emailAddresses:
            f = open('approved_emailers.txt', 'a')
            f.write(email + "\n")
            f.close()
            return email
        return "User already has access"
    return "false"

# Uploads a new student CSV on the admin page
@app.route('/upload-new-csv/', methods=['POST'])
def uploadNewCsv():
    global studentsDict
    adminUserId = request.form['adminUserId']
    if testIfAdmin(adminUserId):
        if 'file' not in request.files:
            return 'No file chosen'
        file = request.files['file']
        if file.filename == '':
            return 'No file chosen'
        if file and allowed_filename(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(os.getcwd(), filename))
            try:
                testStudentDict = makeStudentsDict(filename)
            except:
                return 'File is incorrectly formatted. Please ensure that there is exactly one header line at the top of the file before student information.'
            if len(testStudentDict.keys()) > 0:
                for id in testStudentDict.keys():
                    try:
                        id = str(int(id))
                        if not len(id) == 8:
                            return "Issue: Could not detect student IDs. Please make sure that the csv file contains each student's ID." 
                    except:
                        return "Issue: Could not detect student IDs. Please make sure that the csv file contains each student's ID."
            else:
                return "Issue: Could not detect student IDs. Please make sure that the csv file contains each student's ID."

            if (time.mktime(testStudentDict[id][0].timetuple())) == time.mktime(datetime.datetime.strptime("3000 12 25", "%Y %m %d").timetuple()):
                return "Issue: Could not detect birthday format. Please ensure birthdays are formatted as either 1/1/1990 (month/day/year) or Jan-1-1990 (month(abbrv)-day-year.)"

            studentsDict = testStudentDict
            os.rename(filename, 'AllUsers.csv')
            return 'true'
        return 'File must be a .csv file.'
    return 'false'

# Removes an authorized scanner user
@app.route('/remove-authorized-student/', methods=['POST'])
def removeAuthStudent():
    name_and_id = str(request.form['id'])
    if "(" in name_and_id:
        student_id = name_and_id.split("(")[1].split(")")[0]
    else:
        student_id = name_and_id
    adminUserId = request.form['adminUserId']
    if testIfAdmin(adminUserId):
        f = open('authorized_users.txt', 'r')
        ids = f.read().splitlines()
        f.close()
        if student_id in ids:
            ids.remove(student_id)
        f = open('authorized_users.txt', 'w')
        f.write("\n".join(ids))
        f.close()
        return name_and_id
    return "false"

# Removes an authorized scanner user
@app.route('/remove-authorized-email/', methods=['POST'])
def removeAuthEmail():
    email = str(request.form['email'])
    adminUserId = request.form['adminUserId']
    if testIfAdmin(adminUserId):
        f = open('approved_emailers.txt', 'r')
        emails = f.read().splitlines()
        f.close()
        if email in emails:
            emails.remove(email)
        f = open('approved_emailers.txt', 'w')
        f.write("\n".join(emails))
        f.close()
        return email
    return "false"

# Returns the list of current authorized scanners
@app.route('/authorized-student-names-request/', methods=['POST'])
def authorizedStudentNamesRequest():
    authUserId = request.form["id"]
    if testIfAdmin(authUserId):
        ids = getAuthorizedUserIds()
        to_return = []
        for id in ids:
            if id in studentsDict:
                to_return.append(studentsDict[id][1] + "(" + id + ")")
            else:
                to_return.append(id)
        return str(to_return)
    return "false"

# Returns the list of current authorized emailers
@app.route('/authorized-email-names-request/', methods=['POST'])
def authorizedEmailNamesRequest():
    authUserId = request.form["id"]
    if testIfAdmin(authUserId):
        return str(getAuthorizedEmailers())
    return "false"


studentsDict = makeStudentsDict()


if __name__ == "__main__":
        app.run(debug = True, port=5050)
