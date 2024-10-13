import uuid
from google.cloud import compute_v1
from google.api_core.exceptions import GoogleAPICallError
import time

def check_and_create_vm_in_zone(compute_client, project_id, zone, gpu_type, network, subnetwork, machine_type, image_project, image_family, instance_name_base):
    """Checks for GPU availability and attempts to create a VM in the zone if available."""
    accelerator_client = compute_v1.AcceleratorTypesClient()

    # Check GPU availability in the zone
    try:
        accelerators = accelerator_client.list(project=project_id, zone=zone)
        for accelerator_type in accelerators:
            if gpu_type in accelerator_type.name:
                # GPU is available, attempt to create VM
                instance_name = f"{instance_name_base}-{str(uuid.uuid4())[:4]}"
                print(f"GPU {gpu_type} is available in {zone}. Creating VM {instance_name}...")

                operation = create_vm_with_gpu(
                    compute_client, project_id, zone, instance_name, network, subnetwork, machine_type, image_project, image_family, gpu_type
                )
                wait_for_operation(operation, project_id, zone)
                print(f"VM {instance_name} successfully created in zone {zone}.")
                return True, instance_name  # Successfully created VM
        print(f"No GPU {gpu_type} available in zone {zone}.")
    except GoogleAPICallError as e:
        print(f"Error checking GPUs or creating VM in zone {zone}: {e}")
    return False, None  # Failed to create VM or no GPU available

def create_vm_with_gpu(compute_client, project_id, zone, instance_name, network, subnetwork, machine_type, image_project, image_family, gpu_type):
    """Creates a VM instance with the specified GPU type."""
    # Configure the source image
    source_disk_image = f"projects/{image_project}/global/images/{image_family}"
    machine_type_full_path = f"zones/{zone}/machineTypes/{machine_type}"

    # Configure the boot disk
    disk = compute_v1.AttachedDisk()
    disk.initialize_params.source_image = source_disk_image
    disk.auto_delete = True
    disk.boot = True
    disk.initialize_params.disk_size_gb = 100

    # Configure the GPU
    guest_accelerator = compute_v1.AcceleratorConfig()
    guest_accelerator.accelerator_count = 1
    guest_accelerator.accelerator_type = f"zones/{zone}/acceleratorTypes/{gpu_type}"

    # Configure the network interface
    network_interface = compute_v1.NetworkInterface()
    network_interface.network = f"global/networks/{network}"
    region = zone[:-2]
    network_interface.subnetwork = f"projects/{project_id}/regions/{region}/subnetworks/{subnetwork}"

    # Configure scheduling
    scheduling = compute_v1.Scheduling()
    scheduling.on_host_maintenance = "TERMINATE"
    scheduling.automatic_restart = True

    # Create the VM instance configuration
    instance = compute_v1.Instance()
    instance.name = instance_name
    instance.disks = [disk]
    instance.machine_type = machine_type_full_path
    instance.network_interfaces = [network_interface]
    instance.guest_accelerators = [guest_accelerator]
    instance.scheduling = scheduling

    # Insert the VM instance
    operation = compute_client.insert(project=project_id, zone=zone, instance_resource=instance)

    return operation

def wait_for_operation(operation, project_id, zone):
    """Waits for the VM creation operation to finish."""
    operations_client = compute_v1.ZoneOperationsClient()

    while True:
        result = operations_client.get(project=project_id, zone=zone, operation=operation.name)
        if result.status == compute_v1.Operation.Status.DONE:
            if 'error' in result:
                raise GoogleAPICallError(result.error.errors[0].code)
            return result
        time.sleep(5)

def instance_exists(compute_client, project_id, zone, instance_name):
    """Check if the instance exists."""
    try:
        compute_client.get(project=project_id, zone=zone, instance=instance_name)
        return True  
    except GoogleAPICallError:
        return False

def delete_instance(compute_client, project_id, zone, instance_name):
    """Deletes the specified Compute Engine instance."""
    try:
        operation = compute_client.delete(project=project_id, zone=zone, instance=instance_name)
        wait_for_operation(operation, project_id, zone)
        print(f"Deleted VM instance {instance_name}.\n")
    except GoogleAPICallError as e:
        print(f"Failed to delete VM instance {instance_name} due to: {e}\n")

def find_and_create_vms(project_id, network, subnetwork, machine_type, image_family, image_project, gpu_type, max_vms):
    """Find zones with GPU and create VMs in them, testing up to a specified number of zones."""
    compute_client = compute_v1.InstancesClient()
    zones_client = compute_v1.ZonesClient()
    available_zones = zones_client.list(project=project_id)
    instance_name_base = "mg7609-vm"
    
    vm_counter = 0

    # Loop over each zone, checking availability and creating VMs as needed
    for zone in available_zones:
        if vm_counter >= max_vms:
            print(f"Reached maximum number of {max_vms} VMs. Stopping.")
            break

        zone_name = zone.name
        print(f"Checking availability in zone {zone_name}...")

        success, instance_name = check_and_create_vm_in_zone(
            compute_client, project_id, zone_name, gpu_type, network, subnetwork, machine_type, image_project, image_family, instance_name_base
        )

        if success:
            vm_counter += 1
        else:
            # Cleanup if instance was partially created
            if instance_name and instance_exists(compute_client, project_id, zone_name, instance_name):
                delete_instance(compute_client, project_id, zone_name, instance_name)

    print(f"VM creation process completed. {vm_counter} VMs created out of {max_vms}.")

if __name__ == "__main__":
    project_id = 'csci-ga-3003-085-fall24-3e17'
    network = "nyu-cs-cml-fall24-auto-vpc-1"
    subnetwork = "nyu-cs-cml-fall24-auto-vpc-1"
    machine_type = "n1-standard-4"
    image_project = "ml-images"
    image_family = "c1-deeplearning-tf-1-15-cu110-v20221107-debian-10"
    gpu_type = "nvidia-tesla-t4"
    max_vms = 1

    find_and_create_vms(project_id, network, subnetwork, machine_type, image_family, image_project, gpu_type, max_vms)