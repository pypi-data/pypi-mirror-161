# Openscreen Python SDK
[Openscreen](www.openscreen.com) is a developer-first platform that enables innovative customer engagement and commerce solutions using QR Codes. 
Additional information on using the Openscreen python SDK can be found in the developer [documentation](https://docs.openscreen.com/overview). 
## Requirements
 - [python](https://www.python.org/downloads/release/python-3100/) 3.10.0 or above
 
You will need your Openscreen account key and secret to get started. If you do not have an Openscreen account, you can sign-up for free [here](https://app.openscreen.com/signup). 
## Installation
```
pip3 install openscreen
```
## Getting Started
Openscreen authenticates your API requests using your account's API key and API secret key. You will also need the ID of the project you wish to work with. Your API key, secret key and project ID can all be found in your by logging into your Openscreen [dashboard](https://app.openscreen.com/). The following examples demonstrates how to use these values in the SDK to generate your first QR code.
```py
from openscreen import Openscreen, save_qr_image_data_to_file
#Obtain your access_key and secret by logging into your Openscreen dashboard
os  =  Openscreen(access_key='YOUR_ACCESS_KEY', access_secret='YOUR_SECRET_KEY')
#You must create a project and obtain project_id from your Openscreen dashboard
my_asset  =  os.project('YOUR_PROJECT_ID').assets().create({
    'name': 'My First QR Code',
    'description': 'Dynamic QR Code',
    'qr_codes': [
        {
            'intent': 'https://www.openscreen.com',
            'intent_type': 'DYNAMIC_REDIRECT',
            'dynamic_redirect_type': 'NO_SCAN_ID',
            'locator_key_type': 'SHORT_URL',
            'status': 'ACTIVE'
        }
    ]
})
qr_code  =  my_asset.asset.qr_codes[0]
save_qr_image_data_to_file(qr_code.image_data, 'qr_code.png')
```
## Links 
- [Openscreen Website](https://www.openscreen.com/)
- [Developer Documentation](https://docs.openscreen.com/overview)
- [Solutions and Use-cases](https://docs.openscreen.com/tutorials/brand-protection)