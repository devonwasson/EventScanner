var students = {};
var todaysDate = new Date();
var scannedIds = [];
var outFile = "";

// Validates the User's ID and passes result to the helper
function testIfAuthorized(id) {
    $.post( "/test-approved-user/", {
        id: id
    }, 
    function(data) {
        result = __(data);
        testIfIsAuthorizedHelper(result, id);
    });
    function __(data) {
        return data;
    }
    return
}

function testIfIsAuthorizedHelper(result, id){
    document.getElementById('testAuth').style.display = "none";
    document.getElementById('testAuth').style.visibility = "hidden";
    if (result == 'true') {
        document.getElementById('selectEvent').style.display = "block";
        document.getElementById('selectEvent').style.visibility = "visible";
        document.getElementById('authUserId').innerHTML = id;
        document.getElementById('eventName').focus();
        getEventFileNames();
    }
    else {
        document.getElementById("unauthorized").style.visibility = "visible";
    }
    return
}

// Validates the User's ID and passes resulting info to the helper
function getEventFileNames() {
    $.post( "/event-file-names-request/", {
        id: document.getElementById('authUserId').innerHTML
    }, 
    function(data) {
        result = __(data);
        getEventFileNamesHelper(result);
    });
    function __(data) {
        return data;
    }
    return
}

function getEventFileNamesHelper(result) {
    if (result == "false") {
        return
    }
    console.log(result);
    csvFileNames = JSON.parse(result.replace(/'/g, "\""));
    // make new drop down options from list
    for (var fileNum = 0; fileNum < csvFileNames.length; fileNum++) {
        var fileName = csvFileNames[fileNum];
        var option = document.createElement("option");
        option.text = fileName;
        document.getElementById("events").add(option);
    }
}


// Validates the User's ID and makes a new file for the event
function makeNewOutFile(fileName) {
    $.post( "/make-new-outfile/", {
        id: document.getElementById('authUserId').innerHTML,
        fileName: fileName
    }, 
    function(data) {
        result = __(data);
        makeNewOutFileHelper(result, fileName);
    });
    function __(data) {
        return data;
    }
    return
}

function makeNewOutFileHelper(result, fileName){
    if (result == 'duplicate') {
        document.getElementById('documentExists').style.visibility = "visible";
    }
    else if (result == 'false') {
        document.getElementById("selectEvent").style.visibility = "hidden";
        document.getElementById("unauthorized").style.visibility = "visible";
    } else {        
        outFile = fileName;
        document.getElementById("eventHeader").innerHTML = "Event: " + fileName;
        document.getElementById("selectEvent").style.visibility = "hidden";
        document.getElementById("scanIds").style.visibility = "visible";
        document.getElementById('documentExists').style.visibility = "hidden";
        document.getElementById('studentId').focus();
        document.getElementById('selectEvent').style.display = "none";
        document.getElementById('scanIds').style.display = "block";
    }
    return
}


// Validates the User's id and get previously stored student ids for event
function openOldOutFile(fileName) {
    $.post( "/open-old-outfile/", {
        id: document.getElementById('authUserId').innerHTML,
        fileName: fileName
    }, 
    function(data) {
        result = __(data);
        openOldOutFileHelper(result, fileName);
    });
    function __(data) {
        return data;
    }
    return
}

function openOldOutFileHelper(result, fileName){
    if (result == 'false') {
        document.getElementById("scanIds").style.visibility = "hidden";
        document.getElementById("unauthorized").style.visibility = "visible";
    } else {
        outFile = fileName;
        previousIds = JSON.parse(result.replace(/'/g, "\""));
        for (var i = 0; i < previousIds.length; i++) {
            scannedIds.push(previousIds[i]);
        }
        document.getElementById("totalCount").innerHTML = "Total Attendance: " + scannedIds.length.toString();
        document.getElementById("eventHeader").innerHTML = "Event: " + fileName;
        document.getElementById("selectEvent").style.visibility = "hidden";
        document.getElementById("scanIds").style.visibility = "visible";
        document.getElementById('documentExists').style.visibility = "hidden";
        document.getElementById('selectEvent').style.display = "none";
        document.getElementById('scanIds').style.display = "block";
    }
    return
}

// Validates User's ID and returns all current ID information
function scanId(scannedId) {
    $.post( "/save-id-to-csv/", {
        id: document.getElementById('authUserId').innerHTML,
        scannedId: scannedId,
        fileName: outFile
    }, 
    function(data) {
        result = __(data);
        scanIdHelper(result);
    });
    function __(data) {
        return data;
    }
    return
}

function scanIdHelper(result) {
    results = JSON.parse(result.replace(/'/g, "\""));
    message = results[0];
    numScanned = results[1];
    document.getElementById("message").innerHTML = message;
    document.getElementById("studentId").value = "";
    document.getElementById("totalCount").innerHTML = "Total Attendance: " + numScanned
}

// Validates User's ID and returns list of valid email addresses
function getAuthorizedEmailerNames() {
    $.post( "/emailer-name-request/", {
        authUserId: document.getElementById('authUserId').innerHTML
    }, 
    function(data) {
        result = __(data);
        getAuthorizedEmailerNamesHelper(result);
    });
    function __(data) {
        return data;
    }
    return
}

function getAuthorizedEmailerNamesHelper(result) {
    if (result == "false") {
        return
    }
    emailerNames = JSON.parse(result.replace(/'/g, "\""));
    // make new drop down options from list
    for (var emailerIndex = 0; emailerIndex < emailerNames.length; emailerIndex++) {
        var emailerName = emailerNames[emailerIndex];
        var option = document.createElement("option");
        option.text = emailerName;
        document.getElementById("emailNames").add(option);
    }
}

function finish() {
    document.getElementById("scanIds").style.visibility = "hidden";
    document.getElementById("email").style.visibility = "visible";
    document.getElementById('scanIds').style.display = "none";
    document.getElementById('email').style.display = "block";
    getAuthorizedEmailerNames();
}

// Validates the User's ID and requested email address, and sends an email with all of the IDs to an authorized user
function emailCsv(to) {
    document.getElementById("emailText").style.visibility = "hidden";
    document.getElementById("emailForm").style.visibility = "hidden";
    document.getElementById("pleaseWait").style.visibility = "visible";
    $.post( "/send-email/", {
        authUserId: document.getElementById('authUserId').innerHTML,
        toAddr: to,
        fileName: outFile,
        eventName: document.getElementById("eventHeader").innerHTML
    }, 
    function(data) {
        result = __(data);
        emailCsvHelper(result);
    });
    function __(data) {
        return data;
    }
    return
}

function emailCsvHelper(result) {
    if (result == "true") {
        document.getElementById("pleaseWait").style.visibility = "hidden";
        document.getElementById("thankYouText").style.visibility = "visible";
    }
    else {
        document.getElementById("unauthorized").style.visibility = "visible";
        document.getElementById("pleaseWait").style.visibility = "hidden";
    }
    return
}



// BEGIN FUNCTIONS FOR ADMIN PAGE

function testIfAdmin(id) {
    $.post( "/test-if-admin/", {
        id: id
    }, 
    function(data) {
        result = __(data);
        testIfAdminHelper(result, id);
    });
    function __(data) {
        return data;
    }
    return
}

function testIfAdminHelper(result, id){
    document.getElementById('testAdmin').style.visibility = "hidden";
    if (result == 'true') {
        document.getElementById('authUserId').innerHTML = id;
        document.getElementById('addEmailer').style.visibility = "visible";
        document.getElementById('uploadNewCsv').style.visibility = "visible";
        document.getElementById('addNewStudent').style.visibility = "visible";
        document.getElementById('removeAuthorizedUsers').style.visibility = "visible";
    }
    else {
        document.getElementById("unauthorized").style.visibility = "visible";
    }
    return
}


function testIfAdmin(id) {
    $.post( "/test-if-admin/", {
        id: id
    }, 
    function(data) {
        result = __(data);
        testIfAdminHelper(result, id);
    });
    function __(data) {
        return data;
    }
    return
}

/*function testIfAdminHelper(result, id){
    document.getElementById('testAdmin').style.visibility = "hidden";
    if (result == 'true') {
        document.getElementById('adminUserId').innerHTML = id;
        document.getElementById('addEmailer').style.visibility = "visible";
        document.getElementById('uploadNewCsv').style.visibility = "visible";
        document.getElementById('addNewStudent').style.visibility = "visible";
        document.getElementById('outMessage').style.visibility = "hidden";
    }
    else {
        document.getElementById("unauthorized").style.visibility = "visible";
    }
    return
}*/

function enterNewAuthStudent(id) {
    $.post( "/add-new-authorized-student/", {
        id: id,
        adminUserId: document.getElementById('adminUserId').innerHTML
    }, 
    function(data) {
        result = __(data);
        enterNewAuthStudentHelper(result);
    });
    function __(data) {
        return data;
    }
    return
}

function enterNewAuthStudentHelper(result){
    if (result == 'false') {
        document.getElementById('addEmailer').style.visibility = "hidden";
        document.getElementById('uploadNewCsv').style.visibility = "hidden";
        document.getElementById('addNewStudent').style.visibility = "hidden";
        document.getElementById('outMessage').style.visibility = "hidden";
	document.getElementById('removeAuthorizedUsers').style.visibility = "hidden";
        document.getElementById("unauthorized").style.visibility = "visible";
    }
    else {
        console.log(result);
        document.getElementById('studentIdForm').reset();
        document.getElementById('outMessage').style.visibility = "visible";
        if ((result == 'User already has access') || (result == 'Unrecognised ID')) {
            document.getElementById('outMessage').innerHTML = result;
        } else {
            document.getElementById('outMessage').innerHTML = result + "has been added as an authorized scanner.";
        }
    }
    return
}

function enterNewEmailer(email) {
    $.post( "/add-new-authorized-emailer/", {
        email: email,
        adminUserId: document.getElementById('adminUserId').innerHTML
    }, 
    function(data) {
        result = __(data);
        enterNewEmailerHelper(result);
    });
    function __(data) {
        return data;
    }
    return
}

function enterNewEmailerHelper(result){
    if (result == 'false') {
        document.getElementById('addEmailer').style.visibility = "hidden";
        document.getElementById('uploadNewCsv').style.visibility = "hidden";
        document.getElementById('addNewStudent').style.visibility = "hidden";
        document.getElementById('outMessage').style.visibility = "hidden";
        document.getElementById('removeAuthorizedUsers').style.visibility = "hidden";
        document.getElementById("unauthorized").style.visibility = "visible";
    } else {
        console.log(result);
        document.getElementById('emailerAddressForm').reset();
        document.getElementById('outMessage').style.visibility = "visible";
        if ((result == 'User already has access') || (result == "Invalid email address")) {
            document.getElementById('outMessage').innerHTML = result;
        } else {
            document.getElementById('outMessage').innerHTML = result + " has been added as an email recepient.";
        }
    }
    return
}

function removeAuthorizedUser(user) {
    $.post( "/remove-authorized-student/", {
        id: id,
        adminUserId: document.getElementById('adminUserId').innerHTML
    },
    function(data) {
        result = __(data);
        enterNewAuthStudentHelper(result);
    });
    function __(data) {
        return data;
    }
    return
}

function removeAuthorizedUserHelper(result){
    if (result == 'false') {
        document.getElementById('addEmailer').style.visibility = "hidden";
        document.getElementById('uploadNewCsv').style.visibility = "hidden";
        document.getElementById('addNewStudent').style.visibility = "hidden";
        document.getElementById('outMessage').style.visibility = "hidden";
        document.getElementById('removeAuthorizedUsers').style.visibility = "hidden";
        document.getElementById("unauthorized").style.visibility = "visible";
    }
    else {
        console.log(result);
        document.getElementById('removeAuthorizedUsers').reset();
        document.getElementById('outMessage').style.visibility = "visible";
        if ((result == 'Unable to find user.')) {
            document.getElementById('outMessage').innerHTML = result;
        } else {
            document.getElementById('outMessage').innerHTML = result + "has been removed as an authorized scanner";
        }
    }
    return
}

// For uploading files to server
$(function() {
    $('#upload-file-btn').click(function() {
        document.getElementById('outMessage').style.visibility = "visible";
        document.getElementById('outMessage').innerHTML = 'Please wait...';
        var form_data = new FormData($('#uploadNewCsv')[0]);
        form_data.append('adminUserId', document.getElementById('adminUserId').innerHTML)
        $.ajax({
            type: 'POST',
            url: '/upload-new-csv/',
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,
            async: false,
            success: function(result) {
                if (result == 'true') {
                    document.getElementById('outMessage').innerHTML = 'Successfully uploaded new file';
                } else if (result == 'false') {
                    document.getElementById('addEmailer').style.visibility = "hidden";
                    document.getElementById('uploadNewCsv').style.visibility = "hidden";
                    document.getElementById('addNewStudent').style.visibility = "hidden";
                    document.getElementById('outMessage').style.visibility = "hidden";
	            document.getElementById('removeAuthorizedUsers').style.visibility = "hidden";
                    document.getElementById("unauthorized").style.visibility = "visible";
                } else {
                    document.getElementById('outMessage').innerHTML = result;
                }
            },
        });
    });
});

document.getElementById('AuthId').focus();
