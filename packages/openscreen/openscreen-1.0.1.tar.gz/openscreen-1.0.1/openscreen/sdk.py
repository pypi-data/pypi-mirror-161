from enum import Enum
from datetime import datetime
from typing import List
from .request_classes import *
from .resources import *
undefined = None


#ENUMERATIONS


class AccountStatus(Enum):
	ACTIVE = 'ACTIVE',
	SUSPENDED = 'SUSPENDED',


class AccountUserRole(Enum):
	OWNER = 'OWNER',
	ADMINISTRATOR = 'ADMINISTRATOR',
	BILLING_CONTACT = 'BILLING_CONTACT',
	MEMBER = 'MEMBER',
	API_KEY = 'API_KEY',
	INVITATION_DECLINED = 'INVITATION_DECLINED',


class AuthMessageId(Enum):
	INVALID_API_KEY = 'INVALID_API_KEY',
	INVALID_EMAIL = 'INVALID_EMAIL',
	INVALID_LEGACY_MIGRATION = 'INVALID_LEGACY_MIGRATION',
	INVALID_PASSWORD = 'INVALID_PASSWORD',
	INVALID_SCOPE = 'INVALID_SCOPE',
	INVALID_SECRET = 'INVALID_SECRET',
	INVALID_TOKEN = 'INVALID_TOKEN',
	MIGRATE_FROM_COGNITO = 'MIGRATE_FROM_COGNITO',
	NO_ACCESS_TOKEN = 'NO_ACCESS_TOKEN',
	NO_REFRESH_TOKEN = 'NO_REFRESH_TOKEN',
	RESET_PASSWORD = 'RESET_PASSWORD',
	RESET_SECRET = 'RESET_SECRET',
	SUSPENDED_OR_INACTIVE = 'SUSPENDED_OR_INACTIVE',
	TOKEN_EXPIRED = 'TOKEN_EXPIRED',
	TRY_AGAIN = 'TRY_AGAIN',
	UNABLE_TO_CONFIRM_EMAIL = 'UNABLE_TO_CONFIRM_EMAIL',
	UNCONFIRMED_EMAIL = 'UNCONFIRMED_EMAIL',


class AuthTokenScope(Enum):
	API = 'API',
	CONFIRM_EMAIL = 'CONFIRM_EMAIL',
	NEW_PASSWORD = 'NEW_PASSWORD',
	NO_SESSION = 'NO_SESSION',


class PricePlanName(Enum):
	FREE = 'free',
	ADVANCED = 'advanced',
	PRO = 'pro',
	ENTERPRISE_CUSTOM = 'enterpriseCustom',
	UNLIMITED = 'unlimited',


class PricePlanPaymentPeriod(Enum):
	MONTHLY = 'monthly',
	ANNUAL = 'annual',


class PricePlanReporting(Enum):
	BASIC = 'basic',
	ADVANCED = 'advanced',
	basic = 'basic',
	advance = 'advanced',


class ProjectStatus(Enum):
	ACTIVE = 'ACTIVE',
	SUSPENDED = 'SUSPENDED',


class QrCodeCornerDotTypes(Enum):
	dot = 'dot',
	square = 'square',


class QrCodeCornerSquareTypes(Enum):
	dot = 'dot',
	square = 'square',
	extra_rounded = 'extra-rounded',


class QrCodeDotTypes(Enum):
	classy = 'classy',
	classy_rounded = 'classy-rounded',
	dots = 'dots',
	extra_rounded = 'extra-rounded',
	rounded = 'rounded',
	square = 'square',


class QrCodeDynamicRedirectType(Enum):
	NO_SCAN_ID = 'NO_SCAN_ID',
	SCAN_ID_IN_PATH_PARAMETER = 'SCAN_ID_IN_PATH_PARAMETER',
	SCAN_ID_IN_QUERY_STRING_PARAMETER = 'SCAN_ID_IN_QUERY_STRING_PARAMETER',


class QrCodeErrorCorrectionLevel(Enum):
	L = 'L',
	M = 'M',
	Q = 'Q',
	H = 'H',


class QrCodeGradientTypes(Enum):
	linear = 'linear',
	radial = 'radial',


class QrCodeIntentType(Enum):
	STATIC_REDIRECT = 'STATIC_REDIRECT',
	DYNAMIC_REDIRECT = 'DYNAMIC_REDIRECT',
	DYNAMIC_REDIRECT_TO_APP = 'DYNAMIC_REDIRECT_TO_APP',


class QrCodeLocatorKeyType(Enum):
	SHORT_URL = 'SHORT_URL',
	HASHED_ID = 'HASHED_ID',
	SECURE_ID = 'SECURE_ID',


class QrCodeStatus(Enum):
	ACTIVE = 'ACTIVE',
	INACTIVE = 'INACTIVE',
	SUSPENDED = 'SUSPENDED',


class QrCodeType(Enum):
	PNG = 'PNG',
	JPEG = 'JPEG',
	SVG = 'SVG',
	png = 'png',
	jpeg = 'jpeg',
	svg = 'svg',


class UserCredentialsStatus(Enum):
	COMPROMISED = 'COMPROMISED',
	CONFIRMED = 'CONFIRMED',
	LEGACY = 'LEGACY',
	NEW_EMAIL = 'NEW_EMAIL',
	NEW_EMAIL_CONFIRMED = 'NEW_EMAIL_CONFIRMED',
	NEW_PASSWORD = 'NEW_PASSWORD',
	SUSPENDED = 'SUSPENDED',
	UNCONFIRMED = 'UNCONFIRMED',


class UserGroups(Enum):
	appuser = 'appuser',
	appadmin = 'appadmin',


class UserSettingsDomain(Enum):
	DASHBOARD = 'DASHBOARD',


# APPLICATION ENTITIES

@nested_dataclass(kw_only=True)
class Entity:


	pass


@nested_dataclass(kw_only=True)
class DdbEntity:
	created: str | datetime | int = None
	modified: str | datetime | int = None
	deleted: str | datetime | int = None


@nested_dataclass(kw_only=True)
class Account:
	account_id: str
	status: AccountStatus
	collect_tax_info: bool
	stripe_customer_id: str
	needs_payment_update: bool
	project_count: int
	scan_count: int
	asset_count: int
	contact_count: int
	dynamic_qr_code_count: int
	static_qr_code_count: int
	created: str | datetime | int = None
	modified: str | datetime | int = None
	deleted: str | datetime | int = None
	company_name: str = None
	last_scan_id: str = None


@nested_dataclass(kw_only=True)
class PricePlan:
	price_plan_id: str
	stripe_customer_id: str
	data_export: bool
	reporting: PricePlanReporting
	role_based_management: bool
	name: str
	total_scans: int
	projects: int
	qr_codes: int
	users: int
	annual_price: int
	monthly_price: int
	stripe_subscription_id: str
	subscription_item_id: str
	created: str | datetime | int = None
	modified: str | datetime | int = None
	deleted: str | datetime | int = None
	payment_period: str = None
	stripe_plan_id: str = None


@nested_dataclass(kw_only=True)
class PricePlanPeriod:
	price_plan_id: str
	period: str | datetime | int
	period_end_date: str | datetime | int
	projects: int
	projects_created: int
	projects_remaining: int
	qr_codes: int
	qr_codes_created: int
	qr_codes_remaining: int
	qr_scans_remaining: int
	scans_used: int
	users: int
	users_created: int
	users_remaining: int
	created: str | datetime | int = None
	modified: str | datetime | int = None
	deleted: str | datetime | int = None


@nested_dataclass(kw_only=True)
class DdbAggregatedEntity:
	created: str | datetime | int = None
	modified: str | datetime | int = None
	deleted: str | datetime | int = None


@nested_dataclass(kw_only=True)
class ContactMailingAddress:
	address: str
	city: str
	province_or_state: str
	postal_or_zip: str
	country: str


@nested_dataclass(kw_only=True)
class ContactConsent:
	consented: bool
	consented_at: str | datetime | int
	url: str


@nested_dataclass(kw_only=True)
class Scan:
	asset_id: str
	scan_id: str
	project_id: str
	scan_time: str | datetime | int
	created: str | datetime | int = None
	modified: str | datetime | int = None
	deleted: str | datetime | int = None
	qr_code_id: str = None
	ip_address: str = None
	browser_name: str = None
	browser_version: str = None
	cpu_architecture: str = None
	device_model: str = None
	device_type: str = None
	device_vendor: str = None
	engine_name: str = None
	engine_version: str = None
	location_city_name: str = None
	location_country_code: str = None
	location_country_name: str = None
	location_latitude: str = None
	location_longitude: str = None
	location_postal_code: str = None
	location_region_code: str = None
	location_region_name: str = None
	location_time_zone: str = None
	os_name: str = None
	os_version: str = None
	user_agent: str = None


@nested_dataclass(kw_only=True)
class QrCodeImageOptions:
	error_correction_level: QrCodeErrorCorrectionLevel
	format: QrCodeType
	margin: int
	scale: int
	width: int
	data_url: bool
	foreground: str
	background: str
	version: int = None
	dark_color: str = None
	light_color: str = None
	logo: str = None
	corner_dot_type: QrCodeCornerDotTypes = None
	corner_dot_color: str = None
	dot_type: QrCodeDotTypes = None
	corner_square_type: QrCodeCornerSquareTypes = None
	corner_square_color: str = None
	background_gradient_type: QrCodeGradientTypes = None
	background_gradient_colors: str = None
	background_gradient_rotation: int = None
	foreground_gradient_type: QrCodeGradientTypes = None
	foreground_gradient_colors: str = None
	foreground_gradient_rotation: int = None


@nested_dataclass(kw_only=True)
class NestedQrCode:
	intent_type: QrCodeIntentType
	dynamic_redirect_type: QrCodeDynamicRedirectType
	locator_key_type: QrCodeLocatorKeyType
	image_options: QrCodeImageOptions
	valid_from: str | datetime | int = None
	valid_to: str | datetime | int = None
	intent: str = None
	status: QrCodeStatus = None
	intent_state: dict = None


@nested_dataclass(kw_only=True)
class NestedAsset:
	name: str
	description: str = None
	custom_attributes: dict = None
	qr_codes: List[NestedQrCode] = None


@nested_dataclass(kw_only=True)
class QrCode:
	asset_id: str
	qr_code_id: str
	locator_key_type: QrCodeLocatorKeyType
	locator_key: str
	intent_type: QrCodeIntentType
	dynamic_redirect_type: QrCodeDynamicRedirectType
	status: QrCodeStatus
	scan_count: int
	image_options: QrCodeImageOptions
	created: str | datetime | int = None
	modified: str | datetime | int = None
	deleted: str | datetime | int = None
	valid_from: str | datetime | int = None
	valid_to: str | datetime | int = None
	intent: str = None
	intent_state: dict = None


@nested_dataclass(kw_only=True)
class QrCodeImage:
	data: str
	options: QrCodeImageOptions


@nested_dataclass(kw_only=True)
class ResponseQrCode:
	asset_id: str
	qr_code_id: str
	locator_key_type: QrCodeLocatorKeyType
	locator_key: str
	intent_type: QrCodeIntentType
	dynamic_redirect_type: QrCodeDynamicRedirectType
	status: QrCodeStatus
	scan_count: int
	image: QrCodeImage
	valid_from: str | datetime | int = None
	valid_to: str | datetime | int = None
	intent: str = None
	intent_state: dict = None


@nested_dataclass(kw_only=True)
class Contact:
	contact_id: str
	account_id: str
	first_name: str
	middle_name: str
	last_name: str
	nickname: str
	created: str | datetime | int = None
	modified: str | datetime | int = None
	deleted: str | datetime | int = None
	email_address: str = None
	cell_phone: str = None
	mailing_address: ContactMailingAddress = None
	consent: List[ContactConsent] = None
	custom_attributes: dict = None
	last_sms: str = None


@nested_dataclass(kw_only=True)
class SmsResponse:
	sms_id: str
	twilio_phone: str
	contact_phone: str
	body: str


@nested_dataclass(kw_only=True)
class User:
	user_id: str
	email: str
	first_name: str
	middle_name: str
	last_name: str
	created: str | datetime | int = None
	modified: str | datetime | int = None
	deleted: str | datetime | int = None


@nested_dataclass(kw_only=True)
class Response:
	user_id: str
	response_id: str
	name: str
	code: int
	created: str | datetime | int = None
	modified: str | datetime | int = None
	deleted: str | datetime | int = None
	message: str = None
	body: DdbEntity = None
	request: str = None
	data: dict = None
	source: str = None
	stack: list = None


@nested_dataclass(kw_only=True)
class AccountEmailContact:
	account_id: str
	email: str
	contact_id: str
	created: str | datetime | int = None
	modified: str | datetime | int = None
	deleted: str | datetime | int = None


@nested_dataclass(kw_only=True)
class AccountInvitation:
	invitation_id: str
	account_id: str
	email: str
	first_name: str
	last_name: str
	senders_user_id: str
	senders_first_name: str
	senders_last_name: str
	user_role: AccountUserRole
	created: str | datetime | int = None
	modified: str | datetime | int = None
	deleted: str | datetime | int = None
	company_name: str = None
	expires_at: str | datetime | int = None


@nested_dataclass(kw_only=True)
class AccountPhoneContact:
	account_id: str
	phone: str
	contact_id: str
	created: str | datetime | int = None
	modified: str | datetime | int = None
	deleted: str | datetime | int = None


@nested_dataclass(kw_only=True)
class AccountResponse(Account):
	account_id: str
	status: AccountStatus
	collect_tax_info: bool
	stripe_customer_id: str
	needs_payment_update: bool
	project_count: int
	scan_count: int
	asset_count: int
	contact_count: int
	dynamic_qr_code_count: int
	static_qr_code_count: int
	price_plan: PricePlan
	current_period: PricePlanPeriod
	created: str | datetime | int = None
	modified: str | datetime | int = None
	deleted: str | datetime | int = None
	company_name: str = None
	last_scan_id: str = None


@nested_dataclass(kw_only=True)
class AccountScan:
	account_id: str
	scan_id: str
	asset_id: str
	created: str | datetime | int = None
	modified: str | datetime | int = None
	deleted: str | datetime | int = None


@nested_dataclass(kw_only=True)
class AccountUser:
	account_id: str
	user_id: str
	user_role: AccountUserRole
	created: str | datetime | int = None
	modified: str | datetime | int = None
	deleted: str | datetime | int = None


@nested_dataclass(kw_only=True)
class ApiKey:
	api_key_id: str
	key: str
	name: str
	created: str | datetime | int = None
	modified: str | datetime | int = None
	deleted: str | datetime | int = None
	description: str = None


@nested_dataclass(kw_only=True)
class ApiKeyCredentials:
	key: str
	api_key_id: str
	status: str
	name: str
	invalid_attempt_count: int
	created: str | datetime | int = None
	modified: str | datetime | int = None
	deleted: str | datetime | int = None
	secret: str = None
	description: str = None


@nested_dataclass(kw_only=True)
class ApiKeySessionResponseBody:
	entity_type: str
	api_key_id: str
	scope: AuthTokenScope
	expires: str | datetime | int


@nested_dataclass(kw_only=True)
class Asset:
	asset_id: str
	project_id: str
	name: str
	scan_count: int
	dynamic_qr_code_count: int
	static_qr_code_count: int
	created: str | datetime | int = None
	modified: str | datetime | int = None
	deleted: str | datetime | int = None
	description: str = None
	custom_attributes: dict = None
	last_scan_id: str = None


@nested_dataclass(kw_only=True)
class AssetContact:
	asset_id: str
	contact_id: str
	created: str | datetime | int = None
	modified: str | datetime | int = None
	deleted: str | datetime | int = None
	type: str = None


@nested_dataclass(kw_only=True)
class EmailInvitation:
	email: str
	account_id: str
	invitation_id: str
	created: str | datetime | int = None
	modified: str | datetime | int = None
	deleted: str | datetime | int = None
	expires_at: str | datetime | int = None


@nested_dataclass(kw_only=True)
class ExportedScan(Scan):
	asset_id: str
	scan_id: str
	project_id: str
	scan_time: str | datetime | int
	asset_name: str
	created: str | datetime | int = None
	modified: str | datetime | int = None
	deleted: str | datetime | int = None
	qr_code_id: str = None
	ip_address: str = None
	browser_name: str = None
	browser_version: str = None
	cpu_architecture: str = None
	device_model: str = None
	device_type: str = None
	device_vendor: str = None
	engine_name: str = None
	engine_version: str = None
	location_city_name: str = None
	location_country_code: str = None
	location_country_name: str = None
	location_latitude: str = None
	location_longitude: str = None
	location_postal_code: str = None
	location_region_code: str = None
	location_region_name: str = None
	location_time_zone: str = None
	os_name: str = None
	os_version: str = None
	user_agent: str = None


@nested_dataclass(kw_only=True)
class NestedContact:
	first_name: str = None
	middle_name: str = None
	last_name: str = None
	nickname: str = None
	cell_phone: str = None
	email_address: str = None
	consent: List[ContactConsent] = None
	mailing_address: ContactMailingAddress = None
	asset: NestedAsset = None
	type: str = None
	custom_attributes: dict = None


@nested_dataclass(kw_only=True)
class PhoneSession:
	contact_phone: str
	contact_id: str
	twilio_phone: str
	sms_id: str
	created: str | datetime | int = None
	modified: str | datetime | int = None
	deleted: str | datetime | int = None
	expires_at: str | datetime | int = None


@nested_dataclass(kw_only=True)
class Project:
	project_id: str
	status: ProjectStatus
	name: str
	scan_count: int
	asset_count: int
	contact_count: int
	dynamic_qr_code_count: int
	static_qr_code_count: int
	created: str | datetime | int = None
	modified: str | datetime | int = None
	deleted: str | datetime | int = None
	description: str = None
	company_name: str = None
	last_scan_id: str = None


@nested_dataclass(kw_only=True)
class ProjectAccount:
	project_id: str
	account_id: str
	created: str | datetime | int = None
	modified: str | datetime | int = None
	deleted: str | datetime | int = None


@nested_dataclass(kw_only=True)
class ProjectContact:
	project_id: str
	contact_id: str
	created: str | datetime | int = None
	modified: str | datetime | int = None
	deleted: str | datetime | int = None


@nested_dataclass(kw_only=True)
class ProjectEmailContact:
	project_id: str
	email: str
	contact_id: str
	created: str | datetime | int = None
	modified: str | datetime | int = None
	deleted: str | datetime | int = None


@nested_dataclass(kw_only=True)
class ProjectPhoneContact:
	project_id: str
	phone: str
	contact_id: str
	created: str | datetime | int = None
	modified: str | datetime | int = None
	deleted: str | datetime | int = None


@nested_dataclass(kw_only=True)
class ProjectScan:
	project_id: str
	scan_id: str
	asset_id: str
	created: str | datetime | int = None
	modified: str | datetime | int = None
	deleted: str | datetime | int = None


@nested_dataclass(kw_only=True)
class QrCodeLocator:
	locator_key: str
	qr_code_id: str
	created: str | datetime | int = None
	modified: str | datetime | int = None
	deleted: str | datetime | int = None


@nested_dataclass(kw_only=True)
class QrCodeNamed(QrCode):
	asset_id: str
	qr_code_id: str
	locator_key_type: QrCodeLocatorKeyType
	locator_key: str
	intent_type: QrCodeIntentType
	dynamic_redirect_type: QrCodeDynamicRedirectType
	status: QrCodeStatus
	scan_count: int
	image_options: QrCodeImageOptions
	name: str
	created: str | datetime | int = None
	modified: str | datetime | int = None
	deleted: str | datetime | int = None
	valid_from: str | datetime | int = None
	valid_to: str | datetime | int = None
	intent: str = None
	intent_state: dict = None


@nested_dataclass(kw_only=True)
class ResponseAsset:
	asset_id: str
	project_id: str
	name: str
	created: str | datetime | int = None
	modified: str | datetime | int = None
	deleted: str | datetime | int = None
	description: str = None
	custom_attributes: dict = None
	qr_codes: List[ResponseQrCode] = None


@nested_dataclass(kw_only=True)
class ResponseBodyUser:
	email: str
	first_name: str
	middle_name: str
	last_name: str
	user_role: AccountUserRole
	created: str | datetime | int
	user_id: str = None
	invitation_id: str = None
	expires_at: str | datetime | int = None


@nested_dataclass(kw_only=True)
class ResponseContact(Contact):
	contact_id: str
	account_id: str
	first_name: str
	middle_name: str
	last_name: str
	nickname: str
	created: str | datetime | int = None
	modified: str | datetime | int = None
	deleted: str | datetime | int = None
	email_address: str = None
	cell_phone: str = None
	mailing_address: ContactMailingAddress = None
	consent: List[ContactConsent] = None
	custom_attributes: dict = None
	last_sms: str = None
	type: str = None


@nested_dataclass(kw_only=True)
class ScanContact:
	scan_id: str
	contact_id: str
	created: str | datetime | int = None
	modified: str | datetime | int = None
	deleted: str | datetime | int = None


@nested_dataclass(kw_only=True)
class ScanContactAccountIndex:
	account_id: str
	indexed_entity_name: str
	contact_id: str
	scan_id: str
	asset_id: str
	created: str | datetime | int = None
	modified: str | datetime | int = None
	deleted: str | datetime | int = None


@nested_dataclass(kw_only=True)
class ScanContactProjectIndex:
	project_id: str
	indexed_entity_name: str
	contact_id: str
	scan_id: str
	asset_id: str
	created: str | datetime | int = None
	modified: str | datetime | int = None
	deleted: str | datetime | int = None


@nested_dataclass(kw_only=True)
class Sms:
	sms_id: str
	contact_id: str
	from_: str
	to: str
	body: str
	project_id: str
	inbound: bool
	price_unit: str
	created: str | datetime | int = None
	modified: str | datetime | int = None
	deleted: str | datetime | int = None
	sms_template_name: str = None
	delivered: bool = None
	delivered_at: str | datetime | int = None
	price: int = None
	status: str = None
	responses: List[SmsResponse] = None


@nested_dataclass(kw_only=True)
class SmsTemplate:
	project_id: str
	sms_template_name: str
	created: str | datetime | int = None
	modified: str | datetime | int = None
	deleted: str | datetime | int = None
	body: str = None
	response_url: str = None
	status_url: str = None


@nested_dataclass(kw_only=True)
class UserSessionResponseBody:
	entity_type: str
	user_id: str
	scope: AuthTokenScope
	expires: str | datetime | int
	user: User = None


@nested_dataclass(kw_only=True)
class UserSettings:
	user_id: str
	path: UserSettingsDomain
	created: str | datetime | int = None
	modified: str | datetime | int = None
	deleted: str | datetime | int = None
	last_selected_account_id: str = None




#HANDLER INTERFACE TYPES

@nested_dataclass(kw_only=True)
class CreateProjectByAccountIdPathParameters:
	account_id: str


@nested_dataclass(kw_only=True)
class CreateProjectByAccountIdRequestBody:
	name: str
	description: str = None
	company_name: str = None


@nested_dataclass(kw_only=True)
class CreateProjectByAccountIdResponseBody:
	entity_type: str
	account_id: str
	project: Project


@nested_dataclass(kw_only=True)
class DeleteContactsByAccountIdPathParameters:
	account_id: str


@nested_dataclass(kw_only=True)
class DeleteContactsByAccountIdQueryStringParameters:
	email_address: str = None
	cell_phone: str = None


@nested_dataclass(kw_only=True)
class DeleteContactsByAccountIdResponseBody:
	entity_type: str
	account_id: str
	contacts: List[Contact]


@nested_dataclass(kw_only=True)
class GetAssetsByAccountIdPathParameters:
	account_id: str


@nested_dataclass(kw_only=True)
class GetAssetsByAccountIdQueryStringParameters:
	limit: int = None
	last_key: str = None
	name: str = None


@nested_dataclass(kw_only=True)
class GetAssetsByAccountIdResponseBody:
	entity_type: str
	account_id: str
	number_of_assets: int
	assets: List[Asset]
	last_key: str = None


@nested_dataclass(kw_only=True)
class GetContactsByAccountIdPathParameters:
	account_id: str


@nested_dataclass(kw_only=True)
class GetContactsByAccountIdQueryStringParameters:
	asset_name: str = None
	contact_name: str = None
	email: str = None
	phone: str = None
	limit: int = None
	last_key: str = None


@nested_dataclass(kw_only=True)
class GetContactsByAccountIdResponseBody:
	entity_type: str
	account_id: str
	contacts: List[Contact]
	number_of_contacts: int
	last_key: str = None


@nested_dataclass(kw_only=True)
class GetProjectsByAccountIdPathParameters:
	account_id: str


@nested_dataclass(kw_only=True)
class GetProjectsByAccountIdQueryStringParameters:
	last_key: str = None
	next: str = None
	limit: int = None


@nested_dataclass(kw_only=True)
class GetProjectsByAccountIdResponseBody:
	entity_type: str
	account_id: str
	number_of_projects: int
	projects: List[Project]
	last_key: str = None
	next: str = None


@nested_dataclass(kw_only=True)
class GetQrCodesByAccountIdPathParameters:
	account_id: str


@nested_dataclass(kw_only=True)
class GetQrCodesByAccountIdQueryStringParameters:
	limit: int = None
	last_key: str = None
	asset_name: str = None


@nested_dataclass(kw_only=True)
class GetQrCodesByAccountIdResponseBody:
	entity_type: str
	account_id: str
	qr_codes: List[QrCodeNamed]
	number_of_qr_codes: int
	last_key: str = None


@nested_dataclass(kw_only=True)
class GetScansByAccountIdPathParameters:
	account_id: str


@nested_dataclass(kw_only=True)
class GetScansByAccountIdQueryStringParameters:
	limit: int = None
	last_key: str = None
	asset_name: str = None
	contact_id: str = None


@nested_dataclass(kw_only=True)
class GetScansByAccountIdResponseBody:
	entity_type: str
	account_id: str
	scans: List[Scan]
	number_of_scans: int
	last_key: str = None


@nested_dataclass(kw_only=True)
class CreateContactByAssetIdPathParameters:
	asset_id: str


@nested_dataclass(kw_only=True)
class CreateContactByAssetIdRequestBody:
	first_name: str = None
	middle_name: str = None
	last_name: str = None
	nickname: str = None
	cell_phone: str = None
	email_address: str = None
	consent: List[ContactConsent] = None
	mailing_address: ContactMailingAddress = None
	type: str = None
	custom_attributes: dict = None


@nested_dataclass(kw_only=True)
class CreateContactByAssetIdResponseBody:
	entity_type: str
	asset_id: str
	asset: Asset
	contact: Contact
	project_contact: ProjectContact
	asset_contact: AssetContact


@nested_dataclass(kw_only=True)
class CreateQrCodeByAssetIdPathParameters:
	asset_id: str


@nested_dataclass(kw_only=True)
class CreateQrCodeByAssetIdRequestBody:
	intent_type: QrCodeIntentType
	dynamic_redirect_type: QrCodeDynamicRedirectType
	locator_key_type: QrCodeLocatorKeyType
	image_options: QrCodeImageOptions
	intent: str = None
	intent_state: dict = None
	status: QrCodeStatus = None
	valid_from: str | datetime | int = None
	valid_to: str | datetime | int = None


@nested_dataclass(kw_only=True)
class CreateQrCodeByAssetIdResponseBody:
	entity_type: str
	asset_id: str
	asset: Asset
	qr_code: ResponseQrCode
	qr_code_id: str
	locator_key: str


@nested_dataclass(kw_only=True)
class DeleteAssetPathParameters:
	asset_id: str


@nested_dataclass(kw_only=True)
class DeleteAssetResponseBody:
	entity_type: str
	asset: Asset


@nested_dataclass(kw_only=True)
class GetAssetPathParameters:
	asset_id: str


@nested_dataclass(kw_only=True)
class GetAssetQueryStringParameters:
	version: int = None
	error_correction_level: QrCodeErrorCorrectionLevel = None
	format: QrCodeType = None
	margin: int = None
	scale: int = None
	width: int = None
	data_url: bool = None
	dark_color: str = None
	light_color: str = None
	foreground: str = None
	background: str = None
	logo: str = None
	corner_dot_type: QrCodeCornerDotTypes = None
	corner_dot_color: str = None
	dot_type: QrCodeDotTypes = None
	corner_square_type: QrCodeCornerSquareTypes = None
	corner_square_color: str = None
	background_gradient_type: QrCodeGradientTypes = None
	background_gradient_colors: str = None
	background_gradient_rotation: int = None
	foreground_gradient_type: QrCodeGradientTypes = None
	foreground_gradient_colors: str = None
	foreground_gradient_rotation: int = None


@nested_dataclass(kw_only=True)
class GetAssetResponseBody:
	entity_type: str
	asset_id: str
	asset: ResponseAsset


@nested_dataclass(kw_only=True)
class GetContactsByAssetIdPathParameters:
	asset_id: str


@nested_dataclass(kw_only=True)
class GetContactsByAssetIdQueryStringParameters:
	last_key: str = None
	limit: int = None


@nested_dataclass(kw_only=True)
class GetContactsByAssetIdResponseBody:
	entity_type: str
	asset_id: str
	number_of_contacts: int
	contacts: List[Contact]
	asset_contacts: List[AssetContact]
	last_key: str = None


@nested_dataclass(kw_only=True)
class GetQrCodesByAssetIdPathParameters:
	asset_id: str


@nested_dataclass(kw_only=True)
class GetQrCodesByAssetIdQueryStringParameters:
	version: int = None
	error_correction_level: QrCodeErrorCorrectionLevel = None
	format: QrCodeType = None
	margin: int = None
	scale: int = None
	width: int = None
	data_url: bool = None
	dark_color: str = None
	light_color: str = None
	foreground: str = None
	background: str = None
	logo: str = None
	corner_dot_type: QrCodeCornerDotTypes = None
	corner_dot_color: str = None
	dot_type: QrCodeDotTypes = None
	corner_square_type: QrCodeCornerSquareTypes = None
	corner_square_color: str = None
	background_gradient_type: QrCodeGradientTypes = None
	background_gradient_colors: str = None
	background_gradient_rotation: int = None
	foreground_gradient_type: QrCodeGradientTypes = None
	foreground_gradient_colors: str = None
	foreground_gradient_rotation: int = None
	limit: int = None
	last_key: str = None


@nested_dataclass(kw_only=True)
class GetQrCodesByAssetIdResponseBody:
	entity_type: str
	asset_id: str
	number_of_qr_codes: int
	qr_codes: List[ResponseQrCode]
	last_key: str = None


@nested_dataclass(kw_only=True)
class GetScansByAssetIdPathParameters:
	asset_id: str


@nested_dataclass(kw_only=True)
class GetScansByAssetIdQueryStringParameters:
	last_key: str = None
	limit: int = None


@nested_dataclass(kw_only=True)
class GetScansByAssetIdResponseBody:
	entity_type: str
	asset_id: str
	number_of_scans: int
	scans: List[Scan]
	last_key: str = None


@nested_dataclass(kw_only=True)
class LinkContactToAssetPathParameters:
	asset_id: str
	contact_id: str


@nested_dataclass(kw_only=True)
class LinkContactToAssetRequestBody:
	type: str = None


@nested_dataclass(kw_only=True)
class LinkContactToAssetResponseBody:
	entity_type: str
	asset_contact: AssetContact
	project_contact: ProjectContact


@nested_dataclass(kw_only=True)
class UnlinkContactToAssetPathParameters:
	asset_id: str
	contact_id: str


@nested_dataclass(kw_only=True)
class UpdateAssetPathParameters:
	asset_id: str


@nested_dataclass(kw_only=True)
class UpdateAssetRequestBody:
	description: str = None
	custom_attributes: dict = None


@nested_dataclass(kw_only=True)
class UpdateAssetResponseBody:
	entity_type: str
	asset_id: str
	asset: Asset


@nested_dataclass(kw_only=True)
class DeleteContactPathParameters:
	contact_id: str


@nested_dataclass(kw_only=True)
class DeleteContactResponseBody:
	entity_type: str
	contact: Contact


@nested_dataclass(kw_only=True)
class GetContactPathParameters:
	contact_id: str


@nested_dataclass(kw_only=True)
class GetContactResponseBody:
	entity_type: str
	contact: Contact


@nested_dataclass(kw_only=True)
class UpdateContactPathParameters:
	contact_id: str


@nested_dataclass(kw_only=True)
class UpdateContactRequestBody:
	first_name: str = None
	middle_name: str = None
	last_name: str = None
	nickname: str = None
	cell_phone: str = None
	email_address: str = None
	consent: List[ContactConsent] = None
	mailing_address: ContactMailingAddress = None
	custom_attributes: dict = None


@nested_dataclass(kw_only=True)
class UpdateContactResponseBody:
	entity_type: str
	contact: Contact


@nested_dataclass(kw_only=True)
class CreateAssetByProjectIdPathParameters:
	project_id: str


@nested_dataclass(kw_only=True)
class CreateAssetByProjectIdRequestBody(NestedAsset):
	name: str
	description: str = None
	custom_attributes: dict = None
	qr_codes: List[NestedQrCode] = None


@nested_dataclass(kw_only=True)
class CreateAssetByProjectIdResponseBody:
	entity_type: str
	project_id: str
	asset: ResponseAsset


@nested_dataclass(kw_only=True)
class CreateAssetsByProjectIdPathParameters:
	project_id: str


@nested_dataclass(kw_only=True)
class CreateAssetsByProjectIdRequestBody:
	assets: List[NestedAsset]


@nested_dataclass(kw_only=True)
class CreateAssetsByProjectIdResponseBody:
	entity_type: str
	project_id: str
	assets: List[ResponseAsset]
	number_of_assets: int


@nested_dataclass(kw_only=True)
class CreateContactByProjectIdPathParameters:
	project_id: str


@nested_dataclass(kw_only=True)
class CreateContactByProjectIdRequestBody:
	first_name: str = None
	middle_name: str = None
	last_name: str = None
	nickname: str = None
	cell_phone: str = None
	email_address: str = None
	consent: List[ContactConsent] = None
	mailing_address: ContactMailingAddress = None
	asset: NestedAsset = None
	type: str = None
	custom_attributes: dict = None


@nested_dataclass(kw_only=True)
class CreateContactByProjectIdResponseBody:
	entity_type: str
	project_id: str
	contact: Contact
	project_contact: ProjectContact
	asset: Asset = None
	qr_codes: List[QrCode] = None
	asset_contact: AssetContact = None


@nested_dataclass(kw_only=True)
class CreateContactsByProjectIdPathParameters:
	project_id: str


@nested_dataclass(kw_only=True)
class CreateContactsByProjectIdRequestBody:
	contacts: List[NestedContact]


@nested_dataclass(kw_only=True)
class CreateContactsByProjectIdResponseBody:
	entity_type: str
	project_id: str
	contacts: list
	number_of_contacts: int


@nested_dataclass(kw_only=True)
class CreateSmsTemplateByProjectIdPathParameters:
	project_id: str


@nested_dataclass(kw_only=True)
class CreateSmsTemplateByProjectIdRequestBody:
	sms_template_name: str
	body: str = None
	response_url: str = None
	status_url: str = None


@nested_dataclass(kw_only=True)
class CreateSmsTemplateByProjectIdResponseBody:
	entity_type: str
	sms_template: SmsTemplate


@nested_dataclass(kw_only=True)
class DeleteContactsByProjectIdPathParameters:
	project_id: str


@nested_dataclass(kw_only=True)
class DeleteContactsByProjectIdQueryStringParameters:
	email_address: str = None
	cell_phone: str = None


@nested_dataclass(kw_only=True)
class DeleteContactsByProjectIdResponseBody:
	entity_type: str
	project_id: str
	contacts: List[Contact]


@nested_dataclass(kw_only=True)
class DeleteSmsTemplateByProjectIdPathParameters:
	project_id: str
	sms_template_name: str


@nested_dataclass(kw_only=True)
class DeleteSmsTemplateByProjectIdResponseBody:
	entity_type: str
	project_id: str
	sms_template_name: str = None
	body: str = None
	response_url: str = None
	status_url: str = None


@nested_dataclass(kw_only=True)
class GetAssetsByProjectIdPathParameters:
	project_id: str


@nested_dataclass(kw_only=True)
class GetAssetsByProjectIdQueryStringParameters:
	limit: int = None
	last_key: str = None
	name: str = None


@nested_dataclass(kw_only=True)
class GetAssetsByProjectIdResponseBody:
	entity_type: str
	project_id: str
	number_of_assets: int
	assets: List[Asset]
	last_key: str = None


@nested_dataclass(kw_only=True)
class GetContactsByProjectIdPathParameters:
	project_id: str


@nested_dataclass(kw_only=True)
class GetContactsByProjectIdQueryStringParameters:
	asset_name: str = None
	contact_name: str = None
	email: str = None
	phone: str = None
	limit: int = None
	last_key: str = None


@nested_dataclass(kw_only=True)
class GetContactsByProjectIdResponseBody:
	entity_type: str
	project_id: str
	number_of_contacts: int
	contacts: List[Contact]
	last_key: str = None


@nested_dataclass(kw_only=True)
class GetProjectByProjectIdPathParameters:
	project_id: str


@nested_dataclass(kw_only=True)
class GetProjectByProjectIdResponseBody:
	entity_type: str
	project: Project


@nested_dataclass(kw_only=True)
class GetQrCodesByProjectIdPathParameters:
	project_id: str


@nested_dataclass(kw_only=True)
class GetQrCodesByProjectIdQueryStringParameters:
	limit: int = None
	last_key: str = None
	asset_name: str = None


@nested_dataclass(kw_only=True)
class GetQrCodesByProjectIdResponseBody:
	entity_type: str
	project_id: str
	qr_codes: List[QrCodeNamed]
	number_of_qr_codes: int
	last_key: str = None


@nested_dataclass(kw_only=True)
class GetScansByProjectIdPathParameters:
	project_id: str


@nested_dataclass(kw_only=True)
class GetScansByProjectIdQueryStringParameters:
	limit: int = None
	last_key: str = None
	asset_name: str = None
	contact_id: str = None


@nested_dataclass(kw_only=True)
class GetScansByProjectIdResponseBody:
	entity_type: str
	project_id: str
	scans: List[Scan]
	number_of_scans: int
	last_key: str = None


@nested_dataclass(kw_only=True)
class GetSmsTemplateByProjectIdPathParameters:
	sms_template_name: str
	project_id: str


@nested_dataclass(kw_only=True)
class GetSmsTemplateByProjectIdResponseBody:
	entity_type: str
	project_id: str
	sms_template_name: str
	body: str = None
	response_url: str = None
	status_url: str = None


@nested_dataclass(kw_only=True)
class GetSmsTemplatesByProjectIdPathParameters:
	project_id: str


@nested_dataclass(kw_only=True)
class GetSmsTemplatesByProjectIdQueryStringParameters:
	last_key: str = None
	limit: int = None


@nested_dataclass(kw_only=True)
class GetSmsTemplatesByProjectIdResponseBody:
	entity_type: str
	project_id: str
	number_of_sms_templates: int
	sms_templates: List[SmsTemplate]
	last_key: str = None


@nested_dataclass(kw_only=True)
class UpdateProjectByProjectIdPathParameters:
	project_id: str


@nested_dataclass(kw_only=True)
class UpdateProjectByProjectIdRequestBody:
	status: ProjectStatus = None
	name: str = None
	description: str = None
	company_name: str = None


@nested_dataclass(kw_only=True)
class UpdateProjectByProjectIdResponseBody:
	entity_type: str
	project: Project


@nested_dataclass(kw_only=True)
class UpdateSmsTemplatePathParameters:
	project_id: str
	sms_template_name: str


@nested_dataclass(kw_only=True)
class UpdateSmsTemplateRequestBody:
	body: str = None
	response_url: str = None
	status_url: str = None


@nested_dataclass(kw_only=True)
class UpdateSmsTemplateResponseBody:
	entity_type: str
	project_id: str
	sms_template_name: str = None
	body: str = None
	response_url: str = None
	status_url: str = None


@nested_dataclass(kw_only=True)
class DeleteQrCodePathParameters:
	qr_code_id: str


@nested_dataclass(kw_only=True)
class DeleteQrCodeResponseBody:
	entity_type: str
	qr_code: QrCode


@nested_dataclass(kw_only=True)
class GetQrCodePathParameters:
	qr_code_id: str


@nested_dataclass(kw_only=True)
class GetQrCodeQueryStringParameters:
	version: int = None
	error_correction_level: QrCodeErrorCorrectionLevel = None
	format: QrCodeType = None
	margin: int = None
	scale: int = None
	width: int = None
	data_url: bool = None
	dark_color: str = None
	light_color: str = None
	foreground: str = None
	background: str = None
	logo: str = None
	corner_dot_type: QrCodeCornerDotTypes = None
	corner_dot_color: str = None
	dot_type: QrCodeDotTypes = None
	corner_square_type: QrCodeCornerSquareTypes = None
	corner_square_color: str = None
	background_gradient_type: QrCodeGradientTypes = None
	background_gradient_colors: str = None
	background_gradient_rotation: int = None
	foreground_gradient_type: QrCodeGradientTypes = None
	foreground_gradient_colors: str = None
	foreground_gradient_rotation: int = None


@nested_dataclass(kw_only=True)
class GetQrCodeResponseBody(ResponseQrCode):
	entity_type: str
	asset_id: str
	qr_code_id: str
	locator_key_type: QrCodeLocatorKeyType
	locator_key: str
	intent_type: QrCodeIntentType
	dynamic_redirect_type: QrCodeDynamicRedirectType
	status: QrCodeStatus
	scan_count: int
	image: QrCodeImage
	valid_from: str | datetime | int = None
	valid_to: str | datetime | int = None
	intent: str = None
	intent_state: dict = None


@nested_dataclass(kw_only=True)
class UpdateQrCodePathParameters:
	qr_code_id: str


@nested_dataclass(kw_only=True)
class UpdateQrCodeRequestBody:
	intent: str = None
	dynamic_redirect_type: QrCodeDynamicRedirectType = None
	intent_state: dict = None
	status: QrCodeStatus = None
	image_options: QrCodeImageOptions = None


@nested_dataclass(kw_only=True)
class UpdateQrCodeResponseBody:
	entity_type: str
	qr_code: ResponseQrCode


@nested_dataclass(kw_only=True)
class CreateContactByScanIdPathParameters:
	scan_id: str


@nested_dataclass(kw_only=True)
class CreateContactByScanIdRequestBody:
	first_name: str = None
	middle_name: str = None
	last_name: str = None
	nickname: str = None
	cell_phone: str = None
	email_address: str = None
	consent: List[ContactConsent] = None
	mailing_address: ContactMailingAddress = None
	type: str = None
	custom_attributes: dict = None


@nested_dataclass(kw_only=True)
class CreateContactByScanIdResponseBody:
	entity_type: str
	asset_id: str
	asset: Asset
	contact: Contact
	project_contact: ProjectContact
	asset_contact: AssetContact
	scan_contact: ScanContact


@nested_dataclass(kw_only=True)
class GetScanPathParameters:
	scan_id: str


@nested_dataclass(kw_only=True)
class GetScanResponseBody:
	entity_type: str
	qr_code: QrCode
	asset: Asset
	scan: Scan
	contacts: List[ResponseContact]


@nested_dataclass(kw_only=True)
class SendSmsByScanIdPathParameters:
	scan_id: str


@nested_dataclass(kw_only=True)
class SendSmsByScanIdRequestBody:
	contact_id: str
	sms_template_name: str = None
	body: str = None
	custom_variables: dict = None


@nested_dataclass(kw_only=True)
class SendSmsByScanIdResponseBody:
	entity_type: str
	sms: Sms


@nested_dataclass(kw_only=True)
class GetSessionRequestBody:
	key: str
	secret: str




#HANDLER REQUEST CLASSES

class CreateProjectByAccountIdRequest(RequestPost[CreateProjectByAccountIdPathParameters, undefined, CreateProjectByAccountIdRequestBody, CreateProjectByAccountIdResponseBody]):
	def __init__(self, session):
		super(CreateProjectByAccountIdRequest, self).__init__(session, route_segments =  [{"parm":"accountId","routePart":"accounts","sdkPartName":"account"},{"routePart":"projects","sdkPartName":"projects"}])


class DeleteContactsByAccountIdRequest(RequestDelete[DeleteContactsByAccountIdPathParameters, DeleteContactsByAccountIdQueryStringParameters, undefined, DeleteContactsByAccountIdResponseBody]):
	def __init__(self, session):
		super(DeleteContactsByAccountIdRequest, self).__init__(session, route_segments =  [{"parm":"accountId","routePart":"accounts","sdkPartName":"account"},{"routePart":"contacts/batch","sdkPartName":"contactsBatch"}])


class GetAssetsByAccountIdRequest(RequestGet[GetAssetsByAccountIdPathParameters, GetAssetsByAccountIdQueryStringParameters, undefined, GetAssetsByAccountIdResponseBody]):
	def __init__(self, session):
		super(GetAssetsByAccountIdRequest, self).__init__(session, route_segments =  [{"parm":"accountId","routePart":"accounts","sdkPartName":"account"},{"routePart":"assets","sdkPartName":"assets"}])


class GetContactsByAccountIdRequest(RequestGet[GetContactsByAccountIdPathParameters, GetContactsByAccountIdQueryStringParameters, undefined, GetContactsByAccountIdResponseBody]):
	def __init__(self, session):
		super(GetContactsByAccountIdRequest, self).__init__(session, route_segments =  [{"parm":"accountId","routePart":"accounts","sdkPartName":"account"},{"routePart":"contacts","sdkPartName":"contacts"}])


class GetProjectsByAccountIdRequest(RequestGet[GetProjectsByAccountIdPathParameters, GetProjectsByAccountIdQueryStringParameters, undefined, GetProjectsByAccountIdResponseBody]):
	def __init__(self, session):
		super(GetProjectsByAccountIdRequest, self).__init__(session, route_segments =  [{"parm":"accountId","routePart":"accounts","sdkPartName":"account"},{"routePart":"projects","sdkPartName":"projects"}])


class GetQrCodesByAccountIdRequest(RequestGet[GetQrCodesByAccountIdPathParameters, GetQrCodesByAccountIdQueryStringParameters, undefined, GetQrCodesByAccountIdResponseBody]):
	def __init__(self, session):
		super(GetQrCodesByAccountIdRequest, self).__init__(session, route_segments =  [{"parm":"accountId","routePart":"accounts","sdkPartName":"account"},{"routePart":"qrcodes","sdkPartName":"qrCodes"}])


class GetScansByAccountIdRequest(RequestGet[GetScansByAccountIdPathParameters, GetScansByAccountIdQueryStringParameters, undefined, GetScansByAccountIdResponseBody]):
	def __init__(self, session):
		super(GetScansByAccountIdRequest, self).__init__(session, route_segments =  [{"parm":"accountId","routePart":"accounts","sdkPartName":"account"},{"routePart":"scans","sdkPartName":"scans"}])


class CreateContactByAssetIdRequest(RequestPost[CreateContactByAssetIdPathParameters, undefined, CreateContactByAssetIdRequestBody, CreateContactByAssetIdResponseBody]):
	def __init__(self, session):
		super(CreateContactByAssetIdRequest, self).__init__(session, route_segments =  [{"parm":"assetId","routePart":"assets","sdkPartName":"asset"},{"routePart":"contacts","sdkPartName":"contacts"}])


class CreateQrCodeByAssetIdRequest(RequestPost[CreateQrCodeByAssetIdPathParameters, undefined, CreateQrCodeByAssetIdRequestBody, CreateQrCodeByAssetIdResponseBody]):
	def __init__(self, session):
		super(CreateQrCodeByAssetIdRequest, self).__init__(session, route_segments =  [{"parm":"assetId","routePart":"assets","sdkPartName":"asset"},{"routePart":"qrcodes","sdkPartName":"qrCodes"}])


class DeleteAssetRequest(RequestDelete[DeleteAssetPathParameters, undefined, undefined, DeleteAssetResponseBody]):
	def __init__(self, session):
		super(DeleteAssetRequest, self).__init__(session, route_segments =  [{"parm":"assetId","routePart":"assets","sdkPartName":"asset"}])


class GetAssetRequest(RequestGet[GetAssetPathParameters, GetAssetQueryStringParameters, undefined, GetAssetResponseBody]):
	def __init__(self, session):
		super(GetAssetRequest, self).__init__(session, route_segments =  [{"parm":"assetId","routePart":"assets","sdkPartName":"asset"}])


class GetContactsByAssetIdRequest(RequestGet[GetContactsByAssetIdPathParameters, GetContactsByAssetIdQueryStringParameters, undefined, GetContactsByAssetIdResponseBody]):
	def __init__(self, session):
		super(GetContactsByAssetIdRequest, self).__init__(session, route_segments =  [{"parm":"assetId","routePart":"assets","sdkPartName":"asset"},{"routePart":"contacts","sdkPartName":"contacts"}])


class GetQrCodesByAssetIdRequest(RequestGet[GetQrCodesByAssetIdPathParameters, GetQrCodesByAssetIdQueryStringParameters, undefined, GetQrCodesByAssetIdResponseBody]):
	def __init__(self, session):
		super(GetQrCodesByAssetIdRequest, self).__init__(session, route_segments =  [{"parm":"assetId","routePart":"assets","sdkPartName":"asset"},{"routePart":"qrcodes","sdkPartName":"qrCodes"}])


class GetScansByAssetIdRequest(RequestGet[GetScansByAssetIdPathParameters, GetScansByAssetIdQueryStringParameters, undefined, GetScansByAssetIdResponseBody]):
	def __init__(self, session):
		super(GetScansByAssetIdRequest, self).__init__(session, route_segments =  [{"parm":"assetId","routePart":"assets","sdkPartName":"asset"},{"routePart":"scans","sdkPartName":"scans"}])


class LinkContactToAssetRequest(RequestPost[LinkContactToAssetPathParameters, undefined, LinkContactToAssetRequestBody, LinkContactToAssetResponseBody]):
	def __init__(self, session):
		super(LinkContactToAssetRequest, self).__init__(session, route_segments =  [{"parm":"assetId","routePart":"assets","sdkPartName":"asset"},{"parm":"contactId","routePart":"contacts","sdkPartName":"contact"}])


class UnlinkContactToAssetRequest(RequestDelete[UnlinkContactToAssetPathParameters, undefined, undefined, undefined]):
	def __init__(self, session):
		super(UnlinkContactToAssetRequest, self).__init__(session, route_segments =  [{"parm":"assetId","routePart":"assets","sdkPartName":"asset"},{"parm":"contactId","routePart":"contacts","sdkPartName":"contact"}])


class UpdateAssetRequest(RequestPatch[UpdateAssetPathParameters, undefined, UpdateAssetRequestBody, UpdateAssetResponseBody]):
	def __init__(self, session):
		super(UpdateAssetRequest, self).__init__(session, route_segments =  [{"parm":"assetId","routePart":"assets","sdkPartName":"asset"}])


class DeleteContactRequest(RequestDelete[DeleteContactPathParameters, undefined, undefined, DeleteContactResponseBody]):
	def __init__(self, session):
		super(DeleteContactRequest, self).__init__(session, route_segments =  [{"parm":"contactId","routePart":"contacts","sdkPartName":"contact"}])


class GetContactRequest(RequestGet[GetContactPathParameters, undefined, undefined, GetContactResponseBody]):
	def __init__(self, session):
		super(GetContactRequest, self).__init__(session, route_segments =  [{"parm":"contactId","routePart":"contacts","sdkPartName":"contact"}])


class UpdateContactRequest(RequestPatch[UpdateContactPathParameters, undefined, UpdateContactRequestBody, UpdateContactResponseBody]):
	def __init__(self, session):
		super(UpdateContactRequest, self).__init__(session, route_segments =  [{"parm":"contactId","routePart":"contacts","sdkPartName":"contact"}])


class CreateAssetByProjectIdRequest(RequestPost[CreateAssetByProjectIdPathParameters, undefined, CreateAssetByProjectIdRequestBody, CreateAssetByProjectIdResponseBody]):
	def __init__(self, session):
		super(CreateAssetByProjectIdRequest, self).__init__(session, route_segments =  [{"parm":"projectId","routePart":"projects","sdkPartName":"project"},{"routePart":"assets","sdkPartName":"assets"}])


class CreateAssetsByProjectIdRequest(RequestPost[CreateAssetsByProjectIdPathParameters, undefined, CreateAssetsByProjectIdRequestBody, CreateAssetsByProjectIdResponseBody]):
	def __init__(self, session):
		super(CreateAssetsByProjectIdRequest, self).__init__(session, route_segments =  [{"parm":"projectId","routePart":"projects","sdkPartName":"project"},{"routePart":"assets/batch","sdkPartName":"assetsBatch"}])


class CreateContactByProjectIdRequest(RequestPost[CreateContactByProjectIdPathParameters, undefined, CreateContactByProjectIdRequestBody, CreateContactByProjectIdResponseBody]):
	def __init__(self, session):
		super(CreateContactByProjectIdRequest, self).__init__(session, route_segments =  [{"parm":"projectId","routePart":"projects","sdkPartName":"project"},{"routePart":"contacts","sdkPartName":"contacts"}])


class CreateContactsByProjectIdRequest(RequestPost[CreateContactsByProjectIdPathParameters, undefined, CreateContactsByProjectIdRequestBody, CreateContactsByProjectIdResponseBody]):
	def __init__(self, session):
		super(CreateContactsByProjectIdRequest, self).__init__(session, route_segments =  [{"parm":"projectId","routePart":"projects","sdkPartName":"project"},{"routePart":"contacts/batch","sdkPartName":"contactsBatch"}])


class CreateSmsTemplateByProjectIdRequest(RequestPost[CreateSmsTemplateByProjectIdPathParameters, undefined, CreateSmsTemplateByProjectIdRequestBody, CreateSmsTemplateByProjectIdResponseBody]):
	def __init__(self, session):
		super(CreateSmsTemplateByProjectIdRequest, self).__init__(session, route_segments =  [{"parm":"projectId","routePart":"projects","sdkPartName":"project"},{"routePart":"smstemplates","sdkPartName":"smsTemplates"}])


class DeleteContactsByProjectIdRequest(RequestDelete[DeleteContactsByProjectIdPathParameters, DeleteContactsByProjectIdQueryStringParameters, undefined, DeleteContactsByProjectIdResponseBody]):
	def __init__(self, session):
		super(DeleteContactsByProjectIdRequest, self).__init__(session, route_segments =  [{"parm":"projectId","routePart":"projects","sdkPartName":"project"},{"routePart":"contacts/batch","sdkPartName":"contactsBatch"}])


class DeleteSmsTemplateByProjectIdRequest(RequestDelete[DeleteSmsTemplateByProjectIdPathParameters, undefined, undefined, DeleteSmsTemplateByProjectIdResponseBody]):
	def __init__(self, session):
		super(DeleteSmsTemplateByProjectIdRequest, self).__init__(session, route_segments =  [{"parm":"projectId","routePart":"projects","sdkPartName":"project"},{"parm":"smsTemplateName","routePart":"smstemplates","sdkPartName":"smsTemplate"}])


class GetAssetsByProjectIdRequest(RequestGet[GetAssetsByProjectIdPathParameters, GetAssetsByProjectIdQueryStringParameters, undefined, GetAssetsByProjectIdResponseBody]):
	def __init__(self, session):
		super(GetAssetsByProjectIdRequest, self).__init__(session, route_segments =  [{"parm":"projectId","routePart":"projects","sdkPartName":"project"},{"routePart":"assets","sdkPartName":"assets"}])


class GetContactsByProjectIdRequest(RequestGet[GetContactsByProjectIdPathParameters, GetContactsByProjectIdQueryStringParameters, undefined, GetContactsByProjectIdResponseBody]):
	def __init__(self, session):
		super(GetContactsByProjectIdRequest, self).__init__(session, route_segments =  [{"parm":"projectId","routePart":"projects","sdkPartName":"project"},{"routePart":"contacts","sdkPartName":"contacts"}])


class GetProjectByProjectIdRequest(RequestGet[GetProjectByProjectIdPathParameters, undefined, undefined, GetProjectByProjectIdResponseBody]):
	def __init__(self, session):
		super(GetProjectByProjectIdRequest, self).__init__(session, route_segments =  [{"parm":"projectId","routePart":"projects","sdkPartName":"project"}])


class GetQrCodesByProjectIdRequest(RequestGet[GetQrCodesByProjectIdPathParameters, GetQrCodesByProjectIdQueryStringParameters, undefined, GetQrCodesByProjectIdResponseBody]):
	def __init__(self, session):
		super(GetQrCodesByProjectIdRequest, self).__init__(session, route_segments =  [{"parm":"projectId","routePart":"projects","sdkPartName":"project"},{"routePart":"qrcodes","sdkPartName":"qrCodes"}])


class GetScansByProjectIdRequest(RequestGet[GetScansByProjectIdPathParameters, GetScansByProjectIdQueryStringParameters, undefined, GetScansByProjectIdResponseBody]):
	def __init__(self, session):
		super(GetScansByProjectIdRequest, self).__init__(session, route_segments =  [{"parm":"projectId","routePart":"projects","sdkPartName":"project"},{"routePart":"scans","sdkPartName":"scans"}])


class GetSmsTemplateByProjectIdRequest(RequestGet[GetSmsTemplateByProjectIdPathParameters, undefined, undefined, GetSmsTemplateByProjectIdResponseBody]):
	def __init__(self, session):
		super(GetSmsTemplateByProjectIdRequest, self).__init__(session, route_segments =  [{"parm":"projectId","routePart":"projects","sdkPartName":"project"},{"parm":"smsTemplateName","routePart":"smstemplates","sdkPartName":"smsTemplate"}])


class GetSmsTemplatesByProjectIdRequest(RequestGet[GetSmsTemplatesByProjectIdPathParameters, GetSmsTemplatesByProjectIdQueryStringParameters, undefined, GetSmsTemplatesByProjectIdResponseBody]):
	def __init__(self, session):
		super(GetSmsTemplatesByProjectIdRequest, self).__init__(session, route_segments =  [{"parm":"projectId","routePart":"projects","sdkPartName":"project"},{"routePart":"smstemplates","sdkPartName":"smsTemplates"}])


class UpdateProjectByProjectIdRequest(RequestPatch[UpdateProjectByProjectIdPathParameters, undefined, UpdateProjectByProjectIdRequestBody, UpdateProjectByProjectIdResponseBody]):
	def __init__(self, session):
		super(UpdateProjectByProjectIdRequest, self).__init__(session, route_segments =  [{"parm":"projectId","routePart":"projects","sdkPartName":"project"}])


class UpdateSmsTemplateRequest(RequestPatch[UpdateSmsTemplatePathParameters, undefined, UpdateSmsTemplateRequestBody, UpdateSmsTemplateResponseBody]):
	def __init__(self, session):
		super(UpdateSmsTemplateRequest, self).__init__(session, route_segments =  [{"parm":"projectId","routePart":"projects","sdkPartName":"project"},{"parm":"smsTemplateName","routePart":"smstemplates","sdkPartName":"smsTemplate"}])


class DeleteQrCodeRequest(RequestDelete[DeleteQrCodePathParameters, undefined, undefined, DeleteQrCodeResponseBody]):
	def __init__(self, session):
		super(DeleteQrCodeRequest, self).__init__(session, route_segments =  [{"parm":"qrCodeId","routePart":"qrcodes","sdkPartName":"qrCode"}])


class GetQrCodeRequest(RequestGet[GetQrCodePathParameters, GetQrCodeQueryStringParameters, undefined, GetQrCodeResponseBody]):
	def __init__(self, session):
		super(GetQrCodeRequest, self).__init__(session, route_segments =  [{"parm":"qrCodeId","routePart":"qrcodes","sdkPartName":"qrCode"}])


class UpdateQrCodeRequest(RequestPatch[UpdateQrCodePathParameters, undefined, UpdateQrCodeRequestBody, UpdateQrCodeResponseBody]):
	def __init__(self, session):
		super(UpdateQrCodeRequest, self).__init__(session, route_segments =  [{"parm":"qrCodeId","routePart":"qrcodes","sdkPartName":"qrCode"}])


class CreateContactByScanIdRequest(RequestPost[CreateContactByScanIdPathParameters, undefined, CreateContactByScanIdRequestBody, CreateContactByScanIdResponseBody]):
	def __init__(self, session):
		super(CreateContactByScanIdRequest, self).__init__(session, route_segments =  [{"parm":"scanId","routePart":"scans","sdkPartName":"scan"},{"routePart":"contacts","sdkPartName":"contacts"}])


class GetScanRequest(RequestGet[GetScanPathParameters, undefined, undefined, GetScanResponseBody]):
	def __init__(self, session):
		super(GetScanRequest, self).__init__(session, route_segments =  [{"parm":"scanId","routePart":"scans","sdkPartName":"scan"}])


class SendSmsByScanIdRequest(RequestPost[SendSmsByScanIdPathParameters, undefined, SendSmsByScanIdRequestBody, SendSmsByScanIdResponseBody]):
	def __init__(self, session):
		super(SendSmsByScanIdRequest, self).__init__(session, route_segments =  [{"parm":"scanId","routePart":"scans","sdkPartName":"scan"},{"routePart":"sms","sdkPartName":"sms"}])


class DeleteSessionRequest(RequestDelete[undefined, undefined, undefined, undefined]):
	def __init__(self, session):
		super(DeleteSessionRequest, self).__init__(session, route_segments =  [{"routePart":"auth/session","sdkPartName":"authSession"}])


class GetSessionRequest(RequestPost[undefined, undefined, GetSessionRequestBody, undefined]):
	def __init__(self, session):
		super(GetSessionRequest, self).__init__(session, route_segments =  [{"routePart":"auth/session","sdkPartName":"authSession"}])


class GetSessionRefreshRequest(RequestPost[undefined, undefined, undefined, undefined]):
	def __init__(self, session):
		super(GetSessionRefreshRequest, self).__init__(session, route_segments =  [{"routePart":"auth/session/refresh","sdkPartName":"refreshAuthSession"}])


#HANDLER RESOURCE CLASSES

class SdkAccountProjectsResources(Resources):
	def create(self, request_body: CreateProjectByAccountIdRequestBody, options: any = None) -> CreateProjectByAccountIdResponseBody:
		request = CreateProjectByAccountIdRequest(self.session)
		return request.go(self.path_parameters, query_string_parameters=None, request_body=request_body, response_body_class=CreateProjectByAccountIdResponseBody, options=options)


	def get(self, query_string_parameters: GetProjectsByAccountIdQueryStringParameters = None, options: any = None) -> GetProjectsByAccountIdResponseBody:
		request = GetProjectsByAccountIdRequest(self.session)
		return request.go(self.path_parameters, query_string_parameters=query_string_parameters, response_body_class=GetProjectsByAccountIdResponseBody, options=options)




class SdkAccountContactsBatchResources(Resources):
	def delete(self, query_string_parameters: DeleteContactsByAccountIdQueryStringParameters = None, options: any = None) -> DeleteContactsByAccountIdResponseBody:
		request = DeleteContactsByAccountIdRequest(self.session)
		return request.go(self.path_parameters, query_string_parameters=query_string_parameters, response_body_class=DeleteContactsByAccountIdResponseBody, options=options)




class SdkAccountAssetsResources(Resources):
	def get(self, query_string_parameters: GetAssetsByAccountIdQueryStringParameters = None, options: any = None) -> GetAssetsByAccountIdResponseBody:
		request = GetAssetsByAccountIdRequest(self.session)
		return request.go(self.path_parameters, query_string_parameters=query_string_parameters, response_body_class=GetAssetsByAccountIdResponseBody, options=options)




class SdkAccountContactsResources(Resources):
	def get(self, query_string_parameters: GetContactsByAccountIdQueryStringParameters = None, options: any = None) -> GetContactsByAccountIdResponseBody:
		request = GetContactsByAccountIdRequest(self.session)
		return request.go(self.path_parameters, query_string_parameters=query_string_parameters, response_body_class=GetContactsByAccountIdResponseBody, options=options)




class SdkAccountQrCodesResources(Resources):
	def get(self, query_string_parameters: GetQrCodesByAccountIdQueryStringParameters = None, options: any = None) -> GetQrCodesByAccountIdResponseBody:
		request = GetQrCodesByAccountIdRequest(self.session)
		return request.go(self.path_parameters, query_string_parameters=query_string_parameters, response_body_class=GetQrCodesByAccountIdResponseBody, options=options)




class SdkAccountScansResources(Resources):
	def get(self, query_string_parameters: GetScansByAccountIdQueryStringParameters = None, options: any = None) -> GetScansByAccountIdResponseBody:
		request = GetScansByAccountIdRequest(self.session)
		return request.go(self.path_parameters, query_string_parameters=query_string_parameters, response_body_class=GetScansByAccountIdResponseBody, options=options)




class SdkAccountResource(Resource):
	def projects(self) -> SdkAccountProjectsResources:
		return SdkAccountProjectsResources(self.getSession(), self.path_parameters)


	def contacts_batch(self) -> SdkAccountContactsBatchResources:
		return SdkAccountContactsBatchResources(self.getSession(), self.path_parameters)


	def assets(self) -> SdkAccountAssetsResources:
		return SdkAccountAssetsResources(self.getSession(), self.path_parameters)


	def contacts(self) -> SdkAccountContactsResources:
		return SdkAccountContactsResources(self.getSession(), self.path_parameters)


	def qr_codes(self) -> SdkAccountQrCodesResources:
		return SdkAccountQrCodesResources(self.getSession(), self.path_parameters)


	def scans(self) -> SdkAccountScansResources:
		return SdkAccountScansResources(self.getSession(), self.path_parameters)




class SdkAssetContactsResources(Resources):
	def create(self, request_body: CreateContactByAssetIdRequestBody, options: any = None) -> CreateContactByAssetIdResponseBody:
		request = CreateContactByAssetIdRequest(self.session)
		return request.go(self.path_parameters, query_string_parameters=None, request_body=request_body, response_body_class=CreateContactByAssetIdResponseBody, options=options)


	def get(self, query_string_parameters: GetContactsByAssetIdQueryStringParameters = None, options: any = None) -> GetContactsByAssetIdResponseBody:
		request = GetContactsByAssetIdRequest(self.session)
		return request.go(self.path_parameters, query_string_parameters=query_string_parameters, response_body_class=GetContactsByAssetIdResponseBody, options=options)




class SdkAssetQrCodesResources(Resources):
	def create(self, request_body: CreateQrCodeByAssetIdRequestBody, options: any = None) -> CreateQrCodeByAssetIdResponseBody:
		request = CreateQrCodeByAssetIdRequest(self.session)
		return request.go(self.path_parameters, query_string_parameters=None, request_body=request_body, response_body_class=CreateQrCodeByAssetIdResponseBody, options=options)


	def get(self, query_string_parameters: GetQrCodesByAssetIdQueryStringParameters = None, options: any = None) -> GetQrCodesByAssetIdResponseBody:
		request = GetQrCodesByAssetIdRequest(self.session)
		return request.go(self.path_parameters, query_string_parameters=query_string_parameters, response_body_class=GetQrCodesByAssetIdResponseBody, options=options)




class SdkAssetScansResources(Resources):
	def get(self, query_string_parameters: GetScansByAssetIdQueryStringParameters = None, options: any = None) -> GetScansByAssetIdResponseBody:
		request = GetScansByAssetIdRequest(self.session)
		return request.go(self.path_parameters, query_string_parameters=query_string_parameters, response_body_class=GetScansByAssetIdResponseBody, options=options)




class SdkAssetContactResource(Resource):
	def link(self, request_body: LinkContactToAssetRequestBody, options: any = None) -> LinkContactToAssetResponseBody:
		request = LinkContactToAssetRequest(self.session)
		return request.go(self.path_parameters, query_string_parameters=None, request_body=request_body, response_body_class=LinkContactToAssetResponseBody, options=options)


	def unlink(self, options: any = None) -> Any:
		request = UnlinkContactToAssetRequest(self.session)
		return request.go(self.path_parameters, query_string_parameters=None, response_body_class=Any, options=options)




class SdkAssetResource(Resource):
	def contacts(self) -> SdkAssetContactsResources:
		return SdkAssetContactsResources(self.getSession(), self.path_parameters)


	def qr_codes(self) -> SdkAssetQrCodesResources:
		return SdkAssetQrCodesResources(self.getSession(), self.path_parameters)


	def scans(self) -> SdkAssetScansResources:
		return SdkAssetScansResources(self.getSession(), self.path_parameters)


	def contact(self, contactId: str) -> SdkAssetContactResource:
		return SdkAssetContactResource(self.getSession(), {**self.path_parameters, 'contactId': contactId})


	def delete(self, options: any = None) -> DeleteAssetResponseBody:
		request = DeleteAssetRequest(self.session)
		return request.go(self.path_parameters, query_string_parameters=None, response_body_class=DeleteAssetResponseBody, options=options)


	def get(self, query_string_parameters: GetAssetQueryStringParameters = None, options: any = None) -> GetAssetResponseBody:
		request = GetAssetRequest(self.session)
		return request.go(self.path_parameters, query_string_parameters=query_string_parameters, response_body_class=GetAssetResponseBody, options=options)


	def update(self, request_body: UpdateAssetRequestBody, options: any = None) -> UpdateAssetResponseBody:
		request = UpdateAssetRequest(self.session)
		return request.go(self.path_parameters, query_string_parameters=None, request_body=request_body, response_body_class=UpdateAssetResponseBody, options=options)




class SdkContactResource(Resource):
	def delete(self, options: any = None) -> DeleteContactResponseBody:
		request = DeleteContactRequest(self.session)
		return request.go(self.path_parameters, query_string_parameters=None, response_body_class=DeleteContactResponseBody, options=options)


	def get(self, options: any = None) -> GetContactResponseBody:
		request = GetContactRequest(self.session)
		return request.go(self.path_parameters, query_string_parameters=None, response_body_class=GetContactResponseBody, options=options)


	def update(self, request_body: UpdateContactRequestBody, options: any = None) -> UpdateContactResponseBody:
		request = UpdateContactRequest(self.session)
		return request.go(self.path_parameters, query_string_parameters=None, request_body=request_body, response_body_class=UpdateContactResponseBody, options=options)




class SdkProjectAssetsResources(Resources):
	def create(self, request_body: CreateAssetByProjectIdRequestBody, options: any = None) -> CreateAssetByProjectIdResponseBody:
		request = CreateAssetByProjectIdRequest(self.session)
		return request.go(self.path_parameters, query_string_parameters=None, request_body=request_body, response_body_class=CreateAssetByProjectIdResponseBody, options=options)


	def get(self, query_string_parameters: GetAssetsByProjectIdQueryStringParameters = None, options: any = None) -> GetAssetsByProjectIdResponseBody:
		request = GetAssetsByProjectIdRequest(self.session)
		return request.go(self.path_parameters, query_string_parameters=query_string_parameters, response_body_class=GetAssetsByProjectIdResponseBody, options=options)




class SdkProjectAssetsBatchResources(Resources):
	def create(self, request_body: CreateAssetsByProjectIdRequestBody, options: any = None) -> CreateAssetsByProjectIdResponseBody:
		request = CreateAssetsByProjectIdRequest(self.session)
		return request.go(self.path_parameters, query_string_parameters=None, request_body=request_body, response_body_class=CreateAssetsByProjectIdResponseBody, options=options)




class SdkProjectContactsResources(Resources):
	def create(self, request_body: CreateContactByProjectIdRequestBody, options: any = None) -> CreateContactByProjectIdResponseBody:
		request = CreateContactByProjectIdRequest(self.session)
		return request.go(self.path_parameters, query_string_parameters=None, request_body=request_body, response_body_class=CreateContactByProjectIdResponseBody, options=options)


	def get(self, query_string_parameters: GetContactsByProjectIdQueryStringParameters = None, options: any = None) -> GetContactsByProjectIdResponseBody:
		request = GetContactsByProjectIdRequest(self.session)
		return request.go(self.path_parameters, query_string_parameters=query_string_parameters, response_body_class=GetContactsByProjectIdResponseBody, options=options)




class SdkProjectContactsBatchResources(Resources):
	def create(self, request_body: CreateContactsByProjectIdRequestBody, options: any = None) -> CreateContactsByProjectIdResponseBody:
		request = CreateContactsByProjectIdRequest(self.session)
		return request.go(self.path_parameters, query_string_parameters=None, request_body=request_body, response_body_class=CreateContactsByProjectIdResponseBody, options=options)


	def delete(self, query_string_parameters: DeleteContactsByProjectIdQueryStringParameters = None, options: any = None) -> DeleteContactsByProjectIdResponseBody:
		request = DeleteContactsByProjectIdRequest(self.session)
		return request.go(self.path_parameters, query_string_parameters=query_string_parameters, response_body_class=DeleteContactsByProjectIdResponseBody, options=options)




class SdkProjectSmsTemplatesResources(Resources):
	def create(self, request_body: CreateSmsTemplateByProjectIdRequestBody, options: any = None) -> CreateSmsTemplateByProjectIdResponseBody:
		request = CreateSmsTemplateByProjectIdRequest(self.session)
		return request.go(self.path_parameters, query_string_parameters=None, request_body=request_body, response_body_class=CreateSmsTemplateByProjectIdResponseBody, options=options)


	def get(self, query_string_parameters: GetSmsTemplatesByProjectIdQueryStringParameters = None, options: any = None) -> GetSmsTemplatesByProjectIdResponseBody:
		request = GetSmsTemplatesByProjectIdRequest(self.session)
		return request.go(self.path_parameters, query_string_parameters=query_string_parameters, response_body_class=GetSmsTemplatesByProjectIdResponseBody, options=options)




class SdkProjectSmsTemplateResource(Resource):
	def delete(self, options: any = None) -> DeleteSmsTemplateByProjectIdResponseBody:
		request = DeleteSmsTemplateByProjectIdRequest(self.session)
		return request.go(self.path_parameters, query_string_parameters=None, response_body_class=DeleteSmsTemplateByProjectIdResponseBody, options=options)


	def get(self, options: any = None) -> GetSmsTemplateByProjectIdResponseBody:
		request = GetSmsTemplateByProjectIdRequest(self.session)
		return request.go(self.path_parameters, query_string_parameters=None, response_body_class=GetSmsTemplateByProjectIdResponseBody, options=options)


	def update(self, request_body: UpdateSmsTemplateRequestBody, options: any = None) -> UpdateSmsTemplateResponseBody:
		request = UpdateSmsTemplateRequest(self.session)
		return request.go(self.path_parameters, query_string_parameters=None, request_body=request_body, response_body_class=UpdateSmsTemplateResponseBody, options=options)




class SdkProjectQrCodesResources(Resources):
	def get(self, query_string_parameters: GetQrCodesByProjectIdQueryStringParameters = None, options: any = None) -> GetQrCodesByProjectIdResponseBody:
		request = GetQrCodesByProjectIdRequest(self.session)
		return request.go(self.path_parameters, query_string_parameters=query_string_parameters, response_body_class=GetQrCodesByProjectIdResponseBody, options=options)




class SdkProjectScansResources(Resources):
	def get(self, query_string_parameters: GetScansByProjectIdQueryStringParameters = None, options: any = None) -> GetScansByProjectIdResponseBody:
		request = GetScansByProjectIdRequest(self.session)
		return request.go(self.path_parameters, query_string_parameters=query_string_parameters, response_body_class=GetScansByProjectIdResponseBody, options=options)




class SdkProjectResource(Resource):
	def assets(self) -> SdkProjectAssetsResources:
		return SdkProjectAssetsResources(self.getSession(), self.path_parameters)


	def assets_batch(self) -> SdkProjectAssetsBatchResources:
		return SdkProjectAssetsBatchResources(self.getSession(), self.path_parameters)


	def contacts(self) -> SdkProjectContactsResources:
		return SdkProjectContactsResources(self.getSession(), self.path_parameters)


	def contacts_batch(self) -> SdkProjectContactsBatchResources:
		return SdkProjectContactsBatchResources(self.getSession(), self.path_parameters)


	def sms_templates(self) -> SdkProjectSmsTemplatesResources:
		return SdkProjectSmsTemplatesResources(self.getSession(), self.path_parameters)


	def sms_template(self, smsTemplateName: str) -> SdkProjectSmsTemplateResource:
		return SdkProjectSmsTemplateResource(self.getSession(), {**self.path_parameters, 'smsTemplateName': smsTemplateName})


	def qr_codes(self) -> SdkProjectQrCodesResources:
		return SdkProjectQrCodesResources(self.getSession(), self.path_parameters)


	def scans(self) -> SdkProjectScansResources:
		return SdkProjectScansResources(self.getSession(), self.path_parameters)


	def get(self, options: any = None) -> GetProjectByProjectIdResponseBody:
		request = GetProjectByProjectIdRequest(self.session)
		return request.go(self.path_parameters, query_string_parameters=None, response_body_class=GetProjectByProjectIdResponseBody, options=options)


	def update(self, request_body: UpdateProjectByProjectIdRequestBody, options: any = None) -> UpdateProjectByProjectIdResponseBody:
		request = UpdateProjectByProjectIdRequest(self.session)
		return request.go(self.path_parameters, query_string_parameters=None, request_body=request_body, response_body_class=UpdateProjectByProjectIdResponseBody, options=options)




class SdkQrCodeResource(Resource):
	def delete(self, options: any = None) -> DeleteQrCodeResponseBody:
		request = DeleteQrCodeRequest(self.session)
		return request.go(self.path_parameters, query_string_parameters=None, response_body_class=DeleteQrCodeResponseBody, options=options)


	def get(self, query_string_parameters: GetQrCodeQueryStringParameters = None, options: any = None) -> GetQrCodeResponseBody:
		request = GetQrCodeRequest(self.session)
		return request.go(self.path_parameters, query_string_parameters=query_string_parameters, response_body_class=GetQrCodeResponseBody, options=options)


	def update(self, request_body: UpdateQrCodeRequestBody, options: any = None) -> UpdateQrCodeResponseBody:
		request = UpdateQrCodeRequest(self.session)
		return request.go(self.path_parameters, query_string_parameters=None, request_body=request_body, response_body_class=UpdateQrCodeResponseBody, options=options)




class SdkScanContactsResources(Resources):
	def create(self, request_body: CreateContactByScanIdRequestBody, options: any = None) -> CreateContactByScanIdResponseBody:
		request = CreateContactByScanIdRequest(self.session)
		return request.go(self.path_parameters, query_string_parameters=None, request_body=request_body, response_body_class=CreateContactByScanIdResponseBody, options=options)




class SdkScanSmsResources(Resources):
	def send(self, request_body: SendSmsByScanIdRequestBody, options: any = None) -> SendSmsByScanIdResponseBody:
		request = SendSmsByScanIdRequest(self.session)
		return request.go(self.path_parameters, query_string_parameters=None, request_body=request_body, response_body_class=SendSmsByScanIdResponseBody, options=options)




class SdkScanResource(Resource):
	def contacts(self) -> SdkScanContactsResources:
		return SdkScanContactsResources(self.getSession(), self.path_parameters)


	def sms(self) -> SdkScanSmsResources:
		return SdkScanSmsResources(self.getSession(), self.path_parameters)


	def get(self, options: any = None) -> GetScanResponseBody:
		request = GetScanRequest(self.session)
		return request.go(self.path_parameters, query_string_parameters=None, response_body_class=GetScanResponseBody, options=options)




class SdkAuthSessionResources(Resources):
	def delete(self, options: any = None) -> Any:
		request = DeleteSessionRequest(self.session)
		return request.go(self.path_parameters, query_string_parameters=None, response_body_class=Any, options=options)


	def create(self, request_body: GetSessionRequestBody, options: any = None) -> Any:
		request = GetSessionRequest(self.session)
		return request.go(self.path_parameters, query_string_parameters=None, request_body=request_body, response_body_class=Any, options=options)




class SdkRefreshAuthSessionResources(Resources):
	def create(self, options: any = None) -> Any:
		request = GetSessionRefreshRequest(self.session)
		return request.go(self.path_parameters, query_string_parameters=None, response_body_class=Any, options=options)




class SdkResources(Resources):
	def account(self, accountId: str) -> SdkAccountResource:
		return SdkAccountResource(self.getSession(), {**self.path_parameters, 'accountId': accountId})


	def asset(self, assetId: str) -> SdkAssetResource:
		return SdkAssetResource(self.getSession(), {**self.path_parameters, 'assetId': assetId})


	def contact(self, contactId: str) -> SdkContactResource:
		return SdkContactResource(self.getSession(), {**self.path_parameters, 'contactId': contactId})


	def project(self, projectId: str) -> SdkProjectResource:
		return SdkProjectResource(self.getSession(), {**self.path_parameters, 'projectId': projectId})


	def qr_code(self, qrCodeId: str) -> SdkQrCodeResource:
		return SdkQrCodeResource(self.getSession(), {**self.path_parameters, 'qrCodeId': qrCodeId})


	def scan(self, scanId: str) -> SdkScanResource:
		return SdkScanResource(self.getSession(), {**self.path_parameters, 'scanId': scanId})


	def auth_session(self) -> SdkAuthSessionResources:
		return SdkAuthSessionResources(self.getSession(), self.path_parameters)


	def refresh_auth_session(self) -> SdkRefreshAuthSessionResources:
		return SdkRefreshAuthSessionResources(self.getSession(), self.path_parameters)




