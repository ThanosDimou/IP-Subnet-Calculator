# ==============================================================================
# IP Subnet Calculator
#
# A desktop application using Tkinter to calculate and analyze IPv4/IPv6
# network properties and perform subnetting.
#
# Author: Dimou Athanasios
# Email: dimou.athanasios@gmail.com
# Version: 2.0
# Last Modified: 2025-05-31
# ==============================================================================

# --- Basic Libraries ---
import sys
import csv
import io
import json
import logging
from pathlib import Path
from typing import Optional, Union, Dict, Any

# --- GUI Libraries ---
import tkinter as tk
from tkinter import messagebox, ttk, filedialog

# --- Third-Party Libraries ---
from PIL import Image, ImageTk
import ipaddress
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx

# --- Logging Configuration ---
# Sets up basic logging to capture info, warnings, and errors.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# ==============================================================================
# Main Application Class
# ==============================================================================
class IPCalculator:
    """
    The main class for the IP Calculator application.
    It handles the GUI setup, user interactions, and orchestrates the
    backend logic for calculations and exports.
    """
    def __init__(self, root: tk.Tk):
        """
        Initializes the main application window and its components.
        
        Args:
            root (tk.Tk): The main Tkinter window object.
        """
        self.root = root
        self.texts: Dict[str, Dict[str, str]] = {}
        self.current_language = "en"
        
        # --- State Variables ---
        # These store the results of the last calculation.
        self.network: Optional[Union[ipaddress.IPv4Network, ipaddress.IPv6Network]] = None
        self.new_subnet_prefix: Optional[int] = None

        # --- Theming and Styling ---
        # Centralized styling for a consistent look and feel.
        self.style = ttk.Style()
        self.style.theme_use('clam') # Modern theme
        self.style.configure('TButton', padding=5, font=('Helvetica', 10))
        self.style.configure('TLabel', font=('Helvetica', 10))
        self.style.configure('TEntry', font=('Helvetica', 10))
        self.style.configure('Header.TLabel', font=('Helvetica', 12, 'bold'))

        # Load assets and set up the GUI
        self.load_languages()
        self._load_flag_images()
        self._setup_gui()
        self.change_language(self.current_language)

    # --- GUI Setup Methods ---

    def _setup_gui(self):
        """Sets up the entire graphical user interface."""
        self.root.title("IP Calculator")
        self.root.geometry("800x650") # Give it a default size
        self.root.minsize(750, 600)   # Set a minimum size

        # --- Main Layout ---
        # Configure the main grid to be responsive.
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(2, weight=1) # Allow the results area to expand

        # Create frames for logical grouping of widgets.
        self._create_header_frame()
        self._create_input_frame()
        self._create_results_frame()
        self._create_log_frame()
        self._create_action_buttons_frame()

    def _create_header_frame(self):
        """Creates the top frame with the title and language buttons."""
        header_frame = ttk.Frame(self.root, padding=10)
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)

        self.title_label = ttk.Label(header_frame, text="IP Subnet Calculator", style='Header.TLabel')
        self.title_label.grid(row=0, column=0, sticky="w")
        
        # Language buttons frame
        flag_frame = ttk.Frame(header_frame)
        flag_frame.grid(row=0, column=1, sticky="e")
        
        us_flag_button = ttk.Button(flag_frame, image=self.us_flag_img, command=lambda: self.change_language("en"))
        us_flag_button.pack(side=tk.LEFT, padx=2)
        
        gr_flag_button = ttk.Button(flag_frame, image=self.gr_flag_img, command=lambda: self.change_language("el"))
        gr_flag_button.pack(side=tk.LEFT, padx=2)

    def _create_input_frame(self):
        """Creates the frame for user input fields."""
        input_frame = ttk.LabelFrame(self.root, text="Input", padding=15)
        input_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        input_frame.grid_columnconfigure(1, weight=1)
        
        self.ip_label = ttk.Label(input_frame, text="IP Address:")
        self.ip_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        self.ip_address_field = ttk.Entry(input_frame, width=40)
        self.ip_address_field.grid(row=0, column=1, sticky="ew", padx=10, pady=5)
        
        self.mask_label = ttk.Label(input_frame, text="Subnet Mask / CIDR:")
        self.mask_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        self.subnet_mask_field = ttk.Entry(input_frame)
        self.subnet_mask_field.grid(row=1, column=1, sticky="ew", padx=10, pady=5)
        
        self.new_subnet_label = ttk.Label(input_frame, text="New Subnet Prefix (for subnetting):")
        self.new_subnet_label.grid(row=2, column=0, sticky=tk.W, pady=5)
        self.new_subnet_prefix_field = ttk.Entry(input_frame)
        self.new_subnet_prefix_field.grid(row=2, column=1, sticky="ew", padx=10, pady=5)
    
    def _create_results_frame(self):
        """Creates the frame to display calculation results."""
        results_frame = ttk.LabelFrame(self.root, text="Results", padding=15)
        results_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        results_frame.grid_columnconfigure(0, weight=1)
        results_frame.grid_rowconfigure(0, weight=1)

        self.result_text = tk.Text(results_frame, height=15, wrap="word", font=("Courier New", 10), state=tk.DISABLED)
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        self.result_text['yscrollcommand'] = scrollbar.set
        
        self.result_text.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

    def _create_log_frame(self):
        """Creates the frame for the debug/log output area."""
        log_frame = ttk.LabelFrame(self.root, text="Log", padding=10)
        log_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=5)
        log_frame.grid_columnconfigure(0, weight=1)
        
        self.debug_text = tk.Text(log_frame, height=5, wrap="word", font=("Courier New", 9), state=tk.DISABLED, bg="#f0f0f0")
        self.debug_text.grid(row=0, column=0, sticky="ew")
        
        # Redirect stdout/stderr to the debug text widget
        sys.stdout = TextRedirector(self.debug_text)
        sys.stderr = TextRedirector(self.debug_text)

    def _create_action_buttons_frame(self):
        """Creates the bottom frame for all action buttons."""
        btn_frame = ttk.Frame(self.root, padding=10)
        btn_frame.grid(row=4, column=0, sticky="ew", padx=10, pady=10)
        
        # --- Main Actions ---
        self.calculate_button = ttk.Button(btn_frame, text="Calculate", command=self.calculate)
        self.calculate_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = ttk.Button(btn_frame, text="Clear", command=self.clear_fields)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        self.visualize_button = ttk.Button(btn_frame, text="Visualize", command=self.visualize_network)
        self.visualize_button.pack(side=tk.LEFT, padx=5)
        
        # --- Export Actions (on the right) ---
        self.export_pdf_button = ttk.Button(btn_frame, text="Export to PDF", command=self.export_to_pdf)
        self.export_pdf_button.pack(side=tk.RIGHT, padx=5)
        
        self.export_csv_button = ttk.Button(btn_frame, text="Export to CSV", command=self.export_to_csv)
        self.export_csv_button.pack(side=tk.RIGHT, padx=5)
        
        self.copy_button = ttk.Button(btn_frame, text="Copy Results", command=self.copy_results)
        self.copy_button.pack(side=tk.RIGHT, padx=5)

    # --- Language and Asset Loading ---

    def load_languages(self):
        """Loads language strings from JSON files."""
        for lang_code in ["en", "el"]:
            try:
                lang_file = Path("locales") / f"{lang_code}.json"
                self.texts[lang_code] = json.loads(lang_file.read_text(encoding="utf-8"))
            except FileNotFoundError:
                logger.error(f"Language file for '{lang_code}' not found at {lang_file}")
                # Provide a fallback
                if lang_code == "en":
                    messagebox.showerror("Fatal Error", f"English language file not found. Application cannot continue.")
                    self.root.destroy()

    def _load_flag_images(self, size: tuple = (24, 24)):
        """Loads and resizes flag icons."""
        try:
            us_img = Image.open("images/us.png").resize(size, Image.LANCZOS)
            self.us_flag_img = ImageTk.PhotoImage(us_img)
            
            gr_img = Image.open("images/gr.png").resize(size, Image.LANCZOS)
            self.gr_flag_img = ImageTk.PhotoImage(gr_img)
        except FileNotFoundError as e:
            logger.warning(f"Could not load image file: {e}. Language switching will be text-only.")
            self.us_flag_img = None
            self.gr_flag_img = None

    def change_language(self, lang_code: str):
        """
        Updates the GUI text to the selected language.
        
        Args:
            lang_code (str): The language code to switch to (e.g., 'en', 'el').
        """
        self.current_language = lang_code
        texts = self.texts.get(lang_code, self.texts["en"]) # Fallback to English

        # Update all widgets with translated text
        self.root.title(texts.get("title", "IP Calculator"))
        self.title_label.config(text=texts.get("main_title", "IP Subnet Calculator"))
        self.ip_label.config(text=texts.get("ip_address", "IP Address:"))
        self.mask_label.config(text=texts.get("subnet_mask", "Subnet Mask / CIDR:"))
        self.new_subnet_label.config(text=texts.get("new_subnet_prefix", "New Subnet Prefix:"))
        self.calculate_button.config(text=texts.get("calculate", "Calculate"))
        self.clear_button.config(text=texts.get("clear", "Clear"))
        self.visualize_button.config(text=texts.get("visualize", "Visualize"))
        self.copy_button.config(text=texts.get("copy_results", "Copy Results"))
        self.export_csv_button.config(text=texts.get("export_to_csv", "Export to CSV"))
        self.export_pdf_button.config(text=texts.get("export_to_pdf", "Export to PDF"))

    # --- Core Logic and Actions ---

    def calculate(self):
        """
        Main calculation logic. It validates input, performs calculations,
        and displays the results.
        """
        try:
            # 1. Get and Validate Inputs
            ip_str = self.ip_address_field.get().strip()
            mask_str = self.subnet_mask_field.get().strip()
            new_prefix_str = self.new_subnet_prefix_field.get().strip()
            
            if not ip_str or not mask_str:
                messagebox.showerror("Input Error", "IP Address and Subnet Mask are required.")
                return

            ip_obj = ipaddress.ip_address(ip_str)
            ip_version = ip_obj.version
            max_prefix = 32 if ip_version == 4 else 128
            
            # 2. Process Subnet Mask (handle both dotted-decimal and CIDR)
            if '/' in mask_str:
                cidr = int(mask_str.split('/')[1])
            else:
                # Assuming it's a dotted-decimal mask or just a number for CIDR
                net_for_prefix = ipaddress.ip_network(f"{ip_str}/{mask_str}", strict=False)
                cidr = net_for_prefix.prefixlen

            if not (0 <= cidr <= max_prefix):
                raise ValueError(f"Invalid CIDR/{mask_str} for IPv{ip_version}.")

            # 3. Process New Subnet Prefix (if provided)
            self.new_subnet_prefix = None
            if new_prefix_str:
                self.new_subnet_prefix = int(new_prefix_str)
                if not (cidr < self.new_subnet_prefix <= max_prefix):
                    raise ValueError(f"New prefix must be > {cidr} and <= {max_prefix}.")

            # 4. Perform Calculation and store the network object
            self.network = ipaddress.ip_network(f"{ip_str}/{cidr}", strict=False)

            # 5. Format and Display Results
            result_data = self._get_network_details(self.network, self.new_subnet_prefix)
            self._display_results(result_data)

        except ValueError as e:
            messagebox.showerror("Input Validation Error", f"Invalid input: {e}")
            logger.error(f"Calculation failed: {e}")
        except Exception as e:
            messagebox.showerror("Unexpected Error", f"An unexpected error occurred: {e}")
            logger.exception("An unexpected error occurred during calculation.")

    def _get_network_details(self, network, new_prefix=None) -> Dict[str, Any]:
        """
        Analyzes a network object and returns a dictionary of its properties.
        This separates the logic from the formatting.
        """
        details = {
            "IP Version": f"IPv{network.version}",
            "Address": str(network.network_address),
            "CIDR": f"/{network.prefixlen}",
            "Netmask": str(network.netmask),
            "Total Addresses": network.num_addresses,
        }

        if isinstance(network, ipaddress.IPv4Network):
            details.update({
                "Wildcard Mask": str(network.hostmask),
                "Broadcast Address": str(network.broadcast_address),
                "Usable Host Range": f"{network.network_address + 1} - {network.broadcast_address - 1}",
                "Usable Hosts": max(0, network.num_addresses - 2),
            })
        else: # IPv6
            details.update({
                "Usable Host Range": "N/A (Typically the entire subnet)",
                "Usable Hosts": network.num_addresses,
                "Compressed Address": network.network_address.compressed,
            })

        # Subnetting information
        if new_prefix and new_prefix > network.prefixlen:
            num_subnets = 2 ** (new_prefix - network.prefixlen)
            subnets_list = list(network.subnets(new_prefix=new_prefix))
            first_subnet = subnets_list[0]
            
            details.update({
                "--- Subnetting ---": "",
                "Number of Subnets": f"{num_subnets} (using /{new_prefix})",
                "Addresses per Subnet": first_subnet.num_addresses,
                "First Subnet Range": f"{first_subnet.network_address} - {first_subnet.broadcast_address}",
            })
        
        return details

    def _display_results(self, data: Dict[str, Any]):
        """Formats and displays the results dictionary in the Text widget."""
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        
        for key, value in data.items():
            if "---" in key: # For section headers
                self.result_text.insert(tk.END, f"\n{key}\n")
            else:
                self.result_text.insert(tk.END, f"{key:<25}: {value}\n")
        
        self.result_text.config(state=tk.DISABLED)

    def visualize_network(self):
        """
        Creates a new window and visualizes the network and its subnets
        using Matplotlib and NetworkX.
        """
        if not self.network:
            messagebox.showwarning("No Network", "Please perform a calculation first.")
            return

        # --- Create a new top-level window for the plot ---
        vis_window = tk.Toplevel(self.root)
        vis_window.title("Network Visualization")
        vis_window.geometry("800x600")

        G = nx.Graph()
        
        # --- Define Node Properties ---
        main_net_node = str(self.network)
        main_net_color = "#3498db" # Blue
        subnet_color = "#f1c40f" # Yellow
        node_size = 4000
        
        G.add_node(main_net_node, color=main_net_color, label=main_net_node)

        # --- Add Subnet Nodes and Edges ---
        if self.new_subnet_prefix and self.new_subnet_prefix > self.network.prefixlen:
            subnets = list(self.network.subnets(new_prefix=self.new_subnet_prefix))
            # Display only a reasonable number of subnets to avoid clutter
            for subnet in subnets[:16]: 
                subnet_node = str(subnet)
                G.add_node(subnet_node, color=subnet_color, label=subnet_node)
                G.add_edge(main_net_node, subnet_node)
            if len(subnets) > 16:
                # Add a representative node for the rest
                etc_node = f"... ({len(subnets) - 16} more)"
                G.add_node(etc_node, color="#bdc3c7", label=etc_node) # Gray
                G.add_edge(main_net_node, etc_node)
        
        # --- Drawing the Graph ---
        pos = nx.spring_layout(G, seed=42) # Seed for reproducible layout
        colors = [data['color'] for node, data in G.nodes(data=True)]
        labels = {node: data['label'] for node, data in G.nodes(data=True)}

        fig = plt.figure(figsize=(10, 7))
        nx.draw(G, pos, labels=labels, with_labels=True, node_color=colors,
                node_size=node_size, font_size=9, font_weight='bold',
                edge_color="#7f8c8d")
        
        fig.suptitle("Network Topology", fontsize=16)

        # --- Embed Matplotlib plot in Tkinter window ---
        canvas = FigureCanvasTkAgg(fig, master=vis_window)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def clear_fields(self):
        """Clears all input fields and results."""
        self.ip_address_field.delete(0, tk.END)
        self.subnet_mask_field.delete(0, tk.END)
        self.new_subnet_prefix_field.delete(0, tk.END)
        
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state=tk.DISABLED)
        
        self.network = None
        self.new_subnet_prefix = None
        logger.info("Fields cleared.")

    def copy_results(self):
        """Copies the contents of the result box to the clipboard."""
        content = self.result_text.get(1.0, tk.END).strip()
        if content:
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            messagebox.showinfo("Copied", "Results copied to clipboard!")
        else:
            messagebox.showwarning("No Results", "There is nothing to copy.")

    # --- Export Methods ---

    def export_to_csv(self):
        """Exports the current results to a CSV file."""
        content = self.result_text.get(1.0, tk.END).strip()
        if not content:
            messagebox.showwarning("No Results", "There are no results to export.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension='.csv',
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not file_path: return

        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Parameter', 'Value']) # Header
                for line in content.split('\n'):
                    if ':' in line:
                        writer.writerow([item.strip() for item in line.split(':', 1)])
            messagebox.showinfo("Export Successful", f"Results exported to\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export to CSV: {e}")

    def export_to_pdf(self):
        """Exports the current results to a PDF file."""
        content = self.result_text.get(1.0, tk.END).strip()
        if not content:
            messagebox.showwarning("No Results", "There are no results to export.")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension='.pdf',
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if not file_path: return

        try:
            doc = SimpleDocTemplate(file_path, pagesize=letter)
            styles = getSampleStyleSheet()
            elements = []

            elements.append(Paragraph("IP Calculation Report", styles['h1']))
            elements.append(Spacer(1, 12))

            data = [['Parameter', 'Value']]
            for line in content.split('\n'):
                if ':' in line:
                    data.append([item.strip() for item in line.split(':', 1)])

            table = Table(data, colWidths=[200, 300])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(table)
            
            doc.build(elements)
            messagebox.showinfo("Export Successful", f"Results exported to\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export to PDF: {e}")


# ==============================================================================
# Helper Class for Redirecting Output
# ==============================================================================
class TextRedirector(io.StringIO):
    """
    A helper class to redirect stdout/stderr to a Tkinter Text widget.
    """
    def __init__(self, widget: tk.Text):
        super().__init__()
        self.widget = widget

    def write(self, string: str):
        self.widget.config(state=tk.NORMAL)
        self.widget.insert(tk.END, string)
        self.widget.see(tk.END) # Auto-scroll
        self.widget.config(state=tk.DISABLED)
    
    def flush(self):
        # This method is needed for compatibility.
        pass


# ==============================================================================
# Entry Point of the Application
# ==============================================================================
if __name__ == "__main__":
    # Create the main window
    root = tk.Tk()
    
    # Instantiate the application class
    app = IPCalculator(root)
    
    # Start the Tkinter event loop
    root.mainloop()