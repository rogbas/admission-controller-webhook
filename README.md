# admission-controller-webhook

PoC of a admission-controller validation webhook for group creation
```
oc apply -f deploy/validation-webhook.deployment.yaml
oc apply -f deploy/validation-webhook.service.yaml
oc apply -f deploy/validation-webhook.route.yaml
oc apply -f deploy/group-validation.ValidatingWebhookConfiguration.yaml

```
