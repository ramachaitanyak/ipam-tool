# This program recursively checks all the values.yaml files
# under current directory to identify duplicates under the YAML
# structure of 'deck':'deployment':'vips'.
# The duplicates identified are represented as below:
#
#- Found conflicting IP: 10.220.149.26 in following files
#   - /Users/rkavuluru/ipam/mars-az02/values.yaml
#   - /Users/rkavuluru/ipam/jupiter-az01/values.yaml
# Usage: python check_duplication.py (This needs to be run from the directory containing Ips)

import sys
import os
import yaml

walk_dir = os.getcwd()

# Debug only
# print('walk_dir = ' + walk_dir)

# Debug only
# Use walk_dir if run from anywhere else apart from helm-data root
# print('walk_dir (absolute) = ' + os.path.abspath(walk_dir))

# A dict of duplicate IPs
ips_dict = dict()

# Walking each directory under current directory recursively
for root, subdirs, files in os.walk(walk_dir):

    # Examine each file in a subdir
    for filename in files:
        # Check for IPs only in corresponding values.yaml file
        if filename == 'values.yaml':
            file_path = os.path.join(root, filename)
            # Exclude elb directory while examining for duplicates
            if 'elb' in file_path:
                continue
            with open(file_path, 'r') as stream:
                try:
                    # Open file as yaml
                    yaml_dict = yaml.safe_load(stream)
                    vips_dict = yaml_dict['deck']['deployment']['vips']
                    for domain in vips_dict:
                        for ir in vips_dict[domain]:
                            # Skip iterating over anycast VIPs
                            if "anycast" in ir:
                                continue
                            else:
                                # Add IPs to ips_dict along with domain and ir
                                iter_file_path = file_path + ", "+domain+ ", "+ir
                                each_ip = vips_dict[domain][ir]
                                ips_dict.setdefault(each_ip,[])
                                ips_dict[each_ip].append(iter_file_path)
                except yaml.YAMLError as exc:
                    print(exc)

# Capture exit status for calling program (CI/CD pipeline)
exit = 0
for key, values in ips_dict.items():
    if len(ips_dict[key]) > 1:
        exit = 1
        print('\t- Found conflicting IP: %s in following files' % (key))
        for value in values:
            print('\t\t- %s' % value)
sys.exit(exit)

