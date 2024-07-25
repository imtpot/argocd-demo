from pulumi import ComponentResource, ResourceOptions, Output, export
from pulumi_command import local
from pulumi_kubernetes import Provider
from pulumi_kubernetes.core.v1 import Secret
from pulumi_kubernetes.helm.v3 import Release, RepositoryOptsArgs
from base64 import b64decode

class KindCluster(ComponentResource):
    def __init__(self, name: str, opts=None):
        super().__init__("custom:KindCluster", name, None, opts)
        
        self.cluster = local.Command(
            f"{name}-create",
            create=f"kind create cluster --name {name}",
            delete=f"kind delete cluster --name {name}",
            opts=ResourceOptions(parent=self)
        )
        
        self.kubeconfig = local.Command(
            f"{name}-kubeconfig",
            create=f"kind get kubeconfig --name {name}",
            opts=ResourceOptions(parent=self, depends_on=[self.cluster])
        )
        
        self.provider = Provider(
            f"{name}-provider",
            kubeconfig=self.kubeconfig.stdout,
            opts=ResourceOptions(parent=self, depends_on=[self.kubeconfig])
        )

class ArgoCD(ComponentResource):
    def __init__(self, name: str, cluster: KindCluster, opts=None):
        super().__init__("custom:ArgoCD", name, None, opts)
        
        self.argocd = Release(
            name,
            name="argocd",
            chart="argo-cd",
            version="7.3.7",
            repository_opts=RepositoryOptsArgs(repo="https://argoproj.github.io/argo-helm"),
            namespace="argocd",
            create_namespace=True,
            opts=ResourceOptions(provider=cluster.provider, parent=self, depends_on=[cluster.cluster])
        )

        self.secret = Secret.get(
            f"{name}-secret",
            "argocd/argocd-initial-admin-secret",
            opts=ResourceOptions(provider=cluster.provider, parent=self, depends_on=[self.argocd])
        )

def decode_password(password: Output[str]) -> Output[str]:
    return password.apply(lambda p: b64decode(p).decode("utf-8"))

def apply_kustomize(cluster: KindCluster, overlay: str, depends_on=None):
    return local.Command(
        f"apply-kustomize-{cluster._name}",
        create=f"kubectl apply -k argocd/bootstrap/overlays/{overlay} --context kind-{cluster._name}",
        opts=ResourceOptions(depends_on=depends_on)
    )

# Create clusters
cluster_1 = KindCluster("cluster-1")
# cluster_2 = KindCluster("cluster-2", opts=ResourceOptions(depends_on=[cluster_1]))

# Deploy ArgoCD
argocd_1 = ArgoCD("argocd-1", cluster_1)
# argocd_2 = ArgoCD("argocd-2", cluster_2)

# Apply Kustomize overlays
production = apply_kustomize(cluster_1, "production", [argocd_1])
# staging = apply_kustomize(cluster_2, "staging", [argocd_2])

# Export ArgoCD admin passwords
export("argo-1-secret", decode_password(argocd_1.secret.data["password"]))
# export("argo-2-secret", decode_password(argocd_2.secret.data["password"]))
