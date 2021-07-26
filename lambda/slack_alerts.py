#message to slack from lambda function
import json
import urllib3

def lambda_handler(event, context):
    http = urllib3.PoolManager()
   
    data = {"text": "Sample Message from lambda pipeline function"}
   
    r = http.request("POST",
                      "https://hooks.slack.com/services/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",
                       body = json.dumps(data),
                       headers = {"Content-Type": "application/"})
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
