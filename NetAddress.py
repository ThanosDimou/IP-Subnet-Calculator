import tkinter as tk
from tkinter import messagebox, ttk
import ipaddress
import sys
import io

def is_valid_ip(ip):
    try:
        ip_obj = ipaddress.ip_address(ip)
        print(f"Valid IP address: {ip} (IPv{ip_obj.version})")
        return ip_obj
    except ValueError as e:
        print(f"Invalid IP address: {ip}. Error: {e}")
        return None

def is_valid_subnet_mask(mask, ip_version):
    try:
        if ip_version == 4:
            network = ipaddress.IPv4Network(f"0.0.0.0/{mask}", strict=False)
        else:  # IPv6
            network = ipaddress.IPv6Network(f"::{mask}", strict=False)
        
        print(f"Mask: {mask}, Prefix length: {network.prefixlen}")
        return True
    except ValueError as e:
        print(f"ValueError in is_valid_subnet_mask: {e}")
        return False

def calculate_subnets(network, new_prefix):
    try:
        current_prefix = network.prefixlen
        if new_prefix <= current_prefix:
            return 0
        return 2 ** (new_prefix - current_prefix)
    except ValueError as e:
        print(f"Error calculating subnets: {e}")
        return 0

def cidr_to_subnet_mask(cidr, ip_version):
    if ip_version == 4:
        return str(ipaddress.IPv4Network(f"0.0.0.0/{cidr}").netmask)
    else:  # IPv6
        return f"/{cidr}"  # Για IPv6, επιστρέφουμε το CIDR notation

def calculate():
    redirect_output()
    ip_address = ip_address_field.get()
    subnet_mask = subnet_mask_field.get()
    
    # Check if subnet mask does not start with '/' and handle it
    if not subnet_mask.startswith('/'):
        try:
            if '.' in subnet_mask or ':' in subnet_mask:
                subnet_mask = '/' + str(ipaddress.ip_network(f"0.0.0.0/{subnet_mask}", strict=False).prefixlen)
            else:
                subnet_mask = '/' + subnet_mask
        except ValueError:
            messagebox.showerror("Error", "Invalid subnet mask")
            return
        
    new_subnet_prefix = new_subnet_prefix_field.get()
    if new_subnet_prefix:
        if new_subnet_prefix.startswith('/'):
            new_subnet_prefix = new_subnet_prefix[1:]  # Αφαιρέστε την κάθετο αν υπάρχει
        try:
            new_subnet_prefix = int(new_subnet_prefix)
        except ValueError:
            messagebox.showerror("Error", "Invalid new subnet prefix")
            return

    print(f"IP Address: {ip_address}")
    print(f"Subnet Mask: {subnet_mask}")

    ip_obj = is_valid_ip(ip_address)
    if not ip_obj:
        messagebox.showerror("Error", "Invalid IP address")
        return

    ip_version = ip_obj.version

    try:
        cidr = int(subnet_mask[1:])
        max_cidr = 32 if ip_version == 4 else 128
        if 0 <= cidr <= max_cidr:
            subnet_mask = cidr_to_subnet_mask(cidr, ip_version)
            print(f"Converted CIDR to subnet mask: {subnet_mask}")
        else:
            messagebox.showerror("Error", f"Invalid CIDR notation for IPv{ip_version}")
            return
    except ValueError:
        messagebox.showerror("Error", "Invalid subnet mask")
        return

    print(f"Subnet mask before validation: {subnet_mask}")
    if not is_valid_subnet_mask(subnet_mask, ip_version):
        messagebox.showerror("Error", "Invalid subnet mask")
        return

    try:
        if ip_version == 4:
            network = ipaddress.ip_network(f"{ip_address}/{cidr}", strict=False)
            result_text.set(f"Network address: {network.network_address}\n"
                            f"Broadcast address: {network.broadcast_address}\n"
                            f"Subnet mask: {subnet_mask if ip_version == 4 else f'/{network.prefixlen}'}\n"
                            f"Wildcard mask: {network.hostmask}\n"
                            f"CIDR notation: /{network.prefixlen}\n"
                            f"Number of addresses: {network.num_addresses}\n"
                            f"Usable addresses: {network.num_addresses - 2}\n"
                            f"IP version: IPv{ip_version}\n"
                            f"First usable address: {network.network_address + 1}\n"
                            f"Last usable address: {network.broadcast_address - 1}\n"
                            f"Number of subnets: {calculate_subnets(network, int(new_subnet_prefix)) if new_subnet_prefix else 'N/A'}")
        else:  # IPv6
            network = ipaddress.ip_network(f"{ip_address}/{cidr}", strict=False)
            first_usable = network.network_address
            last_usable = network.network_address + network.num_addresses - 1
            result_text.set(f"Network address: {network.network_address}\n"
                            f"Subnet mask: /{network.prefixlen}\n"
                            f"CIDR notation: /{network.prefixlen}\n"
                            f"Number of addresses: {network.num_addresses}\n"
                            f"Usable addresses: {network.num_addresses}\n"
                            f"IP version: IPv{ip_version}\n"
                            f"First usable address: {first_usable}\n"
                            f"Last usable address: {last_usable}\n"
                            f"Number of subnets: {calculate_subnets(network, int(new_subnet_prefix)) if new_subnet_prefix else 'N/A'}\n"
                            f"Compressed IPv6: {ip_obj.compressed}")
    except ValueError as e:
        messagebox.showerror("Error", f"Invalid network: {e}")



def get_ip_class(ip):
    if isinstance(ip, ipaddress.IPv4Address):
        first_octet = int(ip.exploded.split('.')[0])
        if 1 <= first_octet <= 126:
            return "A"
        elif 128 <= first_octet <= 191:
            return "B"
        elif 192 <= first_octet <= 223:
            return "C"
        elif 224 <= first_octet <= 239:
            return "D (Multicast)"
        elif 240 <= first_octet <= 255:
            return "E (Reserved)"
        else:
            return "Invalid"
    else:
        return "N/A (IPv6)"

def clear_fields():
    ip_address_field.delete(0, tk.END)
    subnet_mask_field.delete(0, tk.END)
    new_subnet_prefix_field.delete(0, tk.END)
    result_text.set("")
    debug_text.config(state=tk.NORMAL)
    debug_text.delete(1.0, tk.END)
    debug_text.config(state=tk.DISABLED)

def copy_results():
    root.clipboard_clear()
    root.clipboard_append(result_text.get())
    messagebox.showinfo("Copied", "Results copied to clipboard")

class TextRedirector(io.StringIO):
    def __init__(self, text_widget):
        self.text_widget = text_widget
        super().__init__()

    def write(self, str):
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.insert(tk.END, str)
        self.text_widget.see(tk.END)
        self.text_widget.config(state=tk.DISABLED)

def redirect_output():
    debug_text.config(state=tk.NORMAL)
    debug_text.delete(1.0, tk.END)
    debug_text.config(state=tk.DISABLED)
    sys.stdout = TextRedirector(debug_text)
    sys.stderr = TextRedirector(debug_text)

# GUI setup
root = tk.Tk()
root.title("NetAddress Analyzer__")

# Create labels and entry fields
tk.Label(root, text="IP Address:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
tk.Label(root, text="Subnet Mask:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
tk.Label(root, text="New Subnet Prefix:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)

ip_address_field = tk.Entry(root)
ip_address_field.grid(row=0, column=1, padx=10, pady=5)
subnet_mask_field = tk.Entry(root)
subnet_mask_field.grid(row=1, column=1, padx=10, pady=5)
new_subnet_prefix_field = tk.Entry(root)
new_subnet_prefix_field.grid(row=2, column=1, padx=10, pady=5)

# Create buttons
calculate_button = tk.Button(root, text="Calculate", command=calculate, bg="light blue")
calculate_button.grid(row=3, column=0, pady=10)
clear_button = tk.Button(root, text="Clear", command=clear_fields, bg="light gray")
clear_button.grid(row=3, column=1, pady=10)
copy_button = tk.Button(root, text="Copy Results", command=copy_results, bg="light green")
copy_button.grid(row=3, column=2, pady=10)

# Create result display
result_text = tk.StringVar()
result_label = tk.Label(root, textvariable=result_text, justify=tk.LEFT)
result_label.grid(row=4, column=0, columnspan=3, sticky=tk.W, padx=10, pady=5)

# Create debug text area
debug_text = tk.Text(root, height=10, width=50)
debug_text.grid(row=5, column=0, columnspan=3, padx=10, pady=5)
debug_text.config(state=tk.DISABLED)

# Configure grid
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)

root.mainloop()
