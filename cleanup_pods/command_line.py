import argparse
import logging
from kubernetes import client, config

# https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/
POD_PHASE = [
    # All Containers in the Pod have terminated in success, and will not be restarted.
    'succeeded',
    # All Containers in the Pod have terminated, and at least one Container has terminated in failure.
    # That is, the Container either exited with non-zero status or was terminated by the system.
    'failed'
]

# https://kubernetes.io/docs/tasks/administer-cluster/out-of-resource/
POD_REASON = ['evicted']


def delete_pod(name, namespace):
    core_v1 = client.CoreV1Api()
    delete_options = client.V1DeleteOptions()
    api_response = core_v1.delete_namespaced_pod(
        name=name,
        namespace=namespace,
        body=delete_options)
    logging.info(api_response)


def cleanup(args):
    config.load_kube_config()
    core_v1 = client.CoreV1Api()
    pod_list = core_v1.list_namespaced_pod(args.namespace)
    for pod in pod_list.items:
        logging.info(pod.status)
        logging.info(pod.status.reason)
        pod_phase, pod_reason = pod.status.phase, pod.status.reason
        if pod_phase.lower() in POD_PHASE or (pod_reason and pod_reason.lower() in POD_REASON):
            delete_pod(pod.name, args.namespace)


def main():
    parser = argparse.ArgumentParser(description='Clean up k8s pods in evicted/failed/succeeded states.')
    parser.add_argument('--namespace', dest='namespace', default='default', type=str,
                        help='Namespace')
    args = parser.parse_args()
    cleanup(args)
