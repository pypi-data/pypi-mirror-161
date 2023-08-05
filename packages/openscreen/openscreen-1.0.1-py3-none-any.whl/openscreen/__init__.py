import base64
import re

from .sdk import *
from .session import Session

Prod_Configuration_Path = 'prod-public-mfDwrCg41rf'


class Openscreen(SdkResources):
    os_session = Session

    def __init__(self, access_key, access_secret, env=Prod_Configuration_Path):
        if env is None:
            env = Prod_Configuration_Path
        os_session = Session(access_key=access_key, access_secret=access_secret, config_name=env)
        super().__init__(os_session)
        self.os_session = os_session

    def save_qr_image_data_to_file(self, qr_code: QrCode, file_path: str = None):

        image = qr_code.image
        print(qr_code)
        if image is None or image.data is None or image.options is None:
            raise Exception('Openscreen: invalid qr code for qr code id: ' + qr_code.qr_code_id)
        image_format = qr_code.image.options.format.upper()
        if not file_path:  file_path = f'{qr_code.qr_code_id}.{image_format}'

        if image_format == 'PNG' or image_format == 'JPEG':
            binary_data = ''
            if qr_code.image.options.data_url:
                binary_data = bytearray(base64.b64decode(re.sub('^data:image\/\w+;base64,', '', image.data)))
            else:
                binary_data = bytearray(base64.b64decode(image.data))
            with open(file_path, 'wb') as f:
                f.write(binary_data)
        elif image_format == 'SVG':
            with open(file_path, 'wb') as f:
                f.write(qr_code.image.data)

        else:
            raise Exception('QrCodeType not supported: ' + image_format)
