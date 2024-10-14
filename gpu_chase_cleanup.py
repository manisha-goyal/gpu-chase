import time
from google.cloud import compute_v1
from google.api_core.exceptions import GoogleAPICallError

def list_instances_by_prefix(compute_client, project_id, zone, prefix):
    """Lists all instances in a zone that start with a given prefix."""
    instances = compute_client.list(project=project_id, zone=zone)
    matched_instances = []

    for instance in instances:
        if instance.name.startswith(prefix):
            matched_instances.append(instance.name)

    return matched_instances

def delete_instance(compute_client, project_id, zone, instance_name):
    """Deletes the specified Compute Engine instance and waits for the operation to complete."""
    try:
        operation = compute_client.delete(project=project_id, zone=zone, instance=instance_name)

        # Embed waiting logic here for VM deletion completion
        operations_client = compute_v1.ZoneOperationsClient()
        print(f"Waiting for deletion of VM {instance_name} in {zone} to complete...")
        while True:
            result = operations_client.get(project=project_id, zone=zone, operation=operation.name)
            if result.status == compute_v1.Operation.Status.DONE:
                if 'error' in result:
                    raise GoogleAPICallError(result.error.errors[0].code)
                break
            time.sleep(5)

        print(f"Deleted VM instance {instance_name}.")
    except GoogleAPICallError as e:
        print(f"Failed to delete VM instance {instance_name} due to: {e}")

def delete_all_instances_with_prefix(project_id, prefix):
    """Finds and deletes all instances with a given prefix across all zones."""
    compute_client = compute_v1.InstancesClient()
    zones_client = compute_v1.ZonesClient()

    # Get all zones
    zones = zones_client.list(project=project_id)

    for zone in zones:
        zone_name = zone.name
        print(f"Checking for instances with prefix '{prefix}' in zone {zone_name}...")
        
        matched_instances = list_instances_by_prefix(compute_client, project_id, zone_name, prefix)
        
        if matched_instances:
            for instance_name in matched_instances:
                print(f"Deleting instance {instance_name} in zone {zone_name}...")
                delete_instance(compute_client, project_id, zone_name, instance_name)
        else:
            print(f"No instances with prefix '{prefix}' found in zone {zone_name}.")

if __name__ == "__main__":
    project_id = 'csci-ga-3003-085-fall24-3e17'
    instance_prefix = "mg7609-vm"

    delete_all_instances_with_prefix(project_id, instance_prefix)