import pathlib

import openscreen
import pytest

DEBUG = True
class TestAssets:
    def test_get_assets(self, openscreen_session: openscreen.Openscreen, account_id):
        assets = openscreen_session.account(account_id).assets().get()
        assert type(assets.assets) is list
        assert assets.account_id == account_id

    def test_create_asset(self,openscreen_session: openscreen.Openscreen, project_id):
        asset_res = openscreen_session.project(project_id).assets().create({'name': 'Test asset', 'description': 'Old Description',
        })
        assert not asset_res.asset.deleted
        pytest.asset_id = asset_res.asset.asset_id

    def test_get_asset(self, openscreen_session: openscreen.Openscreen):
        asset_res = openscreen_session.asset(pytest.asset_id).get()
        assert asset_res.asset.asset_id == pytest.asset_id

    def test_save_image_to_asset(self, openscreen_session: openscreen.Openscreen):
        asset_res = openscreen_session.asset(pytest.asset_id).get()
        assert asset_res.asset.asset_id == pytest.asset_id
        qr_code_res = openscreen_session.qr_code(asset_res.asset.qr_codes[0].qr_code_id).get()
        cwd = pathlib.Path(__file__).parent.resolve()
        openscreen_session.save_qr_image_data_to_file(qr_code_res, 'test_images/test_image.jpg')
        assert pathlib.Path('test_images/test_image.jpg').exists()

    def test_update_asset(self,openscreen_session: openscreen.Openscreen):
        new_description = 'New Description'
        asset_res = openscreen_session.asset(pytest.asset_id).update({'description': new_description})
        assert asset_res.asset.asset_id == pytest.asset_id
        assert asset_res.asset.description == new_description

    def test_create_dynamic_qr(self, openscreen_session: openscreen.Openscreen):
        asset_res = openscreen_session.asset(pytest.asset_id).get()
        assert asset_res.asset.asset_id == pytest.asset_id
        qr_code_res = openscreen_session.asset(pytest.asset_id).qr_codes().create({
            'intent': 'https://my-real-estate-app.com/123cherry/',
            'intent_type': 'DYNAMIC_REDIRECT',
            'image_options': {
                'format': 'PNG'
            }
        })
        asset_res = openscreen_session.asset(pytest.asset_id).get()
        assert qr_code_res.qr_code.qr_code_id is not None

    def test_link_contact_to_asset(self, openscreen_session: openscreen.Openscreen):
        asset_res = openscreen_session.asset(pytest.asset_id).get()
        # create contact by projectId
        contact_res = openscreen_session.project(asset_res.asset.project_id).contacts().create({
            "cell_phone": "+16472870751",
            "consent": [
                {
                    "consented": True,
                    "consented_at": "2022-02-04",
                    "url": "https://openscreen.com"
                }
            ],
            "custom_attributes": {},
            "email_address": "jason33@gmail.com",
            "first_name": "jason",
            "last_name": "kitamura",
            "mailing_address": {
                "address": "123 dundas st e",
                "city": "Toronto",
                "country": "CA",
                "postal_or_zip": "1ab 2c3",
                "provinceOrState": "ON"
            },
            "middle_name": "",
            "nickname": "",
            "type": ""
        })
        contact_id = contact_res.contact.contact_id
        # link contact to asset
        asset_res = openscreen_session.asset(pytest.asset_id).contact(contact_id).link({
            "type": "OWNER"
        })
        contact = openscreen_session.asset(pytest.asset_id).contact(contact_id).unlink()
        assert contact is None

    def test_delete_asset(self, openscreen_session: openscreen.Openscreen):
        asset_res = openscreen_session.asset(pytest.asset_id).delete()
        assert asset_res.asset.asset_id == pytest.asset_id
        should_fail_get = False
        try:
            get_asset_res = openscreen_session.asset(pytest.asset_id).get()


        except PermissionError or ModuleNotFoundError:
            should_fail_get = True
        except Exception:
            pass
        assert should_fail_get

    # link contact to asset
