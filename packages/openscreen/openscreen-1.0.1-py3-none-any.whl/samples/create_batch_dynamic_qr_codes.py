import os
from openscreen import Openscreen, CreateAssetsByProjectIdRequestBody

#Obtain your access key and secret from Openscreen Dashboard
ospro = Openscreen(access_key=os.environ.get('OS_ACCESS_KEY'), access_secret=os.environ.get('OS_ACCESS_SECRET'))
#Create a new project on Openscreen Dashboard. Paste the projectId below
projectId = os.environ.get('PROJECT_ID')

#Create multiple assets that each represent a different billboard. 
#Each of these billboards will direct a user to the same listing at 123 Cherry Street. 
bulkAssetsBody = CreateAssetsByProjectIdRequestBody(assets=[
    {
        'name': 'Billboard 1',
        'description': 'Billboard at Yonge and Eglinton for 123 Cherry Street Listing',
        'qrCodes': [
          {
            'intent': 'https://my-real-estate-app.com/123cherry/',
            'intentType': 'DYNAMIC_REDIRECT',
            'dynamicRedirectType': 'NO_SCAN_ID',
            'locatorKeyType': 'SHORT_URL',
            'status': 'ACTIVE'
        }]
    },
    {
        'name': 'Billboard 2',
        'description': 'Billboard at Yonge and Lawrence for 123 Cherry Street Listing',
        'qrCodes': [{
            'intent': 'https://my-real-estate-app.com/123cherry/',
            'intentType': 'DYNAMIC_REDIRECT',
            'dynamicRedirectType': 'NO_SCAN_ID',
            'locatorKeyType': 'SHORT_URL',
            'status': 'ACTIVE'
        }]
    },
    {
    'name': 'Billboard 3',
    'description': 'Billboard at Mt. Pleasant and Eglinton for 123 Cherry Street Listing',
    'qrCodes': [
        {
          'intent': 'https://my-real-estate-app.com/123cherry/',
          'intentType': 'DYNAMIC_REDIRECT',
          'dynamicRedirectType': 'NO_SCAN_ID',
          'locatorKeyType': 'SHORT_URL',
          'status': 'ACTIVE'
        }]
    }])
bulkAssets = ospro.project(projectId).assetsBatch().create(bulkAssetsBody)