#!/bin/bash

APIM_TRADE_URL=${APIM_TRADE_URL:?'You must set the APIM_TRADE_URL environment variable to the URL of the Trade API in APIM'}
APIM_API_KEY=${APIM_API_KEY:?'You must set the APIM_API_KEY environment variable to the API subscrition key of the Trade API in APIM'}

for i in {1..100}
do
    echo "Payload $i -> HTTP"
    python gen-payload.py | curl -X POST -H "Content-Type: application/json" -H "Ocp-Apim-Subscription-Key: $APIM_API_KEY" -d @- $APIM_TRADE_URL
done
