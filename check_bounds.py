import csv
import sys
import os
import yaml
import ipaddress

def check_bound(ip, subnets):
    for subnet in subnets:
        # Check if the ip is found in any subnet
        if ipaddress.ip_address(ip) in ipaddress.ip_network(subnet):
            return True
    # Return false if it is not in any valid ip subnet
    return False

subnet_list = []

with open('subnets.txt') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        subnet_list.append(row[0])
        line_count += 1

# A dict of IPs and paths

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
                            # Add IPs to ips_dict along with domain and ir
                            iter_file_path = file_path + ", "+domain+ ", "+ir
                            each_ip = vips_dict[domain][ir]
                            ips_dict[each_ip] = iter_file_path
                except yaml.YAMLError as exc:
                    print(exc)

# Capture exit status for calling program (CI/CD pipeline)
ret_val = 0
for key, value in ips_dict.items():
    # Check if the IP is in a valid bound
        if (check_bound(key, subnet_list)):
            continue
        else:
            print('\t- Found out of bounds IP: %s in following files' % (key))
            print('\t\t- %s' % value)
            ret_val = 1
sys.exit(ret_val)

