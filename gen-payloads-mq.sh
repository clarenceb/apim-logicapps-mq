#!/bin/bash

for i in {1..100}
do
    echo "Payload $i -> MQ"
    python gen-payload.py | kubectl exec -it secureapphelm-ibm-mq-0 -- /opt/mqm/samp/bin/amqsput DEMO.REQUEST.TRADE secureapphelm
done
