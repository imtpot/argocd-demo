# ArgoCD Overlays Demo

This Pulumi project sets up multiple Kind (Kubernetes in Docker) clusters, deploys ArgoCD to each of them, and applies Kustomize overlays.

## Prerequisites

- [Pulumi](https://www.pulumi.com/docs/get-started/install/)
- [Docker](https://docs.docker.com/get-docker/)
- [Kind](https://kind.sigs.k8s.io/docs/user/quick-start/#installation)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)

## Components

### KindCluster

The `KindCluster` component creates a Kind cluster and sets up the necessary Kubernetes provider.

### ArgoCD

The `ArgoCD` component deploys ArgoCD to a specified Kind cluster using Helm.

### Kustomize Overlay Application

The `apply_kustomize` function applies Kustomize overlays to the clusters after ArgoCD is deployed.

## Usage

1. Clone this repository:

   ```
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

3. Initialize a new Pulumi stack:

   ```
   pulumi stack init dev
   ```

4. Deploy the infrastructure:

   ```
   pulumi login --local
   pulumi up
   ```

   This will:
   - Create two Kind clusters
   - Deploy ArgoCD to each cluster
   - Apply the production Kustomize overlay to the first cluster
   - Apply the staging Kustomize overlay to the second cluster

5. Access ArgoCD:

   To get the ArgoCD admin passwords:

   ```
   pulumi stack output --show-secrets
   ```

   Use these passwords with the username `admin` to log in to the ArgoCD UI.

6. Clean up:

   When you're done, you can destroy all created resources:

   ```
   pulumi destroy
   ```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Specify your license here]
