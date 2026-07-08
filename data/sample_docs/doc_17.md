# Kubernetes Pod Scheduling

Kubernetes schedules Pods onto Nodes based on resource requests and limits, node affinity rules, taints and tolerations, and other constraints, aiming to pack workloads efficiently while respecting the constraints each Pod declares. The scheduler runs in two phases: filtering, which eliminates Nodes that don't meet a Pod's requirements, and scoring, which ranks the remaining Nodes to select the best fit.

Resource requests specify the minimum CPU and memory a Pod needs, used by the scheduler to decide which Node has room for it, while resource limits cap the maximum a Pod is allowed to consume, with the container runtime throttling or killing the Pod if it exceeds its memory limit. Pods without resource requests set are scheduled opportunistically but are the first to be evicted under Node resource pressure.

Node affinity and anti-affinity rules let you require or prefer that Pods run on Nodes with specific labels, or avoid co-locating certain Pods together -- for example, spreading replicas of the same service across different availability zones for fault tolerance. Taints applied to a Node repel Pods unless those Pods have a matching toleration, commonly used to reserve specialized Nodes (like GPU machines) for specific workloads only.
