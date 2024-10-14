# Google Cloud GPU Chase

This project automates the process of finding available GPUs in various Google Cloud zones and attempts to create Virtual Machine (VM) instances with the selected GPU. It also provides functionality to delete all instances that match a given prefix to assist in resource cleanup and avoid unwanted charges.

## Features

- Iterates through multiple regions and zones to identify GPU availability.
- Attempts to create a VM instance with the desired GPU type in available zones.
- Provides a summary of success or failure for VM creation.
- Cleans up resources in case of failures to avoid unwanted charges.
- Deletes all instances that match a specified prefix (e.g., cleanup for test VMs created during the GPU chase).

## Prerequisites

Before running this project, ensure you have the following:

- A Google Cloud project with billing enabled.
- The [Google Cloud SDK](https://cloud.google.com/sdk) installed and initialized.
- Compute Engine API enabled in your Google Cloud project.
- Python 3.7+ installed on your system.
- Appropriate permissions to create and delete Compute Engine instances.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/manisha-goyal/gpu-chase.git
    cd gpu-chase
    ```

2. Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

3. Authenticate with Google Cloud:
    ```bash
    gcloud auth login
    gcloud config set project <your-project-id>
    ```

## Configuration

Modify the `gpu_chase.py` and `delete_instances.py` scripts to set the following variables as per your setup:

- **In `gpu_chase.py`:**
  - `project_id`: Your Google Cloud project ID. (e.g., `csci-ga-3003-085-fall24-3e17`)
  - `network`: The network name to use for the VM. (e.g., `nyu-cs-cml-fall24-auto-vpc-1`)
  - `subnetwork`: The subnetwork name to use for the VM. (e.g., `nyu-cs-cml-fall24-auto-vpc-1`)
  - `machine_type`: The machine type for the VM. (e.g., `n1-standard-4`)
  - `image_project`: The project that hosts the image family. (e.g., `ml-images`)
  - `image_family`: The image family for the VM's OS disk. (e.g., `c1-deeplearning-tf-1-15-cu110-v20221107-debian-10`)
  - `gpu_type`: The GPU type to search for. (e.g., `nvidia-tesla-t4`)
  - `max_vms`: The maximum number of VMs to create. (e.g., `10`)
  
- **In `gpu_chase_cleanup.py`:**
  - `project_id`: Your Google Cloud project ID. (e.g., `csci-ga-3003-085-fall24-3e17`)
  - `instance_prefix`: The prefix of the instance names to delete (e.g., `mg7609-vm`).

## Usage

### Searching for GPUs and Creating VMs

To search for available GPUs and create VMs, run:

```bash
python gpu_chase.py
```

This script will:
- Search through multiple zones for GPU availability.
- Attempt to create a VM in each zone with available GPUs.
- Output the status of VM creation (success or failure) and log any issues.

### Deleting VM Instances by Prefix

To delete all VM instances that start with a specific prefix (e.g., `mg7609-vm`), use:

```bash
python gpu_chase_cleanup.py
```

This script will:
- Search through all zones for instances whose names match the given prefix.
- Delete all matching instances.
- Output the status of deletion for each instance (success or failure).

## Example Output

### GPU Search and VM Creation

```bash
Checking availability in zone us-east1-b...
No GPU nvidia-tesla-t4 available in zone us-east1-b.
Checking availability in zone us-east1-c...
GPU nvidia-tesla-t4 is available in us-east1-c. Creating VM mg7609-vm-62c7...
Waiting for operation to create VM mg7609-vm-62c7 in us-east1-c to complete...
VM mg7609-vm-62c7 successfully created in zone us-east1-c.
```

### VM Deletion

```bash
Checking availability in zone us-east1-b...
No GPU nvidia-tesla-t4 available in zone us-east1-b.
Checking availability in zone us-east1-c...
GPU nvidia-tesla-t4 is available in us-east1-c. Creating VM mg7609-vm-62c7...
Waiting for operation to create VM mg7609-vm-62c7 in us-east1-c to complete...
VM mg7609-vm-62c7 successfully created in zone us-east1-c.
```

## Cleanup

### Manually Deleting a Specific VM

After verifying the VM, you can manually delete it to avoid unwanted charges:

```bash
gcloud compute instances delete <instance_name> --zone <zone>
```

### Batch Deletion Using the Script

To delete all VMs created with a specific prefix (e.g., test VMs), you can use the `gpu_chase_cleanup.py` script, which will delete all instances with a matching name prefix:

```bash
python gpu_chase_cleanup.py
```

## License

This project is licensed under the MIT License.