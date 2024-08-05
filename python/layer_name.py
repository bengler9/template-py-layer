import json
import boto3
import pymysql
import base64
import sys
import html
from botocore.exceptions import ClientError

rds_proxy_host_param: str = "/rds/ServiceUpdates/proxyhost"
secret_name: str = "dev/ServiceUpdates/mysql"

# Create a Secrets Manager client
secretsmanagerclient = boto3.client('secretsmanager')

# Create a SSM client
ssmclient = boto3.client('ssm')

try:
    get_secret_value_response = secretsmanagerclient.get_secret_value(
        SecretId=secret_name
    )
except ClientError as e:
    if e.response['Error']['Code']:
        print("ERROR: Unexpected error: Could not get secret. ")
        print("More Error Info: " + str(e))
        raise e
else:
    # print("get_secret_value_response: "+str(get_secret_value_response))
    # Decrypts secret using the associated KMS CMK.
    # Depending on whether the secret is a string or binary, one of these fields will be populated.
    if 'SecretString' in get_secret_value_response:
        secrets = get_secret_value_response['SecretString']
    else:
        secrets = base64.b64decode(get_secret_value_response['SecretBinary'])

#print("secrets: "+str(secrets))
secretinjson=json.loads(secrets)
#print("secretinjson: "+str(secretinjson))

rds_proxy_host_response = ssmclient.get_parameter(
    Name=rds_proxy_host_param
)
#print("rds_proxy_host_response: " + str(rds_proxy_host_response))

# create the database connection outside of the handler to allow connections to be
# re-used by subsequent function invocations.
try:
        conn = pymysql.connect(host=rds_proxy_host_response['Parameter']['Value'], user=secretinjson['username'], passwd=secretinjson['password'], db=secretinjson['dbname'], connect_timeout=5)
except pymysql.MySQLError as e:
    print("ERROR: Unexpected error: Could not connect to MySQL instance.")
    sys.exit(1)

print("SUCCESS: Connection to RDS for MySQL instance succeeded")

def getProvidersActiveAws() -> list:
    item_count = 0
    result = []
    with conn.cursor() as cur:
        cur.execute(
            "SELECT `providers`.`id`, `providers`.`remote_account_id`, `providers`.`remote_assumerole_arn`, "
            "`providers`.`exec_assumerole_arn` "
            "FROM `providers` "
            "WHERE `providers`.`status_id`=1 AND `providers`.`supportedprovider_id`=1 AND "
            "`providers`.`account_id` != 1", ()
            )
        # print("The following providers have been added to the database:")
        for row in cur:
            item_count += 1
            # print(row)
            result.append(row)
    conn.commit()
    print("getProvidersActiveAws result: " + str(result))
    if result:
        return result
    else:
        return False

def getProvidersActiveCodeCommit() -> list:
    item_count = 0
    result = []
    with conn.cursor() as cur:
        cur.execute(
            "SELECT `providers`.`id`, `providers`.`remote_account_id`, `providers`.`remote_assumerole_arn`, "
            "`providers`.`exec_assumerole_arn` "
            "FROM `providers` "
            "WHERE `providers`.`status_id`=1 AND `providers`.`supportedprovider_id`=2 AND "
            "`providers`.`account_id` != 1", ()
            )
        # print("The following providers have been added to the database:")
        for row in cur:
            item_count += 1
            # print(row)
            result.append(row)
    conn.commit()
    print("getProvidersActiveCodeCommit result: " + str(result))
    if result:
        return result
    else:
        return False
