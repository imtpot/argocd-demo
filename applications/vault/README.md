### Init

```bash
vault operator init  -key-shares=1 -key-threshold=1
vault operator unseal
vault login
vault auth enable kubernetes
vault write auth/kubernetes/config \
    kubernetes_host=https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_SERVICE_PORT
```

### Create Policy

```bash
vault policy write argocd-repo-server - <<EOF
path "secret/data/*" {
  capabilities = ["read"]
}
EOF
```

### Create Role

```bash
vault write auth/kubernetes/role/argocd-repo-server \
    bound_service_account_names=argocd-repo-server \
    bound_service_account_namespaces=argocd \
    policies=argocd-repo-server \
    ttl=24h
```

### Test

```bash
vault secrets enable -path=secret kv-v2
vault kv put secret/test_token token=test
vault kv put secret/podinfo repl=3
```
