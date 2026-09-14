# Atlas Current Architecture

Atlas is an internal workload running in an on-premises AKS Kubernetes cluster. Its Microsoft SQL Server database is a separate on-premises dependency and is not deployed in Kubernetes.

```text
Corporate User
      |
      v
On-Prem Kubernetes / AKS
      |
      v
Kubernetes Service (atlas-web:8000)
      |
      v
Atlas Deployment
      |
      +---- Pod 1
      |
      +---- Pod 2
              |
              v
       External SQL Server
              |
              v
           AtlasDb
```

## Request flow

```text
Browser
   |
   v
Kubernetes Service
   |
   v
Atlas Pod
   |
   v
FastAPI Route
   |
   +---- Jinja2 -> HTML response
   |
   OR
   |
   +---- REST API -> JSON response
   |
   v
SQLAlchemy
   |
   v
PyODBC
   |
   v
External SQL Server
```

The Deployment runs two Linux application pods. The ClusterIP Service routes internal HTTP traffic to ready pods. Liveness tests the FastAPI process; readiness performs a database query. Pods require internal network and DNS connectivity to `DB_SERVER:DB_PORT` (TCP 1433 by default). SQL credentials enter the pods from `atlas-db-secret`, while other runtime values come from `atlas-config`.
