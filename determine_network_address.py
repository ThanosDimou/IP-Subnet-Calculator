from tkinter import *

# function to check if IP address is valid
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


# function to convert IP address and subnet mask in binary
def convert_ip_to_binary(ip):
    octets = ip.split('.')
    binary_ip = ''
    for octet in octets:
        binary_ip += bin(int(octet))[2:].zfill(8)
    return binary_ip

#function to count 0 bits in binary string
def count_0_bits(binary_string):
    count = 0
    for i in range(len(binary_string)):
        if binary_string[i] == '0':
            count += 1
    return count


#function to AND two binary strings
def and_binary_strings(binary_string1, binary_string2):
    binary_string = ''
    for i in range(len(binary_string1)):
        if binary_string1[i] == '1' and binary_string2[i] == '1':
            binary_string += '1'
        else:
            binary_string += '0'
    return binary_string

#function to ADD of two binary strings and fill 0s to right
def add_binary_strings(binary_string1, binary_string2):
    binary_string = ''
    carry = 0
    for i in range(len(binary_string1)):
        if binary_string1[i] == '1' and binary_string2[i] == '1':
            if carry == 1:
                binary_string += '1'
                carry = 1
            else:
                binary_string += '0'
                carry = 1
        elif binary_string1[i] == '0' and binary_string2[i] == '0':
            if carry == 1:
                binary_string += '1'
                carry = 0
            else:
                binary_string += '0'
                carry = 0
        else:
            if carry == 1:
                binary_string += '0'
                carry = 1
            else:
                binary_string += '1'
                carry = 0
    if carry == 1:
        binary_string += '1'
    return binary_string


#function from binary to decimal
def binary_to_decimal(binary_string):
    # split the binary string into 8-bit chunks
    octets = [binary_string[i:i+8] for i in range(0, len(binary_string), 8)]
    # convert each 8-bit chunk to decimal
    decimals = [int(octet, 2) for octet in octets]
    # join the decimal octets into a single string
    return '.'.join(str(decimal) for decimal in decimals)

#function to calculate
def Calculate():
    ip_address = ip_address_field.get()
    subnet_mask = subnet_mask_field.get()
    #check if IP address is valid
    while True:
        
        if is_valid_ip(ip_address):
            ipLabel = Label(root, text="Valid IP address")
            ipLabel.grid(row=0, column=2)
            break
        else:
            if ip_address == '':
                ipLabel = Label(root, text="Insert IP address")
                ipLabel.grid(row=0, column=2)
                ip_address_field.delete(0, END)
                return
            else:
                ipLabel = Label(root, text="Invalid IP address")
                ipLabel.grid(row=0, column=2)
                ip_address_field.delete(0, END)
                return
            
    while True:
        
        if is_valid_ip(subnet_mask):
            subnetLabel = Label(root, text="Valid subnet mask")
            subnetLabel.grid(row=1, column=2)
            break
        else:
            if subnet_mask == '':
                subnetLabel = Label(root, text="Insert subnet mask")
                subnetLabel.grid(row=1, column=2)
                subnet_mask_field.delete(0, END)
                return
            else:            
                subLabel = Label(root, text="Invalid subnet mask")
                subLabel.grid(row=1, column=2)
                subnet_mask_field.delete(0, END)
                return
            
    #convert IP address and subnet mask to binary
    ip_address = convert_ip_to_binary(ip_address)
    subnet_mask = convert_ip_to_binary(subnet_mask)
    usable_hosts = 2 **(count_0_bits(subnet_mask)) - 2

    #AND IP address and subnet mask
    network_address = and_binary_strings(ip_address, subnet_mask)

    #convert network address to decimal
    network_address_decimal = binary_to_decimal(network_address)
    
    #show network address
    myLabel=Label(root, text="Network address: " + network_address_decimal)
    myLabel.grid(row=4,column=0,columnspan=2,sticky=W)
    
    #show usable hosts
    myLabel=Label(root, text="Usable hosts: " + str(usable_hosts))
    myLabel.grid(row=6,column=0,columnspan=2,sticky=W)

    hosts_list = []
    for i in range(1,usable_hosts+2):
        #covert decimal to binary and add 0s to the left until 32 bits
        binary_usable_hosts = bin(i)[2:].zfill(32)
        #AND network address and binary usable hosts
        usable_hosts_address = add_binary_strings(network_address, binary_usable_hosts)
        #convert usable hosts address to decimal
        usable_hosts_address_decimal = binary_to_decimal(usable_hosts_address)
        #insert usable hosts address decimal to a list
        hosts_list.append(usable_hosts_address_decimal)
        
    #show broadcast address
    myLabel=Label(root, text="Broadcast address: " + hosts_list[-1])
    myLabel.grid(row=5,column=0,columnspan=2,sticky=W)

    #show range of usable hosts
    myLabel=Label(root, text="Range of usable hosts: " + str(hosts_list[0]) + " - " + str(hosts_list[-2]))
    myLabel.grid(row=7,column=0,columnspan=2,sticky=W)


#############################################################################################################################

root = Tk()
root.title("Determine network address")

#create labels
myLabel=Label(root, text="IP address")
myLabel.grid(row=0,column=0, sticky=W)
myLabel=Label(root, text="Subnet mask")
myLabel.grid(row=1,column=0, sticky=W)

#create button
myButton=Button(root, text="Calculate", command=Calculate)
myButton.grid(row=3, column=1)
#button background color
myButton.config(background="light blue")


#create entry fields to insert IP address and subnet mask
ip_address_field = Entry(root)
ip_address_field.grid(row=0, column=1)

subnet_mask_field = Entry(root)
subnet_mask_field.grid(row=1, column=1)

root.grid_columnconfigure(4, minsize=100)

root.mainloop()  
  



        




