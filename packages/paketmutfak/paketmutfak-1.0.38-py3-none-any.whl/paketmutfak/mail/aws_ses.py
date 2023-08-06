from beartype import beartype
import boto3
from paketmutfak.utils.constants.error_codes import MessageCode


class AwsSes:
    """
        This class generated to send e-mail to slack.
    """
    def __init__(self, aws_access_key_id, aws_secret_access_key, dynamodb_region_name):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.dynamodb_region_name = dynamodb_region_name

        self.client = boto3.client(
                                'ses',
                                region_name=self.dynamodb_region_name,
                                aws_access_key_id=self.aws_access_key_id,
                                aws_secret_access_key=self.aws_secret_access_key,
                              )
        self.slack_email = ["attentionplease-aaaagi52yvw3me5bhzbitqf6em@paket-mutfak.slack.com"]
        self.default_source_address = 'no-reply@paketmutfak.com.tr'

    @beartype
    def send_email(self,
                   subject: str,
                   body: str,
                   recipient_addresses: list = None,
                   cc_addresses: list = None,
                   bcc_addresses: list = None,
                   automatic_reply_addresses: list = None,
                   tags: list = None,
                   source: str = None):

        try:
            if cc_addresses is None:
                cc_addresses = []
            if bcc_addresses is None:
                bcc_addresses = []
            if tags is None:
                tags = []
            if source is None:
                source = self.default_source_address
            if recipient_addresses is None:
                recipient_addresses = self.slack_email

            response = self.client.send_email(
                Source=source,
                Destination={
                    'ToAddresses': recipient_addresses,
                    'CcAddresses': cc_addresses,
                    'BccAddresses': bcc_addresses
                },
                Message={
                    'Subject': {
                        'Data': subject,
                        'Charset': 'UTF-8'
                    },
                    'Body': {
                        'Text': {
                            'Data': body,
                            'Charset': 'UTF-8'
                        }
                    }
                },
                # ReplyToAddresses=automatic_reply_addresses,
                # ReturnPath='',
                # SourceArn='',
                # ReturnPathArn='',
                Tags=tags
            )

            if response.get('ResponseMetadata', {}).get('HTTPStatusCode') == 200:
                return {"message_code": MessageCode.COMPLETED_MESSAGE}, 200
            else:
                return {"message_code": MessageCode.UNEXPECTED_ERROR_ON_SERVICE_MESSAGE}, 500

        except Exception as exp:
            return {"message_code": MessageCode.UNEXPECTED_ERROR_ON_SERVICE_MESSAGE, "exp": exp}, 500

    def verify_email_identity(self, email):
        try:
            response = self.client.verify_email_identity(
                EmailAddress=email
            )

            if response.get('ResponseMetadata', {}).get('HTTPStatusCode') == 200:
                return {"message_code": MessageCode.COMPLETED_MESSAGE}, 200
            else:
                return {"message_code": MessageCode.AWS_MAIL_ERROR}, 500

        except Exception as exp:
            return {"message_code": MessageCode.AWS_MAIL_ERROR, "exp": exp}, 500
