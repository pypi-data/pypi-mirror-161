from openscreen import Openscreen
import os
#Obtain your access key and secret from Openscreen Dashboard
ospro = Openscreen(access_key=os.environ.get('OS_ACCESS_KEY'), access_secret=os.environ.get('OS_ACCESS_SECRET'))
#Create a new project on Openscreen Dashboard. Paste the projectId below
projectId = os.environ.get('PROJECT_ID')

#Create an Asset with a QR code 
my_asset_response = ospro.project(projectId).assets().create({
    'name': '123 Main Steet Sign',
    'description': 'Sign for 123 Main Street, Toronto',
    'customAttributes': {
        'type': 'Sale',
        'MLS#': '123ABC'
    },
    'qrCodes': [{
        'intent': 'https://my-real-estate-website.com/listingId',
        'intentType': 'DYNAMIC_REDIRECT'
    }]
})

#Fetch the QR Code Image in png format
qr_code_png = ospro.qrCode(my_asset_response.asset.qrCodes[0].qrCodeId).get({'format':'png'})