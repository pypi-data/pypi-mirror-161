import os
import pytest
import openscreen

@pytest.fixture
def openscreen_session():
    return openscreen.Openscreen(access_key=os.environ.get('OS_ACCESS_KEY'), access_secret=os.environ.get('OS_ACCESS_SECRET'), env=os.environ.get('OS_ENVIRONMENT'))

@pytest.fixture()
def account_id():
    return os.environ.get('OS_ACCOUNT_ID')

@pytest.fixture()
def project_id():
    return os.environ.get('OS_PROJECT_ID')

def asset__id_plugin():
    return None

def pytest_configure():
    pytest.asset_id = asset__id_plugin()