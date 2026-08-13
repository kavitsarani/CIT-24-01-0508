# Lab 6 Checkpoint Answers

## Checkpoint Q1

**Explain the difference between the control plane and a worker node.**

The control plane is the decision-making layer of the cluster. It does not run application containers itself. Instead, it consists of the API server (the entry point for all kubectl commands and internal communication), etcd (the database that stores the entire cluster's state), the scheduler (which decides which node a new pod should run on), and the controller manager (which continuously runs reconciliation loops to keep actual state matching desired state).

A worker node, by contrast, is where the actual application containers run. Each worker node runs a kubelet (the agent that talks to the control plane and manages containers on that node), kube-proxy (which handles network routing for Services), and a container runtime (like Docker or containerd) that actually pulls images and runs containers. In a Minikube single-node setup, both roles run on the same machine, but conceptually they are still separate responsibilities.

## Checkpoint Q2

**Delete and recreate the pod, check its IP. Has it changed? Why?**

Yes, the IP changed. This demonstrates that Pods are ephemeral. A Pod has no permanent identity. When a Pod is deleted, Kubernetes does not restart the same instance; it removes it entirely and, if recreated, the new Pod is scheduled fresh and assigned a new IP address from the cluster's pod network range. This is exactly why relying on a Pod's IP directly is unreliable, and why Services exist to provide a stable address that does not change even as the Pods behind it come and go.

## Checkpoint Q3

**Using the control-loop model, describe step by step what Kubernetes did when you deleted the pod.**

1. **Desired State**: The Deployment manifest declared replicas: 3, so the cluster's desired state (stored in etcd) says there should always be 3 running Pods matching the app: frontend label.
2. **Controller watches**: The Deployment controller (part of the Controller Manager) continuously watches the actual state of Pods via the API server.
3. **Actual State**: When I deleted one Pod, the actual number of running replicas dropped from 3 to 2.
4. **Gap Detected**: The controller's next reconciliation check compared desired (3) against actual (2) and found a mismatch.
5. **Reconcile**: The controller created a new Pod to replace the deleted one, bringing actual state back to 3 and closing the gap without any manual intervention from me.

## Checkpoint Q4

**Why will you be able to scale the frontend without touching the database tier?**

Because each tier — frontend, API, cache, and database — is defined as its own independent Kubernetes object (a separate Deployment or StatefulSet) with its own manifest and its own replica count. Scaling the frontend Deployment only changes the replicas field in the frontend's own spec; it has no reference to or dependency on the postgres StatefulSet's configuration. This is exactly what the lecture meant by "each service can scale independently" — the tiers are decoupled by design, so operationally, changing one never risks accidentally affecting another.

## Checkpoint Q5

**What is the difference between port-forward and a Service? Why do Services matter given that Pods are ephemeral?**

kubectl port-forward opens a temporary local tunnel directly to one specific Pod's IP address. It only works while that exact terminal session stays open, and if that particular Pod is deleted or replaced, the tunnel breaks immediately because it was pointed at an IP that no longer exists.

A Service, on the other hand, has a stable virtual IP and DNS name that does not change. It uses a label selector (for example, app: frontend) to automatically route traffic to whichever Pods currently match that label — regardless of how many times those Pods get replaced or what their individual IPs are at any given moment. This matters precisely because Pods are ephemeral: without a Service, every time a Pod restarted and got a new IP, anything trying to reach it would break. Services solve this by giving clients one consistent address to talk to while Kubernetes handles routing to the current healthy Pods behind the scenes.

## Checkpoint Q6

**Why would this update-and-rollback be much harder with Docker Compose alone?**

Docker Compose has no built-in concept of gradual, monitored rollouts or revision history. Updating an image in Compose typically means stopping the existing container(s) and starting new ones, which causes downtime, and if the new version has a problem, there is no automatic mechanism to detect that and roll back; you would have to manually track the previous image tag and manually revert it yourself.

Kubernetes Deployments, by contrast, perform a rolling update: new Pods are created gradually while old ones are only terminated once the new ones report healthy, meaning near-zero downtime. Kubernetes also automatically keeps a revision history, so kubectl rollout undo can instantly revert to the exact previous working configuration with a single command — something Compose has no native equivalent for.

## Checkpoint Q7

**Why do frontend/API use a Deployment while the database uses a StatefulSet?**

The frontend and API tiers are stateless — any replica is functionally identical and interchangeable with any other. It does not matter which specific Pod handles a request, and Pods can be created, destroyed, or replaced in any order without consequence. A Deployment fits this perfectly because it treats replicas as an anonymous, interchangeable pool with random Pod names and no persistent storage tied to any individual Pod.

The database tier is stateful — it needs a stable, predictable identity (postgres-0), stable network addressing (via the headless Service), ordered and predictable creation/deletion, and critically, its own dedicated persistent volume that stays associated with that specific Pod identity even if it is rescheduled. A StatefulSet is designed exactly for this: it guarantees stable naming, ordered pod management, and a 1:1 relationship between each replica and its own PersistentVolumeClaim — none of which a plain Deployment provides.

## Checkpoint Q8

**Would the data have survived if postgres was a plain Deployment without a PVC?**

No. Without a PersistentVolumeClaim, a container's data lives only in its own writable filesystem layer, which exists only as long as that specific container instance does. When a Pod is deleted (even if a Deployment immediately creates a replacement), the new Pod's container starts completely fresh from the base image — none of the previous container's filesystem changes carry over. So any data written to disk inside the container would simply be gone the moment the Pod was deleted, regardless of whether a replacement Pod exists.

I actually observed this dynamic during the lab: when Docker Desktop crashed unexpectedly outside of Kubernetes and the postgres Pod's shutdown was not clean, even with a PVC in place, the database initially failed to come back up correctly and needed to be reinitialized — showing how fragile stateful data is even with persistent storage, let alone without it.

## Checkpoint Q9

**What status did the broken pod show? Does it match the lecture's Pod Status table exactly, or is it a related status?**

The broken pod showed ErrImagePull, which then progressed to ImagePullBackOff on subsequent checks. This is not one of the four statuses explicitly listed in the lecture's Pod Status table (Running / Pending / CrashLoopBackOff / OOMKilled), but it is a closely related status in the same family as those failure states. It means the Pod was successfully scheduled onto a node (so it is technically past Pending), but the kubelet was unable to pull the specified container image — in this case because the tag nginx:definitely-not-a-real-tag does not exist on Docker Hub. ImagePullBackOff specifically indicates Kubernetes is retrying the pull with exponential backoff rather than retrying immediately and endlessly, which prevents hammering the registry with repeated failed requests.
