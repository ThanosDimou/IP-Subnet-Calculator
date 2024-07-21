import tkinter as tk
from tkinter import messagebox

# Function to check if IP address is valid
def is_valid_ip(ip):
    octets = ip.split('.')
    if len(octets) != 4:
        return False
    for octet in octets:
        if not octet.isdigit():
            return False
        if int(octet) < 0 or int(octet) > 255:
            return False
    return True

# Function to convert IP address and subnet mask to binary
def convert_ip_to_binary(ip):
    return ''.join(bin(int(octet))[2:].zfill(8) for octet in ip.split('.'))

# Function to count '0' bits in a binary string
def count_0_bits(binary_string):
    return binary_string.count('0')

# Function to AND two binary strings
def and_binary_strings(binary_string1, binary_string2):
    return ''.join('1' if b1 == '1' and b2 == '1' else '0' for b1, b2 in zip(binary_string1, binary_string2))

# Function to add binary strings with carry
def add_binary_strings(binary_string1, binary_string2):
    result = bin(int(binary_string1, 2) + int(binary_string2, 2))[2:].zfill(32)
    return result

# Function to convert binary to decimal
def binary_to_decimal(binary_string):
    return '.'.join(str(int(binary_string[i:i+8], 2)) for i in range(0, len(binary_string), 8))

# Function to calculate network details
def calculate():
    ip_address = ip_address_field.get()
    subnet_mask = subnet_mask_field.get()

    if not is_valid_ip(ip_address):
        messagebox.showerror("Error", "Invalid IP address")
        return

    if not is_valid_ip(subnet_mask):
        messagebox.showerror("Error", "Invalid subnet mask")
        return

    ip_binary = convert_ip_to_binary(ip_address)
    subnet_binary = convert_ip_to_binary(subnet_mask)

    usable_hosts = 2 ** count_0_bits(subnet_binary) - 2

    network_address = and_binary_strings(ip_binary, subnet_binary)
    network_address_decimal = binary_to_decimal(network_address)

    result_text.set(f"Network address: {network_address_decimal}\n"
                    f"Usable hosts: {usable_hosts}\n")

    hosts_list = []
    for i in range(1, usable_hosts + 2):
        binary_usable_host = bin(i)[2:].zfill(32)
        usable_host_address = add_binary_strings(network_address, binary_usable_host)
        usable_host_address_decimal = binary_to_decimal(usable_host_address)
        hosts_list.append(usable_host_address_decimal)

    result_text.set(result_text.get() + f"Broadcast address: {hosts_list[-1]}\n"
                                        f"Range of usable hosts: {hosts_list[0]} - {hosts_list[-2]}")

# GUI setup
root = tk.Tk()
root.title("Network Address Calculator")

# Create labels and entry fields
tk.Label(root, text="IP Address:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
tk.Label(root, text="Subnet Mask:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)

ip_address_field = tk.Entry(root)
ip_address_field.grid(row=0, column=1, padx=10, pady=5)

subnet_mask_field = tk.Entry(root)
subnet_mask_field.grid(row=1, column=1, padx=10, pady=5)

# Create calculate button
calculate_button = tk.Button(root, text="Calculate", command=calculate, bg="light blue")
calculate_button.grid(row=2, column=0, columnspan=2, pady=10)

# Create result display
result_text = tk.StringVar()
result_label = tk.Label(root, textvariable=result_text, justify=tk.LEFT)
result_label.grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=10, pady=5)

# Configure grid
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

root.mainloop()
  



        




