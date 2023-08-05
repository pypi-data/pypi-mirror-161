import boto3
from boto3.dynamodb.types import TypeSerializer, TypeDeserializer


class PmDynamoDb:
    def __init__(self, region_name, aws_access_key_id, aws_secret_access_key):
        try:
            self.aws_access_key_id = aws_access_key_id
            self.aws_secret_access_key = aws_secret_access_key

            self.dynamodb = boto3.resource('dynamodb',
                                           region_name=region_name,
                                           aws_access_key_id=self.aws_access_key_id,
                                           aws_secret_access_key=self.aws_secret_access_key
                                           )

            self.serializer = TypeSerializer()
            self.deserializer = TypeDeserializer()

            self.client = boto3.client('dynamodb',
                                       region_name=region_name,
                                       aws_access_key_id=self.aws_access_key_id,
                                       aws_secret_access_key=self.aws_secret_access_key)
        except ConnectionError as err:
            print(err)

        except Exception as ex:
            print(ex)

    @staticmethod
    def transaction_put(item, table_name, condition_expression, return_value):

        dict_put = {
            'Put': {
                'Item': item,
                'TableName': table_name,
                'ConditionExpression': condition_expression,
                'ReturnValuesOnConditionCheckFailure': return_value
            }
        }

        return dict_put

    @staticmethod
    def transaction_delete(key, table_name, condition_expression, return_value):

        dict_delete = {
            'Delete': {
                'Key': key,
                'TableName': table_name,
                'ConditionExpression': condition_expression,
                'ReturnValuesOnConditionCheckFailure': return_value
            }
        }

        return dict_delete

    @staticmethod
    def transaction_update(key, update_expression, table_name, condition_expression, expression_attribute_names,
                           expression_attribute_values, return_value):

        dict_update = {
            'Update': {
                'Key': key,
                'UpdateExpression': update_expression,
                'TableName': table_name,
                'ConditionExpression': condition_expression,
                'ExpressionAttributeNames': expression_attribute_names,
                'ExpressionAttributeValues': expression_attribute_values,
                'ReturnValuesOnConditionCheckFailure': return_value
            }
        }

        return dict_update

    @staticmethod
    def transaction_get(key, table_name, condition_expression):

        dict_get = {
            'Get': {
                'Key': key,
                'TableName': table_name,
                'ConditionExpression': condition_expression
            }
        }
        # 'ProjectionExpression': 'string',
        # 'ExpressionAttributeNames': {
        #     'string': 'string'
        # }

        return dict_get
