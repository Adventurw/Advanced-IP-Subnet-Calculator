from flask import Flask, render_template, request, jsonify
import ipaddress
from ipaddress import IPv4Network, IPv6Network
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def get_ip_class(ip):
    """Identify the class of an IPv4 address"""
    try:
        first_octet = int(ip.split('.')[0])
        
        if 1 <= first_octet <= 126:
            return "Class A (Default Mask: /8, 255.0.0.0)"
        elif 128 <= first_octet <= 191:
            return "Class B (Default Mask: /16, 255.255.0.0)"
        elif 192 <= first_octet <= 223:
            return "Class C (Default Mask: /24, 255.255.255.0)"
        elif 224 <= first_octet <= 239:
            return "Class D (Multicast)"
        elif 240 <= first_octet <= 255:
            return "Class E (Experimental)"
        else:
            return "Invalid IP"
    except:
        return "Invalid IP"

def cidr_to_mask(ip_cidr):
    """Convert CIDR to subnet mask"""
    try:
        network = IPv4Network(ip_cidr, strict=False)
        return str(network.netmask)
    except:
        return "Invalid CIDR"

def mask_to_cidr(ip, subnet_mask):
    """Convert subnet mask to CIDR notation"""
    try:
        network = IPv4Network(f"{ip}/{subnet_mask}", strict=False)
        return f"{ip}/{network.prefixlen}"
    except:
        return "Invalid IP/Mask"

def calculate_vlsm(ip, prefix, subnet_sizes):
    """Calculate VLSM subnets for given subnet sizes"""
    try:
        network = IPv4Network(f"{ip}/{prefix}", strict=False)
        subnet_sizes = sorted([int(size) for size in subnet_sizes], reverse=True)
        
        results = []
        remaining_subnet = network
        
        for size in subnet_sizes:
            new_prefix = 32 - (size - 1).bit_length() if size > 1 else 32
            for subnet in remaining_subnet.subnets(new_prefix=new_prefix):
                if subnet.num_addresses >= size:
                    results.append({
                        "required_hosts": size,
                        "subnet": str(subnet),
                        "network_address": str(subnet.network_address),
                        "broadcast_address": str(subnet.broadcast_address),
                        "prefix": new_prefix,
                        "usable_hosts": subnet.num_addresses - 2 if subnet.num_addresses > 2 else subnet.num_addresses
                    })
                    remaining_subnet = list(remaining_subnet.address_exclude(subnet))[0]
                    break
        
        return {
            "original_network": str(network),
            "allocated_subnets": results,
            "remaining_space": str(remaining_subnet) if remaining_subnet.num_addresses > 0 else "No space remaining"
        }
    except Exception as e:
        return {"error": str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        ip = data.get('ip', '').strip()
        if not ip:
            return jsonify({"error": "IP address is required"}), 400

        # Handle prefix
        prefix = data.get('prefix')
        if prefix is None:
            return jsonify({"error": "Prefix is required"}), 400
        
        try:
            prefix = int(prefix)
        except ValueError:
            return jsonify({"error": "Prefix must be a number"}), 400

        # Handle CIDR notation in IP field
        if '/' in ip:
            parts = ip.split('/')
            ip = parts[0]
            try:
                prefix = int(parts[1])
            except ValueError:
                return jsonify({"error": "Invalid prefix in CIDR notation"}), 400

        # IPv6 handling
        if ':' in ip:
            try:
                network = IPv6Network(f"{ip}/{prefix}", strict=False)
                new_prefix = data.get('new_prefix')
                
                if new_prefix is not None:
                    try:
                        new_prefix = int(new_prefix)
                        if new_prefix <= prefix:
                            return jsonify({"error": "New prefix must be larger than current prefix"}), 400
                        subnets = list(network.subnets(new_prefix=new_prefix))
                        return jsonify({
                            "ip_version": "IPv6",
                            "ip_class": "N/A (IPv6 uses CIDR only)",
                            "network_address": str(network.network_address),
                            "prefix": prefix,
                            "total_hosts": str(network.num_addresses),
                            "subnets": [{
                                "subnet": str(subnet),
                                "network_address": str(subnet.network_address),
                                "prefix": new_prefix,
                                "hosts": str(subnet.num_addresses)
                            } for subnet in subnets]
                        })
                    except ValueError:
                        return jsonify({"error": "New prefix must be a number"}), 400
                
                return jsonify({
                    "ip_version": "IPv6",
                    "ip_class": "N/A (IPv6 uses CIDR only)",
                    "network_address": str(network.network_address),
                    "prefix": prefix,
                    "total_hosts": str(network.num_addresses)
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 400

        # IPv4 VLSM handling
        subnet_sizes = data.get('subnet_sizes')
        if subnet_sizes:
            try:
                subnet_sizes = [int(size) for size in subnet_sizes]
                vlsm_result = calculate_vlsm(ip, prefix, subnet_sizes)
                if 'error' in vlsm_result:
                    return jsonify(vlsm_result), 400
                vlsm_result['ip_class'] = get_ip_class(ip)
                return jsonify(vlsm_result)
            except Exception as e:
                return jsonify({"error": str(e)}), 400

        # Basic IPv4 subnetting
        try:
            network = IPv4Network(f"{ip}/{prefix}", strict=False)
            new_prefix = data.get('new_prefix')
            
            if new_prefix is not None:
                try:
                    new_prefix = int(new_prefix)
                    if new_prefix <= prefix:
                        return jsonify({"error": "New prefix must be larger than current prefix"}), 400
                    subnets = list(network.subnets(new_prefix=new_prefix))
                    return jsonify({
                        "ip_version": "IPv4",
                        "ip_class": get_ip_class(ip),
                        "network_address": str(network.network_address),
                        "broadcast_address": str(network.broadcast_address),
                        "netmask": str(network.netmask),
                        "prefix": prefix,
                        "total_hosts": network.num_addresses,
                        "usable_hosts": network.num_addresses - 2 if network.num_addresses > 2 else network.num_addresses,
                        "subnets": [{
                            "subnet": str(subnet),
                            "network_address": str(subnet.network_address),
                            "broadcast_address": str(subnet.broadcast_address),
                            "first_host": str(subnet.network_address + 1) if subnet.num_addresses > 2 else "N/A",
                            "last_host": str(subnet.broadcast_address - 1) if subnet.num_addresses > 2 else "N/A",
                            "hosts": subnet.num_addresses - 2 if subnet.num_addresses > 2 else subnet.num_addresses
                        } for subnet in subnets]
                    })
                except ValueError:
                    return jsonify({"error": "New prefix must be a number"}), 400
            
            return jsonify({
                "ip_version": "IPv4",
                "ip_class": get_ip_class(ip),
                "network_address": str(network.network_address),
                "broadcast_address": str(network.broadcast_address),
                "netmask": str(network.netmask),
                "prefix": prefix,
                "total_hosts": network.num_addresses,
                "usable_hosts": network.num_addresses - 2 if network.num_addresses > 2 else network.num_addresses
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/convert', methods=['POST'])
def convert():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        if 'cidr' in data:
            cidr = data['cidr'].strip()
            if not cidr:
                return jsonify({"error": "CIDR notation is required"}), 400
            try:
                network = IPv4Network(cidr, strict=False)
                return jsonify({
                    "subnet_mask": str(network.netmask),
                    "ip_class": get_ip_class(cidr.split('/')[0])
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 400
        elif 'ip' in data and 'subnet_mask' in data:
            ip = data['ip'].strip()
            subnet_mask = data['subnet_mask'].strip()
            if not ip or not subnet_mask:
                return jsonify({"error": "Both IP and subnet mask are required"}), 400
            try:
                network = IPv4Network(f"{ip}/{subnet_mask}", strict=False)
                return jsonify({
                    "cidr": f"{ip}/{network.prefixlen}",
                    "ip_class": get_ip_class(ip)
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 400
        else:
            return jsonify({"error": "Either CIDR notation or both IP and subnet mask are required"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)