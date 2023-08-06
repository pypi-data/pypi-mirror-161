# coding: utf-8

# Copyright 2020,2021 IBM All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from typing import Tuple
import uuid

from ibm_cloud_sdk_core import BaseService
from ibm_watson_openscale.base_classes.tables import Table
from ibm_watson_openscale.base_classes.watson_open_scale_v2 import Asset, AssetPropertiesRequest, \
    AssetDeploymentRequest, RiskEvaluationStatus
from ibm_watson_openscale.base_classes.watson_open_scale_v2 import SparkStruct, IntegratedSystems,IntegratedSystemsListEnums,AnalyticsEngine,JsonPatchOperation, DataSourceStatus, DataSource, DataSourceConnection
from ibm_watson_openscale.base_classes.watson_open_scale_v2 import Subscriptions as BaseSubscriptions
from ibm_watson_openscale.supporting_classes.enums import *

from .utils import *

import json
import tarfile


if TYPE_CHECKING:
    from .client import WatsonOpenScaleV2Adapter
    from ibm_watson_openscale.base_classes.watson_open_scale_v2 import DetailedResponse

_DEFAULT_LIST_LENGTH = 50


# TODO: Add parameters validation in every method
class Subscriptions(BaseSubscriptions):
    """
    Manages Subscription instance.
    """

    def __init__(self, ai_client: 'WatsonOpenScaleV2Adapter') -> None:
        validate_type(ai_client, 'ai_client', BaseService, True)
        self._ai_client = ai_client
        super().__init__(watson_open_scale=self._ai_client)

    def show(self, limit: Optional[int] = 10,
             data_mart_id: str = None,
            service_provider_id: str = None,
            asset_asset_id: str = None,
            deployment_deployment_id: str = None,
            deployment_deployment_type: str = None,
            integration_reference_integrated_system_id: str = None,
            integration_reference_external_id: str = None,
            risk_evaluation_status_state: str = None,
            service_provider_operational_space_id: str = None,
            pre_production_reference_id: str = None,
            **kwargs) -> None:
        """
        Show service providers. By default 10 records will be shown.

        :param limit: maximal number of fetched rows. By default set to 10. (optional)
        :type limit: int
        :param str data_mart_id: (optional) comma-separeted list of IDs.
        :param str service_provider_id: (optional) comma-separeted list of IDs.
        :param str asset_asset_id: (optional) comma-separeted list of IDs.
        :param str deployment_deployment_id: (optional) comma-separeted list of
               IDs.
        :param str deployment_deployment_type: (optional) comma-separeted list of
               types.
        :param str integration_reference_integrated_system_id: (optional)
               comma-separeted list of IDs.
        :param str integration_reference_external_id: (optional) comma-separeted
               list of IDs.
        :param str risk_evaluation_status_state: (optional) comma-separeted list of
               states.
        :param str service_provider_operational_space_id: (optional)
               comma-separeted list of operational space ids (property of service provider
               object).
        :param str pre_production_reference_id: (optional) comma-separeted list of
               IDs.
        :param dict headers: A `dict` containing the request headers       

        A way you might use me is:

        >>> client.subscriptions.show()
        >>> client.subscriptions.show(limit=20)
        >>> client.subscriptions.show(limit=None)
        """
        validate_type(limit, u'limit', int, False)

        response = self.list(data_mart_id = data_mart_id,
            service_provider_id = service_provider_id,
            asset_asset_id = asset_asset_id,
            deployment_deployment_id = deployment_deployment_id,
            deployment_deployment_type = deployment_deployment_type,
            integration_reference_integrated_system_id = integration_reference_integrated_system_id,
            integration_reference_external_id = integration_reference_external_id,
            risk_evaluation_status_state = risk_evaluation_status_state,
            service_provider_operational_space_id = service_provider_operational_space_id,
            pre_production_reference_id = pre_production_reference_id,
            **kwargs)

        records = [[subscription.entity.asset.asset_id,
                    subscription.entity.asset.name,
                    subscription.entity.data_mart_id,
                    subscription.entity.deployment.deployment_id,
                    subscription.entity.deployment.name,
                    subscription.entity.service_provider_id,
                    subscription.entity.status.state,
                    subscription.metadata.created_at,
                    subscription.metadata.id
                    ] for subscription in response.result.subscriptions]
        columns = ['asset_id', 'asset_name', 'data_mart_id', 'deployment_id', 'deployment_name',
                   'service_provider_id', 'status', 'created_at', 'id']

        Table(columns, records).list(
            limit=limit,
            default_limit=_DEFAULT_LIST_LENGTH,
            title="Subscriptions"
        )

    def add(self,
            data_mart_id: str,
            service_provider_id: str,
            asset: 'Asset',
            deployment: 'AssetDeploymentRequest',
            asset_properties: 'AssetPropertiesRequest' = None,
            risk_evaluation_status: 'RiskEvaluationStatus' = None,
            analytics_engine: 'AnalyticsEngine' = None,
            data_sources: List['DataSource'] = None,
            training_data_stats: dict = None,
            background_mode: bool = True,
            **kwargs) -> Union['DetailedResponse', Optional[dict]]:
        """
        Add a subscription to the model deployment.

        :param str data_mart_id: ID of the data_mart (required)
        :param str service_provider_id: ID of the service_provider (required)
        :param Asset asset: an Asset object with asset's information (required)
        :param AssetDeploymentRequest deployment: an AssetDeploymentRequest object with deployment's information (required)
        :param AssetPropertiesRequest asset_properties: (optional) Additional asset
               properties (subject of discovery if not provided when creating the
               subscription).
        :param RiskEvaluationStatus risk_evaluation_status: (optional)
        :param AnalyticsEngine analytics_engine: (optional)
        :param List[DataSource] data_sources: (optional)
        :param training_data_stats: Training statistic json generated using training stats notebook (https://github.com/IBM-Watson/aios-data-distribution/blob/master/training_statistics_notebook.ipynb)
        :param background_mode: if set to True, run will be in asynchronous mode, if set to False
                it will wait for result (optional)
        :type background_mode: bool
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `SubscriptionResponse` result

        A way you may use me:

        >>> from ibm_watson_openscale import *
        >>> added_subscription_info = client.subscriptions.add(
                data_mart_id='997b1474-00d2-4g05-ac02-287ebfc603b5',
                service_provider_id='997b1474-00d2-4g05-ac02-287ebfc603b5',
                asset=Asset(...),
                deployment=AssetDeploymentRequest(...),
                asset_properties=AssetPropertiesRequest(...),
             )
        """
        validate_type(data_mart_id, 'data_mart_id', str, True)
        validate_type(service_provider_id, 'service_provider_id', str, True)
        
        if self._ai_client.check_entitlements is True and self._ai_client.plan_name == constants.LITE_PLAN:
            total_subscriptions = self.list().result.subscriptions
            if len(total_subscriptions) >= 5:
                raise Exception("You are not allowed to create more than 5 subscriptions for lite plan.")
        
        if asset_properties is None and training_data_stats is None:
            raise Exception("Either asset_properties or training_data_stats has to be passed")
     
        ### If "other" data type is present in output or input schema then remove it from subscription before saving it.
        ### https://github.ibm.com/aiopenscale/tracker/issues/19160
        if asset_properties is not None:
            asset_props = asset_properties.to_dict()
            if 'input_data_schema' in asset_props:
                input_schema = asset_props['input_data_schema']
                if input_schema is not None:
                    has_other_data_type = self._has_other_datatype(input_schema['fields'])
                    if has_other_data_type is True:
                        asset_properties.input_data_schema = None    
            if 'output_data_schema' in asset_props:    
                output_schema = asset_props['output_data_schema']
                if output_schema is not None:
                    has_other_data_type = self._has_other_datatype(output_schema['fields'])
                    if has_other_data_type is True:
                        asset_properties.output_data_schema = None
            if 'training_data_schema' in asset_props:    
                training_schema = asset_props['training_data_schema']
                if training_schema is not None:
                    has_other_data_type = self._has_other_datatype(training_schema['fields'])
                    if has_other_data_type is True:
                        asset_properties.training_data_schema = None 
                        
        if training_data_stats is None:
            response = super().add(data_mart_id=data_mart_id, service_provider_id=service_provider_id, asset=asset,
                                   deployment=deployment, asset_properties=asset_properties,
                                   risk_evaluation_status=risk_evaluation_status, 
                                   analytics_engine=analytics_engine,
                                   data_sources=data_sources)
        else:
            #Create subscription using data available in training stats
            if len(training_data_stats) == 0:
                raise Exception("training_data_stats is empty. Please re-generate and use it")
            response = self.__create_subscription_from_training_stats(data_mart_id, service_provider_id, training_data_stats, kwargs,background_mode )

        subscription_id = response.result.metadata.id

        if background_mode:
            return response
        else:
            def check_state() -> dict:
                details = self.get(subscription_id=subscription_id)
                return details.result.entity.status.state

            def get_result() -> Union[Tuple[str, Union[None, str], 'DetailedResponse']]:
                details = self.get(subscription_id=subscription_id)
                state = details.result.entity.status.state

                if state in [StatusStateType.ACTIVE]:
                    return "Successfully finished adding subscription", None, details
                else:
                    return "Add subscription failed with status: {}".format(state), \
                           'Reason: {}'.format(["code: {}, message: {}".format(error.code, error.message) for error in
                                                details.result.entity.status.failure.errors]), details

            return print_synchronous_run(
                'Waiting for end of adding subscription {}'.format(subscription_id),
                check_state,
                get_result=get_result,
                success_states=[StatusStateType.ACTIVE]
            )

    def delete(self,
               subscription_id: str,
               force: bool = None,
               background_mode: bool = True) -> Union['DetailedResponse', Optional[dict]]:
        """
        Delete subscription.

        :param str subscription_id: Unique subscription ID.
        :param bool force: (optional) force hard delete.
        :param background_mode: if set to True, run will be in asynchronous mode, if set to False
                it will wait for result (optional)
        :type background_mode: bool
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse

        A way you may use me:

        >>> client.subscriptions.delete(
                background_mode=False,
                subscription_id='997b1474-00d2-4g05-ac02-287ebfc603b5',
                force=True
             )
        """
        response = super().delete(subscription_id=subscription_id, force=force)

        if background_mode:
            return response
        else:
            def check_state() -> dict:
                details = self.list()
                if subscription_id not in str(details.result):
                    return StatusStateType.FINISHED
                else:
                    return StatusStateType.ACTIVE

            def get_result() -> Union[Tuple[str, Union[None, str], 'DetailedResponse']]:
                details = self.list()
                if subscription_id not in str(details.result):
                    state = StatusStateType.FINISHED
                else:
                    state = StatusStateType.ACTIVE

                if state in [StatusStateType.FINISHED]:
                    return "Successfully finished deleting subscription", None, response
                else:
                    return "Delete subscription failed", 'Reason: None', response  # TODO: Need to show the reason.

            return print_synchronous_run(
                'Waiting for end of deleting subscription {}'.format(subscription_id),
                check_state,
                get_result=get_result,
                success_states=[StatusStateType.FINISHED]
            )
            
    def _has_other_datatype(self, fields):
        for field in fields:
            type = field['type']
            if type == 'other':
                return True
        return False   
    
    #Private method to create subscription using training stats data
    def __create_subscription_from_training_stats(self, data_mart_id, service_provider_id, training_stats_info, params,background_mode):
        
        deployment_id = params.get("deployment_id")
        #Required in case of headless subscription
        deployment_name = params.get("deployment_name")
        deployment_space_id = params.get("deployment_space_id")
        model_type = training_stats_info['common_configuration']['problem_type']
        problem_type = None
        if model_type=="binary":
            problem_type = ProblemType.BINARY_CLASSIFICATION
        elif model_type=="multiclass":
            problem_type = ProblemType.MULTICLASS_CLASSIFICATION
        elif model_type=="regression":
            problem_type = ProblemType.REGRESSION    
        
        
        prediction_column = params.get("prediction_field")
        probability_columns = params.get("probability_fields")
        predicted_target_column = params.get("predicted_target_field")
        
        #validate_type(deployment_id, 'deployment_id', str, True)
        validate_type(prediction_column, 'prediction_field', str, True)
        #validate_type(predicted_target_column, 'predicted_target_field', str, True)
        
        if deployment_id is None and deployment_name is None :
            raise Exception("Please provide deployment_id if you have deployment information or else provide deployment_name in case you want to create headless subscription")
            
        model_asset_details_from_deployment = {}
        deployment_found = False
        if deployment_id is not None and deployment_space_id is not None:
            model_asset_details_from_deployment=self._ai_client.service_providers.get_deployment_asset(data_mart_id=data_mart_id,service_provider_id=service_provider_id,deployment_id=deployment_id,deployment_space_id=deployment_space_id)
            if model_asset_details_from_deployment['metadata']['guid']== deployment_id:
                deployment_found = True
            if not deployment_found :
                raise Exception("Deployment with id {} could not be found in deployment space {}. Please check again".format(deployment_id, deployment_space_id))    
        elif deployment_id is not None and deployment_space_id is None:
            #For non-WML model, pick the right deployment from list
            model_asset_details_from_deployment=self._ai_client.service_providers.list_assets(data_mart_id=data_mart_id,service_provider_id=service_provider_id).result    
            models = model_asset_details_from_deployment['resources']
            for model in models:
                if model['metadata']['guid']== deployment_id:
                    model_asset_details_from_deployment = model
                    deployment_found = True
                    break;
            if not deployment_found :
                raise Exception("Deployment with id {} could not be found. Please check again".format(deployment_id))
        elif deployment_id is None and deployment_space_id is not None:     
            raise Exception("Please provide deployment_id for space {}".format(deployment_space_id))
        else:
            print("Creating headless subscription as both deployment id and deployment space id are null")              
            
        input_data_schema = training_stats_info["common_configuration"]["input_data_schema"]
        fields = []
        label_column=training_stats_info["common_configuration"]["label_column"]
        # remove label column entry from input data schema
        for field in input_data_schema["fields"]:
            if field["name"] == label_column:
                continue
            fields.append(field)
        
        required_input_data_schema = {
            "type": "struct",
            "fields": fields
        }
        training_data_schema = None
          
        if deployment_name is not None and not deployment_found:
            model_asset_id = str(uuid.uuid4())  
            model_name = deployment_name   
            model_url = "https://dummyModelUrl"
            deployment_asset_id = str(uuid.uuid4()) 
            deployment_name = deployment_name 
            scoring_endpoint = "https://dummyScoringUrl"
        else:
            if not deployment_found:
                raise Exception("Deployment with id {} not found".format(deployment_id))    
            model_asset_id = model_asset_details_from_deployment["entity"]["asset"]["asset_id"] 
            model_name = model_asset_details_from_deployment["entity"]["asset"]["name"]   
            model_url = model_asset_details_from_deployment["entity"]["asset"]["url"]
            deployment_asset_id =  model_asset_details_from_deployment['metadata']['guid']
            deployment_name = model_asset_details_from_deployment['entity']['name']
            scoring_endpoint = model_asset_details_from_deployment['entity']['scoring_endpoint']['url']
        
        if model_asset_details_from_deployment is not None and len(model_asset_details_from_deployment)>0:     
            if "training_data_schema" in model_asset_details_from_deployment["entity"]["asset_properties"]:
                training_data_schema = SparkStruct.from_dict(model_asset_details_from_deployment["entity"]["asset_properties"]["training_data_schema"])
            
        return super().add(
                data_mart_id=data_mart_id,
                service_provider_id=service_provider_id,
                asset=Asset(
                    asset_id=model_asset_id,
                    name=model_name,
                    url=model_url,
                    asset_type=AssetTypes.MODEL,
                    input_data_type=InputDataType.STRUCTURED,
                    problem_type=problem_type
                ),
                deployment=AssetDeploymentRequest(
                    deployment_id=deployment_asset_id,
                    name=deployment_name,
                    deployment_type= DeploymentTypes.ONLINE,
                    url=scoring_endpoint
                ),
                asset_properties=AssetPropertiesRequest(
                    label_column=label_column,
                    probability_fields=probability_columns,
                    prediction_field=prediction_column,
                    predicted_target_field=predicted_target_column,
                    feature_fields = training_stats_info["common_configuration"]["feature_fields"],
                    categorical_fields = training_stats_info["common_configuration"]["categorical_fields"],
                    input_data_schema = SparkStruct.from_dict(required_input_data_schema),
                    training_data_schema=training_data_schema
                ),
                background_mode=background_mode
            )
        
    def create_feedback_table(self,
        subscription_id: str,
        **kwargs
    ) -> 'DetailedResponse':
        """
        Create a table for feedback dataset type.

        :param str subscription_id: Unique subscription ID.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `DataSetResponse` result
        """
        dataset_type = "feedback"
        payload = {}
        
        return super().tables(subscription_id=subscription_id, dataset_type=dataset_type, unknown_base_type=payload, **kwargs)
    
    def create_subscription(self, subscription_name: str, datamart_id, service_provider_id, configuration_archive, spark_credentials, data_warehouse_connection, payload_table: dict = {}, feedback_table: dict = {}, **kwargs):
        """
            Create batch subscription
            
            :param str subscription_name: Name of the subscription.
            :param str datamart_id: Datamart id in which we want to to create this subscription.
            :param str service_provider_id: Service Provider id.
            
            :param str configuration_archive: Path to the configuration archive file.
            :param dict spark_credentials: Dictionary containing spark connection information.
                Format for Remote Spark on hadoop 
                spark_credentials =  {
                    "connection":{
                        "endpoint": "<SPARK_ENDPOINT>",
                        "location_type": "custom"
                    },
                    "credentials": {
                        "username": "<USERNAME>",
                        "password": "<PASSWORD>"
                    },
                    "spark_settings": {
                        "max_num_executors": <MAX_EXECUTOR_COUNT>,
                        "min_num_executors": <MIN_EXECUTOR_COUNT>,
                        "executor_cores": <EXECUTOR_CORE>,
                        "executor_memory": <EXECUTOR_MEMORY>,
                        "driver_cores": <NUM_OF_DRIVER_CORES>,
                        "driver_memory": <DRIVER_MEMORY>
                    }                    
                }
                Format for IAE Spark
                spark_credentials = {
                "connection": {
                    "display_name": "<IAE_INSTANCE_DISPLAYNAME>",
                    "endpoint": "<IAE_JOB_ENDPOINT>",
                    "location_type": "cpd_iae",
                    "volume": "<VOLUME_NAME>"
                },
                "credentials": {
                    "username": "<USERNAME>",
                    "apikey": "<APIKEY>"
                },
                "spark_setting": {
                    #Look at remote spark settings
                }
            }
            :param dict data_warehouse_connection: Dictionary containing data warehouse (DB connection) information.  
                Format for the DB connection
                dataware_house_connection = {
                    "type": "jdbc",
                    "connection": {
                        "jdbc_driver": "com.ibm.db2.jcc.DB2Driver",
                        "use_ssl": False,
                        "certificate": None,
                        "jdbc_url": "jdbc:db2://<HOST>:50000/SAMPLE"        
                    },
                    "credentials": {
                         "username": "<USERNAME>",
                        "password": "<PASSWORD>"
                    }
                }
                
            :param dict payload_table: Dictionary containing payload table connection information.
                Format for the payload table 
                payload_table = {
                    "data": {
                        "auto_create": True,
                        "database": "SAMPLE",
                        "schema": "KP",
                        "table": "PAYLOAD_GERMAN_CREDIT_DATA_NEW"
                    },
                    "parameters":{
                        "partition_column": "WOS_PARTITION_COLUMN",
                        "num_partitions": 12
                    }
                }
            :param dict feedback_table: Dictionary containing feedback table connection information.
                Format for the feedback_table is same as payload table
            :return: subscription id
            :rtype: str
        
        """    
        
        validate_type(subscription_name, 'subscription_name', str, True)
        validate_type(datamart_id, 'data_mart_id', str, True)
        validate_type(service_provider_id, 'service_provider_id', str, True)
        #validate_type(configuration_archive, 'configuration_archive', str, True)
        validate_type(spark_credentials, 'spark_credentials', dict, True)
        validate_type(data_warehouse_connection, 'data_warehouse_connection', dict, True)
        validate_type(payload_table, 'payload_table', dict, False)
        validate_type(feedback_table, 'feedback_table', dict, False)
        
        self.__validate_data_warehouse_connetion(data_warehouse_connection)
        
        self.__validate_table_info(payload_table)
        self.__validate_table_info(feedback_table)
        
        #TODO validate parameters
        spark_engine_id = None
        db_integrated_system_id = None
        try:
            print("Creating integrated system for Spark")
            spark_engine_id = self.__create_spark_integrated_system(subscription_name, spark_credentials)
            
            print("Creating integrated system for Hive/DB2")
            
            db_integrated_system_id = self.__create_db2_hive_integrated_system(subscription_name,data_warehouse_connection)
            
            common_config = self.__get_common_configuration(configuration_archive)
            common_configuration = get(common_config,'common_configuration')
            
            # Set asset details
            asset = Asset(
                asset_id=str(uuid.uuid4()),
                url="",
                name=subscription_name,
                asset_type=AssetTypes.MODEL,
                input_data_type=InputDataType.STRUCTURED,
                problem_type=get(common_configuration,"model_type")
            )
            
            # Set deployment details       
            asset_deployment = AssetDeploymentRequest(
                deployment_id=str(uuid.uuid4()),
                name=subscription_name,
                description="This is {}".format(subscription_name),
                deployment_type="batch"
            )
            
                 
            asset_properties_request = AssetPropertiesRequest(
                label_column=get(common_configuration,"label_column"),
                probability_fields=[get(common_configuration,"probability")],
                prediction_field=get(common_configuration,"prediction"),
                feature_fields=get(common_configuration,"feature_columns"),
                categorical_fields=get(common_configuration,"categorical_columns")
            )    
            
            analytics_engine = AnalyticsEngine(
                type="spark",
                integrated_system_id=spark_engine_id,
                parameters = get(spark_credentials,"spark_settings",{})
            )  
            
            subscription_details = self.add(
                data_mart_id=datamart_id,
                service_provider_id=service_provider_id,
                asset=asset,
                deployment=asset_deployment,
                asset_properties=asset_properties_request,                
                analytics_engine=analytics_engine,
                background_mode = False
                ).result
                
        except Exception as e:
            #Delete all the integrated systems created for this failed subscription
            print("Creation of subscription failed")
            print(e)
            #ids = [spark_engine_id, payload_integrated_system_id,feedback_integrated_system_id,training_integrated_system_id]
            ids = [spark_engine_id, db_integrated_system_id]            
            self.__delete_integrated_sytems(ids)
            raise e
        
        subscription_id = subscription_details.metadata.id
        schemas_patch_document=[
                JsonPatchOperation(op=OperationTypes.REPLACE, path='/asset_properties/training_data_schema', value=common_configuration["training_data_schema"]),
                JsonPatchOperation(op=OperationTypes.REPLACE, path='/asset_properties/input_data_schema', value=common_configuration["input_data_schema"]),
                JsonPatchOperation(op=OperationTypes.REPLACE, path='/asset_properties/output_data_schema', value=common_configuration["output_data_schema"])
            ]
        
        self._ai_client.subscriptions.update(subscription_id=subscription_id, patch_document=schemas_patch_document)
        
         # Add selected tables as data sources
        data_sources = []
        source_type = get(data_warehouse_connection,"type")
        if len(payload_table) > 0 and get(payload_table,"data.table",None) is not None:
            data_sources.append(self.__get_data_source(payload_table, db_integrated_system_id, "payload", source_type))
            
        if len(feedback_table) > 0 and get(feedback_table,"data.table",None) is not None:
            data_sources.append(self.__get_data_source(feedback_table, db_integrated_system_id, "feedback", source_type))
        
        #patch datasources
        if len(data_sources) > 0:
            data_sources_patch_document=[
                 JsonPatchOperation(op=OperationTypes.ADD, path="/data_sources", value=data_sources)
            ]        
            self._ai_client.subscriptions.update(subscription_id=subscription_id, patch_document=data_sources_patch_document)
            print("DataSources updated")
        
        print("Subscription is getting created. Id is : {}".format(subscription_id))
        return subscription_id
    
    
    def __create_spark_integrated_system(self, subscription_name, spark_credentials):
        """
        Format of spark_credentials
        
        # Remote Spark example
        spark_credentials =  {
            "connection":{
                "endpoint": "http://wimps1.fyre.ibm.com:5000",
                "location_type": "custom"
            },
            "credentials": {
                "username": "<USERNAME>",
                "password": "<PASSWORD>"
            },
            "spark_settings": {
                "max_num_executors": 1,
                "min_num_executors": 1,
                "executor_cores": 1,
                "executor_memory": 2,
                "driver_cores": 1,
                "driver_memory": 2
            }
        }

        # IAE Spark example
        spark_credentials = {
            "connection": {
                "display_name": "<IAE_DISPLAY_NAME>",
                "endpoint": "<IAE_JOB_ENDPOINT>",
                "location_type": "cpd_iae",
                "volume": "<VOLUME_NAME>"
            },
            "credentials": {
                "username": "admin",
                "apikey": "<APIKEY>"
            },
            "spark_setting": {
                "max_num_executors": 1,
                "min_num_executors": 1,
                "executor_cores": 1,
                "executor_memory": 2,
                "driver_cores": 1,
                "driver_memory": 2
            }
        }

        """
        
        spark_engine_details = IntegratedSystems(self._ai_client).add(
                name=subscription_name + " - Spark Engine",
                description = " ",
                type=IntegratedSystemsListEnums.Type.SPARK.value,
                credentials= get(spark_credentials,"credentials"),
                connection=get(spark_credentials,"connection")
            ).result
            
        
        spark_engine_id = spark_engine_details.metadata.id
        
        print("Integrated system {} created ".format(spark_engine_id))
        
        return spark_engine_id
       
            
    def __create_db2_hive_integrated_system(self, subscription_name, table_info):  
        #system_types = list(set([get(payload_table,"type"),get(feedback_table,"type"),get(scored_training_data_table,"type")]))
        #if len(system_types)==1: #All are of same type
        connection_type = get(table_info,"type")
        hive_db2_connection = get(table_info,"connection")
        hive_db2_credentials = get(table_info,"credentials")
        if hive_db2_credentials is None:
            hive_db2_credentials = {}
            
        if connection_type==IntegratedSystemsListEnums.Type.HIVE.value:
            hive_db2_connection["location_type"] = "metastore"
        
        elif connection_type==IntegratedSystemsListEnums.Type.JDBC.value:
            hive_db2_connection["location_type"] =  IntegratedSystemsListEnums.Type.JDBC.value            
            hive_db2_credentials["jdbc_url"] = get(table_info,"connection.jdbc_url")
            
        hive_db2_connection_details = IntegratedSystems(self._ai_client).add(
                name=subscription_name + " - DB Info",
                description = "",
                type=connection_type,
                credentials=hive_db2_credentials,
                connection=hive_db2_connection
            ).result
        
                
        hive_db2_connection_id=hive_db2_connection_details.metadata.id
        print("Hive/Db2 Integrated system {} created".format(hive_db2_connection_id))
        
        return hive_db2_connection_id
    
    def __delete_integrated_sytems(self, ids):
        print("Cleaning up integration systems")
        for id in ids:
            if id is not None:
                print("Deleting {}".format(id))
                IntegratedSystems(self._ai_client).delete(id)
                
    def __get_common_configuration(self, configuration_archive):
        common_config = None
        with tarfile.open(configuration_archive, 'r:gz') as tar:
            if "common_configuration.json" not in tar.getnames():
                raise Exception("common_configuration.json file is missing in archive file")
            
            json_content = tar.extractfile('common_configuration.json')
            data = json_content.read().decode()
            common_config = json.loads(data)  
                 
        return common_config    
    
    def __validate_data_warehouse_connetion(self, connection_info):
        validate_type(get(connection_info,"type"), 'type', str, True)

        type = get(connection_info,"type")
        if type=="jdbc":
            
            validate_type(get(connection_info,"connection.use_ssl"), 'use_ssl', bool, False)
            use_ssl = get(connection_info,"connection.use_ssl",None)
            if use_ssl:
                validate_type(get(connection_info,"connection.certificate"), 'certificate', str, True)
            validate_type(get(connection_info,"connection.jdbc_driver"), 'jdbc_driver', str, True)
            validate_type(get(connection_info,"connection.jdbc_url"), 'jdbc_url', str, True)
            
            validate_type(get(connection_info,"credentials.username"), 'username', str, True)
            validate_type(get(connection_info,"credentials.password"), 'password', str, True)
         
        else:
            validate_type(get(connection_info,"connection.metastore_url"), 'metastore_url', str, True)
            kerberos_enabled = get(connection_info,"connection.kerberos_enabled",None)
            if kerberos_enabled is not None:
                 validate_type(get(connection_info,"connection.kerberos_enabled"), 'kerberos_enabled', bool, True)
                 if kerberos_enabled:
                     validate_type(get(connection_info,"credentials.kerberos_principal"), 'kerberos_principal', str, True)
                     delegation_token_urn = get(connection_info,"credentials.delegation_token_urn")
                     delegation_token_endpoint = get(connection_info,"credentials.delegation_token_endpoint")
                     if delegation_token_urn is None and delegation_token_endpoint is None:
                         raise Exception("Either delegation_token_urn or delegation_token_endpoint value is required when connecting to Kerberos Hive")
                         
                     
    def __validate_table_info(self, table_info):  
          
        validate_type(get(table_info,"data.auto_create"), 'auto_create', bool, True)
        validate_type(get(table_info,"data.database"), 'database', str, True)
        validate_type(get(table_info,"data.table"), 'table', str, True)                     
 
    def __get_data_source(self, table_info, integrated_system_id,table_type,source_type):
        
        auto_create = get(table_info,"data.auto_create",False)
        status = DataSourceStatus(state="new")
        
        
        parameters = None
        if "parameters" in table_info:
            parameters = get(table_info,"parameters")
        data_source = DataSource(
            type=table_type, 
            database_name=get(table_info,"data.database"), 
            schema_name=get(table_info,"data.database") if source_type==IntegratedSystemsListEnums.Type.HIVE.value else get(table_info,"data.schema"), 
            table_name=get(table_info,"data.table"), 
            auto_create = auto_create,
            status = status,
            connection=DataSourceConnection(
                type=source_type, 
                integrated_system_id=integrated_system_id
            ),
            parameters = parameters
        )
        return data_source.to_dict() 