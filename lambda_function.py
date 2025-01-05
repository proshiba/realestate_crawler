import json
import collect_rent_data

def lambda_handler(event, context):
    callfunc = event.get("function")
    if callfunc == 'rent_data':
        collect_rent_data.main()
    else:
        raise ValueError('Invalid function')
    return {
        'statusCode': 200,
        'body': json.dumps('Crawling finished.')
    }
