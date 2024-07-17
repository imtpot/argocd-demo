from pulumi import ComponentResource, ResourceOptions, export
from pulumi_command import local
from pulumi_kubernetes import Provider
from pulumi_kubernetes.core.v1 import Secret
from pulumi_kubernetes.helm.v3 import Release, RepositoryOptsArgs

class KindCluster(ComponentResource):
    def __init__(self, name: str, opts=None):
        super().__init__('custom:KindCluster', name, None, opts)
        
        self.cluster = local.Command(
            f'{name}-create',
            create=f'kind create cluster --name {name}',
            delete=f'kind delete cluster --name {name}',
            opts=ResourceOptions(parent=self)
        )
        
        self.kubeconfig = local.Command(
            f'{name}-kubeconfig',
            create=f'kind get kubeconfig --name {name}',
            opts=ResourceOptions(parent=self, depends_on=[self.cluster])
        )
        
        self.provider = Provider(
            f'{name}-provider',
            kubeconfig=self.kubeconfig.stdout,
            opts=ResourceOptions(parent=self, depends_on=[self.kubeconfig])
        )

class ArgoCD(ComponentResource):
    def __init__(self, name: str, cluster: KindCluster, opts=None):
        super().__init__('custom:ArgoCD', name, None, opts)
        
        self.argocd = Release(
            name,
            name="argocd",
            chart='argo-cd',
            version='7.3.7',
            repository_opts=RepositoryOptsArgs(repo='https://argoproj.github.io/argo-helm'),
            namespace='argocd',
            create_namespace=True,
            opts=ResourceOptions(provider=cluster.provider, parent=self)
        )

        self.secret = Secret.get(
            f'{name}-secret',
            'argocd/argocd-initial-admin-secret',
            opts=ResourceOptions(provider=cluster.provider, parent=self, depends_on=[self.argocd])
        )

cluster_1 = KindCluster('cluster-1')
argocd_1 = ArgoCD('argocd-1', cluster_1)
