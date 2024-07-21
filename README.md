# NetAddress Analyzer

NetAddress Analyzer is a comprehensive tool designed for network administrators and IT professionals to efficiently analyze and calculate network addresses. The application supports both IPv4 and IPv6 addresses, allowing users to input IP addresses, subnet masks, and new subnet prefixes to retrieve detailed network information.

## Features

- **IPv4 and IPv6 Support**: Analyze and calculate network addresses for both IPv4 and IPv6.
- **Subnet Mask Conversion**: Automatically convert subnet mask values to CIDR notation and vice versa.
- **Network Information**: Retrieve key network information such as network address, broadcast address, subnet mask, wildcard mask, CIDR notation, number of addresses, and usable addresses.
- **Subnet Calculation**: Calculate the number of subnets based on a new subnet prefix.
- **IP Address Validation**: Validate IP addresses and subnet masks to ensure accurate calculations.
- **Debug Output**: View detailed debug output to understand the calculation process.

## Usage

1. **Enter IP Address**: Input the desired IPv4 or IPv6 address.
2. **Enter Subnet Mask**: Input the subnet mask in either dotted-decimal (IPv4) or CIDR notation. The application will convert it as needed.
3. **Enter New Subnet Prefix**: Optionally, enter a new subnet prefix to calculate the number of subnets.
4. **Calculate**: Click the "Calculate" button to retrieve and display the network information.
5. **Clear**: Click the "Clear" button to reset all input fields and results.
6. **Copy Results**: Click the "Copy Results" button to copy the network information to the clipboard for easy sharing.

## Example

### IPv4
- **IP Address**: 192.168.1.1
- **Subnet Mask**: 255.255.255.0
- **New Subnet Prefix**: 26

**Results:**
- Network address: 192.168.1.0
- Broadcast address: 192.168.1.255
- Subnet mask: 255.255.255.0
- Wildcard mask: 0.0.0.255
- CIDR notation: /24
- Number of addresses: 256
- Usable addresses: 254
- IP version: IPv4
- First usable address: 192.168.1.1
- Last usable address: 192.168.1.254
- Number of subnets: 4

### IPv6
- **IP Address**: 2001:0db8:85a3::8a2e:0370:7334
- **Subnet Mask**: 48
- **New Subnet Prefix**: 64

**Results:**
- Network address: 2001:db8:85a3::
- Subnet mask: /48
- CIDR notation: /48
- Number of addresses: 1.20892582e+24
- Usable addresses: 1.20892582e+24
- IP version: IPv6
- First usable address: 2001:db8:85a3::
- Last usable address: 2001:db8:85a3:ffff:ffff:ffff:ffff
- Number of subnets: 65536
- Compressed IPv6: 2001:db8:85a3::8a2e:370:7334

## Installation

To run the NetAddress Analyzer, you need Python and Tkinter installed. Follow these steps:

1. Clone the repository:
    ```
    git clone https://github.com/yourusername/NetAddress-Analyzer.git
    ```
2. Navigate to the project directory:
    ```
    cd NetAddress-Analyzer
    ```
3. Run the application:
    ```
    python netaddress_analyzer.py
    ```

## Contributing

We welcome contributions! Please fork the repository and create a pull request with your changes. Ensure your code follows the existing style and includes appropriate tests.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

