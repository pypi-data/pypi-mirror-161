from typing import List, Optional, cast, Dict

from google.analytics.admin import AnalyticsAdminServiceClient
from google.oauth2 import service_account
from google.analytics.data_v1beta import BetaAnalyticsDataClient, RunReportResponse
from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest

from arcane.core import BadRequestError, BaseAccount
from arcane.credentials import get_user_decrypted_credentials
from arcane.datastore import Client as DatastoreClient

from .helpers import get_google_analytics_v4_account, _get_property_name_lgq


class GaV4Client:
    def __init__(
        self,
        gcp_service_account: str,
        property_id: str,
        base_account: Optional[BaseAccount] = None,
        ga_v4_account: Optional[Dict] = None,
        datastore_client: Optional[DatastoreClient] = None,
        gcp_project: Optional[str] = None,
        secret_key_file: Optional[str] = None,
        firebase_api_key: Optional[str] = None,
        auth_enabled: bool = True,
        clients_service_url: Optional[str] = None,
        user_email: Optional[str] = None
    ):

        self.property_id = property_id
        scopes = ['https://www.googleapis.com/auth/analytics.readonly']
        if gcp_service_account and (ga_v4_account or base_account or user_email):
            if user_email:
                creator_email = user_email
            else:
                if ga_v4_account is None:
                    base_account = cast(BaseAccount, base_account)
                    ga_v4_account = get_google_analytics_v4_account(
                        base_account=base_account,
                        clients_service_url=clients_service_url,
                        firebase_api_key=firebase_api_key,
                        gcp_service_account=gcp_service_account,
                        auth_enabled=auth_enabled
                    )

                creator_email = ga_v4_account['creator_email']

            if creator_email is not None:
                if not secret_key_file:
                    raise BadRequestError('secret_key_file should not be None while using user access protocol')

                self.credentials = get_user_decrypted_credentials(
                    user_email=creator_email,
                    secret_key_file=secret_key_file,
                    gcp_credentials_path=gcp_service_account,
                    gcp_project=gcp_project,
                    datastore_client=datastore_client
                )
            else:
                self.credentials = service_account.Credentials.from_service_account_file(gcp_service_account, scopes=scopes)
        elif gcp_service_account:
            ## Used when posting an account using our credential (it is not yet in our database)
            self.credentials = service_account.Credentials.from_service_account_file(gcp_service_account, scopes=scopes)
        else:
            raise BadRequestError('one of the following arguments must be specified: gcp_service_account and (google_ads_account or base_account or user_email)')

    def check_access(self):
        """Utility function to check if the user has access to the property (call get_property_name)"""
        self.get_property_name()

    def get_property_name(self) -> str:
        client = AnalyticsAdminServiceClient(credentials=self.credentials)
        return _get_property_name_lgq(client, self.property_id)

    def run_report(self, property_id: str, dimensions: List[str], metrics: List[str], start_date: str, end_date: str, limit: int=10000, offset: int=0) -> RunReportResponse:
        """Runs a report on the Google Analytics V4 Data API.
        Check https://developers.google.com/analytics/devguides/reporting/data/v1/basics#report_request for more information.
        For more information on limit and offset check https://developers.google.com/analytics/devguides/reporting/data/v1/basics#pagination
        """
        client = BetaAnalyticsDataClient(credentials=self.credentials)
        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name=dimensinon)
                        for dimensinon in dimensions],
            metrics=[Metric(name=metric) for metric in metrics],
            date_ranges=[DateRange(
                start_date=start_date,
                end_date=end_date
            )],
            limit=limit,
            offset=offset
        )
        response = client.run_report(request)
        return response
