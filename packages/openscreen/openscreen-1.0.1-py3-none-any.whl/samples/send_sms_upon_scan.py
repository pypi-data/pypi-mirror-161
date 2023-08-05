import os
from openscreen import Openscreen
#Obtain your access key and secret from Openscreen Dashboard
ospro = Openscreen(access_key=os.environ.get('OS_ACCESS_KEY'), access_secret=os.environ.get('OS_ACCESS_SECRET'))
#Create a new project on Openscreen Dashboard. Paste the projectId below
projectId = os.environ.get('PROJECT_ID')

#This example shows how to create a contact and send SMS to the contact, upon a succesful QR code scan
#It is your responsibility to ensure a contact has a valid consent in order to send SMS
#The content of the message can be passed in the request body or using an SMS template. 

#create a dynamic QR code and obtain scanId as a path parameter
my_asset = ospro.project(projectId).assets().create({
    'name': '123 Main Steet Sign',
    'description': 'Sign for 123 Main Street, Toronto',
    'customAttributes': {
        'type': 'Sale',
        'MLS#': '123ABC'
    },
    'qrCodes': [{
        'intent': 'https://my-real-estate-website.com/listingId/',
        'intentType': 'DYNAMIC_REDIRECT',
        #scanId is stored in the query string parameter
        'dynamicRedirectType': 'SCAN_ID_IN_QUERY_STRING_PARAMETER',
        'status': 'ACTIVE',
        'locatorKeyType': 'SHORT_URL'
    }]
})

assetId = my_asset.asset.assetId
qrCodeId = my_asset.asset.qrCodes[0].qrCodeId
#Your webapp should record the scanId which is available in the query string
scanId = 'FETCH_SCANID_FROM_QUERY_STRING'

#create a contact by scanId
contact = ospro.scan(scanId).contacts().create({ 
    'firstName': 'Brian',
    'lastName': 'Smith',
    'cellPhone': '+14161234567'
    'consent': [{
        'url': "https://sidewalkqr.com/123main/consent", 
        'consentedAt': "2021-06-20 08:03:00.0", 
        'consented': true
    }]
})

#create SMS template
smsTemplate = ospro.project(projectId).smsTemplates().create({
        'body': 'SMS Template Text body for {{asset.name}}',
        'smsTemplateName': 'firstTemplate',
        'responseUrl': 'httpe://myapp/sms-response',
        'statusUrl': 'httpe://myapp/sms-status'
    })

#send sms by scanId to the contact created above
#You may send message context in the body of the message or use the SMS template.
#In this case, we use the SMS template
contactId = contact.contact.contactId
smsTemplateName = smsTemplate.smsTemplate.smsTemplateName
send_sms = ospro.scan(scanId).sms().send({
    'smsTemplateName': smsTemplateName,
    'contactId': contactId
})