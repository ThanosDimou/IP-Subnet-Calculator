# NetAddress Analyzer

NetAddress Analyzer is a Python application that assists users in calculating subnets, validating IP addresses, and subnet masks. The application supports both IPv4 and IPv6 addresses and includes functionality for visualizing networks, exporting results to CSV and PDF formats, and switching between English and Greek languages.

## Features

- **IP Address and Subnet Mask Validation:** Validates user input for IP addresses and subnet masks.
- **Subnet Calculation:** Calculates the number of subnets that can be created based on the given IP address and subnet mask.
- **Language Support:** Switch between English and Greek languages.
- **Export Options:** Export calculation results to CSV or PDF files.
- **Network Visualization:** Visualize the network and its subnets in a graphical format.

## Requirements

- Python 3.x
- Tkinter (included with Python)
- Pillow
- Matplotlib
- NetworkX
- ReportLab

You can install the required packages using pip:

```bash
pip install Pillow matplotlib networkx reportlab
```

## Usage

1. **IP Address: Enter a valid IPv4 or IPv6 address.
2. **Subnet Mask: Enter the subnet mask corresponding to the IP address.
3. **New Subnet Prefix: Enter the new prefix length for subnetting.
4. **Calculate: Click this button to compute the number of new subnets that can be created.
5. **Clear**: Click the "Clear" button to reset all input fields and results.
6. **Copy Results**: Click the "Copy Results" button to copy the network information to the clipboard for easy sharing.
7. **Export to CSV: Save the results as a CSV file.
8. **Export to PDF: Save the results as a PDF file.
9. **Visualize: Display a graphical representation of the network.

## Language Support
The application supports English and Greek. You can switch languages using the flags in the upper right corner of the window.


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

##Acknowledgments**
- Python - Programming Language
- Tkinter - GUI toolkit
- Pillow - Image processing library
- Matplotlib - Plotting library
- NetworkX - Network analysis library
- ReportLab - PDF generation library


### Instructions

- Replace `https://github.com/your-username/netaddress-analyzer.git` with the actual URL of your repository.
- Adjust any additional information specific to your project as needed.

Let me know if you need any further adjustments!


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.



