APIM + Logic Apps + MQ integration
==================================

Demonstrate APIM receiving a payload and passing it to a Logic Apps workflow which puts a message onto IBM MQ queue for downstream processing.

Set / Load environment variables
--------------------------------

Copy file env.sh.template to env.sh and update the values.

```sh
source ./env.sh
```

Create AKS cluster
------------------

```sh
az group create --name $RESOURCE_GROUP --location $LOCATION

az aks create \
    --resource-group $RESOURCE_GROUP \
    --name $CLUSTER_NAME \
    --node-count 3 \
    --network-plugin azure \
    --network-plugin-mode overlay \
    --pod-cidr 192.168.0.0/16 \
    --enable-managed-identity
    --generate-ssh-keys \
    --enable-addons monitoring \
    --enable-msi-auth-for-monitoring

az aks get-credentials --resource-group $RESOURCE_GROUP --name $CLUSTER_NAME
```

Deploy IBM MQ via Sample Helm Chart
-----------------------------------

```sh
git clone https://github.com/ibm-messaging/mq-helm.git

cd mq-helm/samples/AzureAKS/deploy
./install.sh

kubectl get statefulset
kubectl get pod
kubectl get service
# secureapphelm-ibm-mq-loadbalancer   LoadBalancer   <cluster-ip>   <external-ip>   1414:32709/TCP,9443:31804/TCP   18h

kubectl exec -it secureapphelm-ibm-mq-0 -- /bin/bash
dspmq
# QMNAME(secureapphelm)                                     STATUS(Running)

# Get the channel name
runmqsc secureapphelm
DISPLAY CHANNEL (*) CHLTYPE(SVRCONN)

# AMQ8414I: Display Channel details.
#    CHANNEL(DEV.APP.SVRCONN)                CHLTYPE(SVRCONN)
exit
```

Access the IBM MQ console
-------------------------

Using the load balancer IP address from earlier, visit:

[https://{IP_address}:9443/ibmmq/console/#/](https://{IP_address}:9443/ibmmq/console/#/)

Login with `admin` / `passw0rd` for the default admin credentials.

Deploy a logic app standard
---------------------------

Configure the private CA certificate for the MQ server

- Copy the server.crt and rename to server.cer
- Upload server.cer to the logic app under Settings / Certificates / Public Key Certificates (.cer)
- Copy the thumbprint of the public key certificate
- Under Settings / Configuration, add a new variable "WEBSITE_LOAD_ROOT_CERTIFICATES" with the value of the public key certificate thumbprint

### Add workflow - Message Queue trigger (input from a MQ queue, write to another MQ queue)

Create a new Logic App workflow.

- Add a MQ trigger (polling every 1 minute) with a new MQ connection settings:

  - mq_channelName = DEV.APP.SVRCONN
  - mq_connectAs = app
  - mq_connectionTimeoutSeconds = 60
  - mq_maxConnections = 10
  - mq_password = passw0rd
  - mq_portNumber = 1414
  - mq_queueManagerName = secureapphelm
  - mq_serverName = <load_balancer_IP_address>
  - mq_userName = app
  - mq_useTLS = True

- Retrieve multiple messages (50 max)
- For Each trade:
  - Add a Condition to check if notional > 100000
  - If True, Place trade in the DEMO.LARGE.TRADE queue (reuse MQ connection above)
  - If False, Place trade in the DEMO.REGULAR.TRADE queue (reuse MQ connection above)

Test the workflow:

```sh
./gen-payloads-mq.sh
```

### Add workflow - HTTP request trigger from APIM (output to a MQ queue)

Create a new Logic App workflow.

- Add a Request (HTTP) trigger
- Add a Condition to check if notional > 100000
- If True, Place trade in the DEMO.LARGE.TRADE queue (reuse MQ connection above)
- If False, Place trade in the DEMO.REGULAR.TRADE queue (reuse MQ connection above)
- Return Response 202 Accepted with the request body

Test the workflow:

```sh
# Add the Logic App URL to env.sh
source ./env.sh

./gen-payloads-http.sh
```

### (Optional) Add Workflow endpoint to API Management

Create an APIM instance

Add an endpoint to the Logic App HTTP Triggered workflow

Update the file env.sh to use APIM endpoint instead of Logic App endpoint

Cleanup
-------

Stop the AKS cluster to save costs:

```sh
az aks stop -n $CLUSTER_NAME -g $RESOURCE_GROUP
```

Pause the MQ triggered workflow when not in use to avoid unnecessary polling, otherwise:

```sh
# Delete everything
az group delete --name $RESOURCE_GROUP --location $LOCATION
```

Resources
---------

- [Get an IBM MQ queue for development running on Azure](https://developer.ibm.com/tutorials/mq-connect-app-queue-manager-cloud-azure/) - IBM Developer
- [IBM MQ Sample Helm Chart](https://github.com/ibm-messaging/mq-helm) - GitHub
- [IBM MQ container](https://github.com/ibm-messaging/mq-container) - GitHub
