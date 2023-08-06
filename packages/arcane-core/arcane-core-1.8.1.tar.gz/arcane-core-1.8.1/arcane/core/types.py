from typing import Dict, List, Union, Tuple, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing_extensions import Literal, TypedDict


class AccountType(Enum):
    AMAZON = 'Amazon'
    MICROSOFT_ADVERTISING = 'Microsoft Advertising'
    CRITEO = 'Criteo'
    FACEBOOK = 'Facebook'
    GOOGLE_ADS = 'Google Ads'
    GOOGLE_ANALYTICS = 'Google Analytics'
    MANOMANO = 'Manomano'
    MCT = 'Google Merchant Center'
    PINTEREST = 'Pinterest'
    GOOGLE_ANALYTICS_V4 = 'Google Analytics V4'


class BaseAccount(TypedDict):
    id: str
    client_id: str


@dataclass
class Campaign:
    campaign_id: str
    campaign_name: str
    campaign_status: Union[str, None] = None


@dataclass
class Account:
    account_type: AccountType
    account_id: str
    account_name: str
    campaigns: List[Campaign] = field(default_factory=list)


@dataclass
class ParametersMainSetting:
    client_id: str


@dataclass
class ParametersSubSettingPost:
    client_id: str
    scope_id: int


@dataclass
class ParametersSubSettingDelete:
    scope_id: int


# To use as values in code
class ImportType:
    HTTP = "HTTP"
    FTP_SFTP = "FTP/SFTP"
    GCS = "GCS"
    GOSPORT_SFTP = "GOSPORT_SFTP"
    SPREADSHEET = "SPREADSHEET"
    BIG_QUERY = "BIG_QUERY"
    ADWORDS_PRODUCT = "ADWORDS_PRODUCT"
    GA_ECOMMERCE = "GA_ECOMMERCE"
    ARCANE_SFTP = "ARCANE_SFTP"
    DATALAB = "DATALAB"
    MAGENTO = "MAGENTO"
    SHOPIFY = "SHOPIFY"
    UPLOAD_FROM_DEVICE = "UPLOAD_FROM_DEVICE"
    SNOWFLAKE = "SNOWFLAKE"
    GA_4 = "GA_4"

# To use when specifying typehints
ImportTypeLiteral = Literal[
    "HTTP", "FTP_SFTP", "GCS", "GOSPORT_SFTP", "SPREADSHEET",
    "BIG_QUERY", "ADWORDS_PRODUCT", "GA_ECOMMERCE", "ARCANE_SFTP", "DATALAB",
    "MAGENTO","SHOPIFY", "UPLOAD_FROM_DEVICE", "SNOWFLAKE"
]

# To use as values in code
class ExportTypeEnum:
    HTTP = 'HTTP'
    DELTA_API_PUSH = 'DELTA_API_PUSH'
    SFTP = 'SFTP'
    BQ = 'BQ'
    ALGOLIA = 'ALGOLIA'
    FULL_API_PUSH = 'FULL_API_PUSH'


# To use when specifying typehints
ExportTypeLiteral = Literal["HTTP", "DELTA_API_PUSH", "SFTP", "BQ", "ALGOLIA", "FULL_API_PUSH"]


# To use as values in code
class ChannelType(Enum):
    mct = 'mct'
    mct_legacy = 'mct_legacy'
    googleads = 'googleads'
    facebook = 'facebook'
    facebook_flight = 'facebook_flight'
    bing = 'bing'
    criteo = 'criteo'
    searchads_360 = 'searchads_360'
    leguide_fr = 'leguide_fr'
    kelkoo = 'kelkoo'
    mct_push = 'mct_push'
    pricerunner = 'pricerunner'
    prisjakt = 'prisjakt'
    eperflex = 'eperflex'
    choozen = 'choozen'
    custom = 'custom'
    effinity = 'effinity'
    awin = 'awin'
    pinterest = 'pinterest'
    moebel24 = 'moebel24'
    trovaprezzi = 'trovaprezzi'
    cherchons = 'cherchons'
    stylight = 'stylight'
    shopzilla = 'shopzilla'
    lionshome = 'lionshome'
    touslesprix = 'touslesprix'
    pricingassistant = 'pricingassistant'
    meubles_fr = 'meubles_fr'
    moebel_de = 'moebel_de'
    manomano = 'manomano'
    dsa = 'dsa'
    snapchat = 'snapchat'
    local_inventory_feed = 'local_inventory_feed'
    local_inventory_push = 'local_inventory_push'
    fitle = 'fitle'
    bazaar_voice = 'bazaar_voice'
    idealo = 'idealo'
    audience_google_ads = 'audience_google_ads'
    audience_facebook = 'audience_facebook'
    pass_culture = 'pass_culture'
    sftp = 'sftp'
    big_query = 'big_query'
    ad_customizers = 'ad_customizers'
    inventory_management = 'inventory_management'
    datastudio = 'datastudio'
    rakuten = 'rakuten'
    ssd = 'ssd'
    facebook_ssd = 'facebook_ssd'
    frandroid = 'frandroid'
    outbrain = 'outbrain'


# To use when specifying typehints
ChannelTypeLiteral = Literal['mct', 'mct_legacy', 'googleads', 'facebook', 'facebook_flight', 'bing',
                             'criteo', 'searchads_360', 'leguide_fr', 'kelkoo', 'mct_push', 'pricerunner',
                             'prisjakt', 'eperflex', 'choozen', 'custom', 'effinity', 'awin', 'pinterest', 'moebel24',
                             'trovaprezzi', 'cherchons', 'stylight', 'shopzilla', 'lionshome',
                             'touslesprix', 'pricingassistant', 'meubles_fr', 'moebel_de', 'manomano',
                             'dsa', 'snapchat', 'local_inventory_feed', 'local_inventory_push', 'fitle',
                             'bazaar_voice', 'idealo', 'audience_google_ads', 'audience_facebook', 'pass_culture',
                             'sftp', 'big_query', 'ad_customizers', 'inventory_management', 'datastudio', 'rakuten', 'ssd',
                             'facebook_ssd', 'frandroid', 'outbrain']


class GaEcommerceParameters(object):
    """ Parameters needed for data ingestion GA v3 ECOMMERCE """

    def __init__(self,
                 file_name: str,
                 sleep_time: int,
                 view_id: str,
                 start_date: str,
                 end_date: str,
                 metrics: List[str],
                 dimensions: Union[None, List[str]] = None):
        self.file_name = file_name
        self.sleep_time = sleep_time
        self.view_id = view_id
        self.start_date = start_date
        self.end_date = end_date
        self.metrics = metrics
        self.dimensions = dimensions if dimensions is not None else []

    @property
    def sleep_time(self) -> int:
        return self._sleep_time

    @sleep_time.setter
    def sleep_time(self, sleep_time: Union[int, float]):
        try:
            int_sleep_time = int(sleep_time)
        except ValueError as e:
            raise ValueError(f'failed to parse sleep time to an int. {str(e)}') from e
        if int_sleep_time < 0:
            raise ValueError(f'sleep_time should be a positive value and not {int_sleep_time}.')
        self._sleep_time = int_sleep_time

    def to_dict(self):
        result = dict(
            file_name=self.file_name,
            sleep_time=self.sleep_time,
            view_id=self.view_id,
            start_date=self.start_date,
            end_date=self.end_date,
            metrics=self.metrics)
        if self.dimensions:
            result.update(dimensions=self.dimensions)
        return result


class BodyGaReportApi(object):
    DATE_FORMAT = '%Y-%m-%d'

    def __init__(self,
                 index: int,  # current query number
                 total_queries: int,  # total number of queries to get entire data range
                 data_ingestion_id: int,
                 start_date: str,  # start date of the data range the cloud function will handle
                 end_date: str,
                 monitoring_id: Optional[str] = None):  # end date of the data range the cloud function will handle
        self.index = index
        self.total_queries = total_queries
        self.data_ingestion_id = data_ingestion_id
        self.start_date = start_date
        self.end_date = end_date
        self.monitoring_id = monitoring_id

    @property
    def start_date(self) -> str:
        return self._start_date

    @start_date.setter
    def start_date(self, start_date: str):
        try:
            datetime.strptime(start_date, self.__class__.DATE_FORMAT)
        except ValueError as e:
            raise ValueError(
                f"start_date has an invalid format : {e}")
        self._start_date = start_date

    @property
    def end_date(self) -> str:
        return self._end_date

    @end_date.setter
    def end_date(self, end_date: str):
        try:
            datetime.strptime(end_date, self.__class__.DATE_FORMAT)
        except ValueError as e:
            raise ValueError(
                f"end_date has an invalid format : {e}")
        self._end_date = end_date

    def to_dict(self):
        output = dict(
            index=self.index,
            total_queries=self.total_queries,
            data_ingestion_id=self.data_ingestion_id,
            start_date=self.start_date,
            end_date=self.end_date
        )

        if self.monitoring_id is not None:
            output['monitoring_id'] = self.monitoring_id

        return output


class ScopeContentTypedDict(TypedDict):
        account_id: Union[str, int]
        first_available_date: Union[None, datetime]
        backfill_on_next_exec: Union[None, bool]
        goals: Union[None, List[str]]


# Attribution Models
class ScopeContent(object):
    """ Account information characterising next execution needs """

    def __init__(self,
                 account_id: Union[str, int],
                 first_available_date: Union[None, datetime] = None,
                 backfill_on_next_exec: Union[None, bool] = None,
                 goals: Union[None, List[str]] = None):  # type of goals tracked in GA to follow the model's performance
        self.account_id = account_id
        self.first_available_date = first_available_date
        self.backfill_on_next_exec = backfill_on_next_exec
        self.goals = goals if goals else ["ecommerce"]

    # This class allow us to have a TypedDict when the to_dict is called


    def to_dict(self) -> ScopeContentTypedDict:
        """Returns ScopeContent object as a dict"""
        return ScopeContentTypedDict(
            account_id=self.account_id,
            first_available_date=self.first_available_date,
            backfill_on_next_exec=self.backfill_on_next_exec,
            goals=self.goals)

    @property
    def account_id(self) -> str:
        return self._account_id

    @account_id.setter
    def account_id(self, account_id: Union[int, str]):
        if not isinstance(account_id, str):
            try:
                account_id = str(account_id)
            except TypeError as e:
                raise TypeError(
                    f'Data type is {type(account_id)} whereas it should be <str>. Transcoding error {e}')
        self._account_id = account_id


class Scope(object):
    """ List of all accounts along with their state in pilot, assembled per type """

    def __init__(self,
                 scope_bing: Union[Tuple[dict], List[dict]] = tuple(),
                 scope_facebook: Union[Tuple[dict], List[dict]] = tuple(),
                 scope_adwords: Union[Tuple[dict], List[dict]] = tuple(),
                 scope_ga: Union[Tuple[dict], List[dict]] = tuple(),
                 scope_criteo: Union[Tuple[dict], List[dict]] = tuple()):
        self.scope_bing: List[ScopeContent] = self.build_scope_content(scope_bing)
        self.scope_facebook: List[ScopeContent] = self.build_scope_content(
            scope_facebook)
        self.scope_adwords: List[ScopeContent] = self.build_scope_content(
            scope_adwords)
        self.scope_ga: List[ScopeContent] = self.build_scope_content(scope_ga)
        self.scope_criteo: List[ScopeContent] = self.build_scope_content(
            scope_criteo)

    def to_dict(self):
        """Returns Scope object as a dict"""
        return dict(scope_bing=[account.to_dict() for account in self.scope_bing],
                    scope_facebook=[account.to_dict()
                                    for account in self.scope_facebook],
                    scope_adwords=[account.to_dict()
                                   for account in self.scope_adwords],
                    scope_ga=[account.to_dict() for account in self.scope_ga],
                    scope_criteo=[account.to_dict() for account in self.scope_criteo])

    @staticmethod
    def build_scope_content(scope_list: List[Dict]) -> List[ScopeContent]:
        """
        Transforms a list of dict into a list of ScopeContent.
        :raises TypeError with the element index that has an issue in case an element(dict) does not have a valid format
        """
        result = []
        for scope_index, account_scope in enumerate(scope_list):
            try:
                result.append(ScopeContent(**account_scope))
            except TypeError as e:
                raise TypeError(
                    f'Element {scope_index} does not have the correct keys. Error {e}')
        return result


class CustomModelRule(object):
    """ Contains a Custom Model Rule """

    def __init__(self,
                 coefficient: Union[int, float],
                 rank: str,
                 custom_channel: Union[None, str] = None,
                 pathPosition: Union[None, int, str] = None,
                 pathLength: Union[None, int, str] = None,
                 campaignName: Union[None, str] = None,
                 criterionName: Union[None, str] = None,
                 source: Union[None, str] = None,
                 medium: Union[None, str] = None):
        self.coefficient = coefficient
        self.rank = rank
        self.custom_channel = custom_channel
        self.pathPosition = pathPosition
        self.pathLength = pathLength
        self.campaignName = campaignName
        self.criterionName = criterionName
        self.source = source
        self.medium = medium

    def to_dict(self):
        """ Returns CustomModelRule object as a dict """
        serialized_dict = dict(coefficient=self.coefficient, rank=self.rank)
        if self.custom_channel:
            serialized_dict['custom_channel'] = self.custom_channel
        if self.pathPosition:
            serialized_dict['pathPosition'] = self.pathPosition
        if self.pathLength:
            serialized_dict['pathLength'] = self.pathLength
        if self.campaignName:
            serialized_dict['campaignName'] = self.campaignName
        if self.criterionName:
            serialized_dict['criterionName'] = self.criterionName
        if self.source:
            serialized_dict['source'] = self.source
        if self.medium:
            serialized_dict['medium'] = self.medium
        return serialized_dict


class PreviewResult(object):
    """ Contain preview metrics for a certain channel """

    def __init__(self,
                 channel: str,
                 cost: float,
                 conversions: float,
                 sales: float):
        self.channel = channel
        self.cost = cost
        self.conversions = conversions
        self.sales = sales

    def to_dict(self):
        """ Returns PreviewResult object as a dict """
        return dict(channel=self.channel,
                    cost=self.cost,
                    conversions=self.conversions,
                    sales=self.sales)


class AdscaleError(object):
    """Error resulting from preview"""

    def __init__(self, reason: str, component: str = None):
        self.reason = reason
        self.component = component

    def to_dict(self):
        """Returns Error object as a dict"""
        return dict(reason=self.reason, component=self.component)


class Preview(object):
    """ List of preview results for each channel """

    def __init__(self,
                 preview_results: List[dict] = tuple(),
                 latest_exec: datetime = None,
                 is_loading: bool = False,
                 error: List[dict] = tuple()):
        self.preview_results: List[PreviewResult] = [PreviewResult(
            **preview_result) for preview_result in preview_results]
        self.latest_exec = latest_exec
        self.is_loading = is_loading
        self.error: List[AdscaleError] = [AdscaleError(**e) for e in error]

    def to_dict(self):
        """Returns Preview object as a dict"""
        return dict(preview_results=[preview_result.to_dict() for preview_result in self.preview_results],
                    latest_exec=self.latest_exec,
                    is_loading=self.is_loading,
                    error=[e.to_dict() for e in self.error])

class AttributionStatus:
    start = 'start'
    data_unavailable = 'data_unavailable'
    data_loading = 'data_loading'
    model_computing = 'model_computing'
    done = 'done'
    error = 'error'

@dataclass
class AttributionExecutionInfo:
    status: Optional[str]  # should be something like ValueOf[AttributionStatus]
    errors: Optional[List[str]] = None


class AttributionModel(object):
    """ Set of rules needed to define an attribution model for pilot """

    def __init__(self,
                 name: str,  # name of the setting
                 # accounts included in the model
                 scope: Dict[str, List[dict]],
                 client_id: str,  # name of the client
                 enabled: bool,  # whether the data should be fetched
                 id: Union[None, int] = None,  # id of the entity
                 # definition of custom channels rules
                 custom_channels: Union[None, Dict[str, List]] = None,
                 # latest valid modification of CostxAttribution bq table
                 latest_exec: Union[datetime, None] = None,
                 execution_info: Union[Dict, None] = None,
                 # definition of rules for custom attribution model
                 custom_model: Union[List[Dict], tuple] = tuple(),
                 custom_model_sql: Optional[str] = None,
                 preview: Union[Dict[str, Any], None] = None):  # preview results for each channel
        self.id = id
        self.name = name
        self.scope = Scope(**scope)
        self.client_id = client_id
        self.enabled = enabled
        self.custom_channels = custom_channels
        self.latest_exec = latest_exec
        self.custom_model = self.build_custom_model_rules(custom_model)
        self.custom_model_sql = custom_model_sql
        self.preview = Preview(**preview) if preview else None
        self.execution_info = AttributionExecutionInfo(
            **execution_info) if execution_info else None

        if len(self.custom_model) > 0 and self.custom_model_sql:
            raise ValueError(
                'You cannot specified both custom_model and custom_model_sql')

    def to_dict(self) -> Dict:
        """ returns a dict of the type attribution-model"""
        serialized_dict = dict(
            name=self.name,
            scope=self.scope.to_dict(),
            client_id=self.client_id,
            enabled=self.enabled,
            custom_model=[rule.to_dict() for rule in self.custom_model],
            custom_model_sql=self.custom_model_sql

        )
        if self.id:
            serialized_dict['id'] = self.id
        if self.custom_channels:
            serialized_dict['custom_channels'] = self.custom_channels
        if self.latest_exec:
            serialized_dict['latest_exec'] = self.latest_exec
        if self.preview:
            serialized_dict['preview'] = self.preview.to_dict()
        if self.execution_info:
            serialized_dict['execution_info'] = asdict(self.execution_info)

        return serialized_dict

    @staticmethod
    def build_custom_model_rules(rules_list: Union[List[Dict], tuple]) -> List[CustomModelRule]:
        result = []
        for rule in rules_list:
            try:
                result.append(CustomModelRule(**rule))
            except TypeError as e:
                raise TypeError(
                    f'Element {rule} does not have the correct keys. Error {e}')
        return result
