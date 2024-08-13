# Basic libraries
import sys
import csv
import io
import json
from pathlib import Path
from typing import Optional, Union, Dict, Any

# Gui libraries
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from PIL import Image, ImageTk

# Network Libraries
import ipaddress

# Libraries for export and visualization
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx

# Logging
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IPCalculator:
    def __init__(self, root):
        self.root = root
        self.current_language = "en"
        self.texts: Dict[str, Dict[str, str]] = {}
        self.network: Optional[Union[ipaddress.IPv4Network, ipaddress.IPv6Network]] = None
        self.new_subnet_prefix: Optional[int] = None
        
        self.setup_gui()
        self.load_languages()

    def setup_gui(self):
        self.root.title("IP Calculator")

        # Create and place widgets
        self.create_input_fields()
        self.create_buttons()
        self.create_result_display()
        self.create_debug_area()

        # Arrangement of the grid
        self.root.grid_columnconfigure((0, 1, 2), weight=1)

    def create_input_fields(self):
        self.ip_label = tk.Label(self.root, text="IP Address:")
        self.ip_label.grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        
        self.mask_label = tk.Label(self.root, text="Subnet Mask:")
        self.mask_label.grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        
        self.new_subnet_label = tk.Label(self.root, text="New Subnet Prefix:")
        self.new_subnet_label.grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)

        self.ip_address_field = tk.Entry(self.root)
        self.ip_address_field.grid(row=0, column=1, padx=10, pady=5)
        
        self.subnet_mask_field = tk.Entry(self.root)
        self.subnet_mask_field.grid(row=1, column=1, padx=10, pady=5)
        
        self.new_subnet_prefix_field = tk.Entry(self.root)
        self.new_subnet_prefix_field.grid(row=2, column=1, padx=10, pady=5)

    def create_buttons(self):
        self.calculate_button = tk.Button(self.root, text="Calculate", command=self.calculate, bg="light blue")
        self.calculate_button.grid(row=3, column=0, pady=10)
        
        self.clear_button = tk.Button(self.root, text="Clear", command=self.clear_fields, bg="light gray")
        self.clear_button.grid(row=3, column=1, pady=10)
        
        self.copy_button = tk.Button(self.root, text="Copy Results", command=self.copy_results, bg="light green")
        self.copy_button.grid(row=3, column=2, pady=10)
        
        self.export_csv_button = tk.Button(self.root, text="Export to CSV", command=self.export_to_csv, bg="light yellow")
        self.export_csv_button.grid(row=3, column=3, pady=10)
        
        self.export_pdf_button = tk.Button(self.root, text="Export to PDF", command=self.export_to_pdf, bg="light pink")
        self.export_pdf_button.grid(row=3, column=4, pady=10)
        
        self.visualize_button = tk.Button(self.root, text="Visualize", command=self.visualize_network, bg="lavender")
        self.visualize_button.grid(row=0, column=2, padx=10, pady=10, sticky=tk.NE)

        # Language buttons
        flag_frame = tk.Frame(self.root)
        flag_frame.grid(row=0, column=4, padx=10, pady=5, sticky=tk.NE)

        self.us_flag = self.load_flag_image("images/us.png")
        self.gr_flag = self.load_flag_image("images/gr.png")

        us_flag_button = tk.Button(flag_frame, image=self.us_flag, command=lambda: self.change_language("en"))
        us_flag_button.pack(side=tk.LEFT, padx=2)
        
        gr_flag_button = tk.Button(flag_frame, image=self.gr_flag, command=lambda: self.change_language("el"))
        gr_flag_button.pack(side=tk.LEFT, padx=2)

    def create_result_display(self):
        self.result_text = tk.StringVar()
        self.result_label = tk.Label(self.root, textvariable=self.result_text, justify=tk.LEFT)
        self.result_label.grid(row=4, column=0, columnspan=3, sticky=tk.W, padx=10, pady=5)

    def create_debug_area(self):
        self.debug_text = tk.Text(self.root, height=10, width=50)
        self.debug_text.grid(row=5, column=0, columnspan=3, padx=10, pady=5)
        self.debug_text.config(state=tk.DISABLED)

    def load_languages(self):
        for lang in ["en", "el"]:
            self.texts[lang] = self.load_language(lang)
        self.update_language_texts()

    def load_language(self, lang: str) -> Dict[str, str]:
        try:
            lang_file = Path("locales") / f"{lang}.json"
            return json.loads(lang_file.read_text(encoding="utf-8"))
        except FileNotFoundError:
            logger.error(f"Language file {lang}.json not found")
            return {}

    def change_language(self, lang: str):
        self.current_language = lang
        self.update_language_texts()

    def update_language_texts(self):
        texts = self.texts[self.current_language]
        self.root.title(texts["title"])
        self.ip_label.config(text=texts["ip_address"])
        self.mask_label.config(text=texts["subnet_mask"])
        self.new_subnet_label.config(text=texts["new_subnet_prefix"])
        self.calculate_button.config(text=texts["calculate"])
        self.clear_button.config(text=texts["clear"])
        self.copy_button.config(text=texts["copy_results"])
        self.export_csv_button.config(text=texts["export_to_csv"])
        self.export_pdf_button.config(text=texts["export_to_pdf"])
        self.visualize_button.config(text=texts["visualize"])

    def load_flag_image(self, path: str, size: tuple = (24, 24)) -> Optional[ImageTk.PhotoImage]:
        try:
            image = Image.open(path)
            image = image.resize(size, Image.LANCZOS)
            return ImageTk.PhotoImage(image)
        except FileNotFoundError:
            logger.warning(f"Image file not found: {path}")
            return None

    def is_valid_ip(self, ip: str) -> Optional[Union[ipaddress.IPv4Address, ipaddress.IPv6Address]]:
        try:
            ip_obj = ipaddress.ip_address(ip)
            logger.info(f"Valid IP address: {ip} (IPv{ip_obj.version})")
            return ip_obj
        except ValueError as e:
            logger.error(f"Invalid IP address: {ip}. Error: {e}")
            return None

    def is_valid_subnet_mask(self, mask: str, ip_version: int) -> bool:
        try:
            if ip_version == 4:
                network = ipaddress.IPv4Network(f"0.0.0.0/{mask}", strict=False)
            else:  # IPv6
                network = ipaddress.IPv6Network(f"::{mask}", strict=False)
            
            logger.info(f"Mask: {mask}, Prefix length: {network.prefixlen}")
            return True
        except ValueError as e:
            logger.error(f"ValueError in is_valid_subnet_mask: {e}")
            return False

    def calculate_subnets(self, network: Union[ipaddress.IPv4Network, ipaddress.IPv6Network], new_prefix: int) -> int:
        try:
            current_prefix = network.prefixlen
            if new_prefix <= current_prefix:
                return 0
            return 2 ** (new_prefix - current_prefix)
        except ValueError as e:
            logger.error(f"Error calculating subnets: {e}")
            return 0

    def cidr_to_subnet_mask(self, cidr: int, ip_version: int) -> str:
        if ip_version == 4:
            return str(ipaddress.IPv4Network(f"0.0.0.0/{cidr}").netmask)
        else:  # IPv6
            return f"/{cidr}"

    def get_ip_class(self, ip: Union[ipaddress.IPv4Address, ipaddress.IPv6Address]) -> str:
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

    def calculate(self):
        try:
            self.redirect_output()
            ip_address = self.ip_address_field.get()
            subnet_mask = self.subnet_mask_field.get()
            new_subnet_prefix = self.new_subnet_prefix_field.get()

            ip_obj = self.is_valid_ip(ip_address)
            if not ip_obj:
                messagebox.showerror("Error", "Invalid IP address")
                return

            ip_version = ip_obj.version
            max_prefix = 32 if ip_version == 4 else 128

            if new_subnet_prefix:
                try:
                    new_subnet_prefix = int(new_subnet_prefix)
                    if new_subnet_prefix > max_prefix:
                        messagebox.showerror("Error", f"New subnet prefix must be less than or equal to {max_prefix} for IPv{ip_version}")
                        return
                except ValueError:
                    messagebox.showerror("Error", "New subnet prefix must be an integer")
                    return

            if not subnet_mask.startswith('/'):
                try:
                    if '.' in subnet_mask or ':' in subnet_mask:
                        subnet_mask = '/' + str(ipaddress.ip_network(f"0.0.0.0/{subnet_mask}", strict=False).prefixlen)
                    else:
                        subnet_mask = '/' + subnet_mask
                except ValueError:
                    messagebox.showerror("Error", "Invalid subnet mask")
                    return

            try:
                cidr = int(subnet_mask[1:])
                max_cidr = 32 if ip_version == 4 else 128
                if 0 <= cidr <= max_cidr:
                    subnet_mask = self.cidr_to_subnet_mask(cidr, ip_version)
                else:
                    messagebox.showerror("Error", f"Invalid CIDR notation for IPv{ip_version}")
                    return
            except ValueError:
                messagebox.showerror("Error", "Invalid subnet mask")
                return

            if not self.is_valid_subnet_mask(subnet_mask, ip_version):
                messagebox.showerror("Error", "Invalid subnet mask")
                return

            ip_class = self.get_ip_class(ip_obj)

            if ip_version == 4:
                self.network = ipaddress.ip_network(f"{ip_address}/{cidr}", strict=False)
                self.result_text.set(self.format_ipv4_result(self.network, ip_class, new_subnet_prefix))
            else:  # IPv6
                self.network = ipaddress.ip_network(f"{ip_address}/{cidr}", strict=False)
                self.result_text.set(self.format_ipv6_result(self.network, ip_class, new_subnet_prefix))

            if new_subnet_prefix:
                self.new_subnet_prefix = int(new_subnet_prefix)

        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Unexpected Error", f"An unexpected error occurred: {e}")

    def format_ipv4_result(self, network: ipaddress.IPv4Network, ip_class: str, new_subnet_prefix: str) -> str:
        return (f"Network address: {network.network_address}\n"
                f"Broadcast address: {network.broadcast_address}\n"
                f"Subnet mask: {network.netmask}\n"
                f"Wildcard mask: {network.hostmask}\n"
                f"CIDR notation: /{network.prefixlen}\n"
                f"Number of addresses: {network.num_addresses}\n"
                f"Usable addresses: {network.num_addresses - 2}\n"
                f"IP version: IPv4\n"
                f"IP Class: {ip_class}\n"
                f"First usable address: {network.network_address + 1}\n"
                f"Last usable address: {network.broadcast_address - 1}\n"
                f"Number of subnets: {self.calculate_subnets(network, int(new_subnet_prefix)) if new_subnet_prefix else 'N/A'}")

    def format_ipv6_result(self, network: ipaddress.IPv6Network, ip_class: str, new_subnet_prefix: str) -> str:
        if new_subnet_prefix:
            subnets = list(network.subnets(new_prefix=int(new_subnet_prefix)))
            new_network = subnets[0]
            first_usable = new_network.network_address + 1
            last_usable = new_network.network_address + new_network.num_addresses - 1
            num_addresses = new_network.num_addresses
        else:
            first_usable = network.network_address + 1
            last_usable = network.network_address + network.num_addresses - 1
            num_addresses = network.num_addresses

        return (f"Network address: {network.network_address}\n"
                f"Subnet mask: /{network.prefixlen}\n"
                f"CIDR notation: /{network.prefixlen}\n"
                f"Number of addresses: {num_addresses}\n"
                f"Usable addresses: {num_addresses -1}\n"
                f"IP version: IPv6\n"
                f"IP Class: {ip_class}\n"
                f"First usable address: {first_usable}\n"
                f"Last usable address: {last_usable}\n"
                f"Number of subnets: {self.calculate_subnets(network, int(new_subnet_prefix)) if new_subnet_prefix else 'N/A'}\n"
                f"Compressed IPv6: {network.network_address.compressed}")


    def clear_fields(self):
        self.ip_address_field.delete(0, tk.END)
        self.subnet_mask_field.delete(0, tk.END)
        self.new_subnet_prefix_field.delete(0, tk.END)
        self.result_text.set("")
        self.debug_text.config(state=tk.NORMAL)
        self.debug_text.delete(1.0, tk.END)
        self.debug_text.config(state=tk.DISABLED)

    def copy_results(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.result_text.get())
        messagebox.showinfo("Copied", "Results copied to clipboard")

    def export_to_csv(self):
        results = self.result_text.get().strip().split('\n')
        
        if not results or all(result == "" for result in results):
            messagebox.showwarning("No Results", "There are no results to export.")
            return
        
        file_path = filedialog.asksaveasfilename(defaultextension='.csv',
                                                 filetypes=[("CSV files", "*.csv")])
        
        if file_path:
            try:
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    csv_writer = csv.writer(csvfile)
                    csv_writer.writerow(['Parameter', 'Value'])  # Write the header
                    
                    for result in results:
                        if ':' in result:
                            parameter, value = result.split(':', 1)
                            csv_writer.writerow([parameter.strip(), value.strip()])
                    
                messagebox.showinfo("Export Successful", f"Results exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export results: {e}")

    def export_to_pdf(self):
        ip_address = self.ip_address_field.get().strip()
        results = self.result_text.get().strip().split('\n')
        
        if not results or all(result == "" for result in results):
            messagebox.showwarning("No Results", "There are no results to export.")
            return
        
        file_path = filedialog.asksaveasfilename(defaultextension='.pdf',
                                                 filetypes=[("PDF files", "*.pdf")])
        
        if file_path:
            try:
                doc = SimpleDocTemplate(file_path, pagesize=letter)
                styles = getSampleStyleSheet()
                elements = []
                
                title_text = f"IP Calculation Results for {ip_address} with subnet mask {self.subnet_mask_field.get()} and new subnet prefix {self.new_subnet_prefix_field.get()}"
                title = Paragraph(title_text, styles['Title'])
                elements.append(title)
                elements.append(Spacer(1, 12))
                
                data = []
                for result in results:
                    if ':' in result:
                        parameter, value = result.split(':', 1)
                        data.append([parameter.strip(), value.strip()])
                
                table = Table(data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                
                elements.append(table)
                doc.build(elements)
                messagebox.showinfo("Export Successful", f"Results exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export results: {e}")

    def visualize_network(self):
        if not self.network:
            messagebox.showwarning("No Network", "Please calculate a network first.")
            return

        G = nx.Graph()

        subnets = list(self.network.subnets(new_prefix=self.new_subnet_prefix)) if self.new_subnet_prefix else [self.network]
        for subnet in subnets:
            G.add_node(str(subnet.network_address), label=f"{subnet.network_address}/{subnet.prefixlen}")

        for i in range(len(subnets) - 1):
            G.add_edge(str(subnets[i].network_address), str(subnets[i + 1].network_address))

        plt.figure(figsize=(10, 6))
        pos = nx.spring_layout(G)
        labels = nx.get_node_attributes(G, 'label')
        nx.draw(G, pos, with_labels=True, labels=labels, node_size=3000, node_color="lightblue", font_size=10, font_weight="bold", font_color="black")
        plt.title("Network Visualization")
        plt.show()

    def redirect_output(self):
        self.debug_text.config(state=tk.NORMAL)
        self.debug_text.delete(1.0, tk.END)
        self.debug_text.config(state=tk.DISABLED)
        sys.stdout = TextRedirector(self.debug_text)
        sys.stderr = TextRedirector(self.debug_text)

class TextRedirector(io.StringIO):
    def __init__(self, text_widget):
        self.text_widget = text_widget
        super().__init__()

    def write(self, string):
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)
        self.text_widget.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = IPCalculator(root)
    root.mainloop()