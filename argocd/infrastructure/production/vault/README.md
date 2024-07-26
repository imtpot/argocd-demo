### Init

```bash
vault operator init  -key-shares=1 -key-threshold=1
vault operator unseal
vault write auth/kubernetes/config \
    token_reviewer_jwt="$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)" \
    kubernetes_host="https://$KUBERNETES_PORT_443_TCP_ADDR:443" \
    kubernetes_ca_cert=@/var/run/secrets/kubernetes.io/serviceaccount/ca.crt
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
vault kv put secret/test_token token=test
