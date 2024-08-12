from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import ipaddress
import sys
import io
import os
import json
import csv
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx


vis_window = None
fig = None
ax = None
canvas = None

def export_to_csv():
    # Get the results from result_text
    results = result_text.get().strip().split('\n')
    
    if not results or all(result == "" for result in results):
        messagebox.showwarning("No Results", "There are no results to export.")
        return
    
    # Open a dialog window for the user to choose where to save the file
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

def export_to_pdf():
    # Get the IP address from the input field
    ip_address = ip_address_field.get().strip()

    # Get the results from result_text
    results = result_text.get().strip().split('\n')
    
    if not results or all(result == "" for result in results):
        messagebox.showwarning("No Results", "There are no results to export.")
        return
    
    # Open a dialog window for the user to choose where to save the file
    file_path = filedialog.asksaveasfilename(defaultextension='.pdf',
                                             filetypes=[("PDF files", "*.pdf")])
    
    if file_path:
        try:
            doc = SimpleDocTemplate(file_path, pagesize=letter)
            styles = getSampleStyleSheet()
            elements = []
            
            title_text = f"IP Calculation Results for {ip_address} with subnet mask {subnet_mask_field.get()} and new subnet prefix {new_subnet_prefix_field.get()}"
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

def load_language(lang):
    try:
        with open(os.path.join("locales", f"{lang}.json"), "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        messagebox.showerror("Error", f"Language file {lang}.json not found")
        return None

def visualize_network(network, new_prefix=None):
    G = nx.Graph()

    # Προσθήκη κόμβων και ακμών
    subnets = list(network.subnets(new_prefix=new_prefix)) if new_prefix else [network]
    for subnet in subnets:
        G.add_node(str(subnet.network_address), label=f"{subnet.network_address}/{subnet.prefixlen}")

    for i in range(len(subnets) - 1):
        G.add_edge(str(subnets[i].network_address), str(subnets[i + 1].network_address))

    # Σχεδίαση του γραφήματος
    pos = nx.spring_layout(G)
    labels = nx.get_node_attributes(G, 'label')
    nx.draw(G, pos, with_labels=True, labels=labels, node_size=3000, node_color="lightblue", font_size=10, font_weight="bold", font_color="black")
    plt.title("Network Visualization")
    plt.show()

# Load language files
languages = {
    "en": load_language("en"),
    "el": load_language("el")
}

# Chosen language
current_language = "en"
texts = languages[current_language]

def change_language(lang):
    global current_language, texts
    current_language = lang
    texts = languages[current_language]
    root.title(texts["title"])
    ip_label.config(text=texts["ip_address"])
    mask_label.config(text=texts["subnet_mask"])
    new_subnet_label.config(text=texts["new_subnet_prefix"])
    calculate_button.config(text=texts["calculate"])
    clear_button.config(text=texts["clear"])
    copy_button.config(text=texts["copy_results"])
    export_button.config(text=texts["export_to_csv"])
    export_button.config(text=texts["export_to_csv"])
    pdf_export_button.config(text=texts["export_to_pdf"])
    visualize_button.config(text=texts["visualize"])
     # lang_button.config(text=texts["language"])

def load_flag_image(path, size=(24, 24)):
    if not os.path.exists(path):
        print(f"Warning: Image file not found: {path}")
        return None
    image = Image.open(path)
    image = image.resize(size, Image.LANCZOS)
    return ImageTk.PhotoImage(image)

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
    global current_graph  # Χρήση της παγκόσμιας μεταβλητής
    global network  # Χρήση της παγκόσμιας μεταβλητής για το δίκτυο
    global new_subnet_prefix  # Χρήση της παγκόσμιας μεταβλητής για το νέο πρόθεμα
    #current_graph = None  # Καθαρίστε το προηγούμενο γράφημα

    try:
        redirect_output()
        ip_address = ip_address_field.get()
        subnet_mask = subnet_mask_field.get()
        
        if not subnet_mask.startswith('/'):
            # Χειρισμός της μάσκας υποδικτύου
            try:
                if '.' in subnet_mask or ':' in subnet_mask:
                    subnet_mask = '/' + str(ipaddress.ip_network(f"0.0.0.0/{subnet_mask}", strict=False).prefixlen)
                else:
                    subnet_mask = '/' + subnet_mask
            except ValueError:
                messagebox.showerror("Error", "Invalid subnet mask")
                return
        
        new_subnet_prefix = new_subnet_prefix_field.get()  # Διάβασμα της νέας υποδιεύθυνσης
        if new_subnet_prefix:
            if new_subnet_prefix.startswith('/'):
                new_subnet_prefix = new_subnet_prefix[1:]  
            try:
                new_subnet_prefix = int(new_subnet_prefix)
            except ValueError:
                messagebox.showerror("Error", "Invalid new subnet prefix")
                return

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
            else:
                messagebox.showerror("Error", f"Invalid CIDR notation for IPv{ip_version}")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid subnet mask")
            return

        if not is_valid_subnet_mask(subnet_mask, ip_version):
            messagebox.showerror("Error", "Invalid subnet mask")
            return
        
        ip_class = get_ip_class(ip_obj)  # Load the ip class

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
                            f"IP Class: {ip_class}\n"
                            f"First usable address: {network.network_address + 1}\n"
                            f"Last usable address: {network.broadcast_address - 1}\n"
                            f"Number of subnets: {calculate_subnets(network, int(new_subnet_prefix)) if new_subnet_prefix else 'N/A'}")
        else:  # IPv6
            network = ipaddress.ip_network(f"{ip_address}/{cidr}", strict=False)
            first_usable = network.network_address + 1
            last_usable = network.network_address + network.num_addresses - 1
            result_text.set(f"Network address: {network.network_address}\n"
                            f"Subnet mask: /{network.prefixlen}\n"
                            f"CIDR notation: /{network.prefixlen}\n"
                            f"Number of addresses: {network.num_addresses}\n"
                            f"Usable addresses: {network.num_addresses}\n"
                            f"IP version: IPv{ip_version}\n"
                            f"IP Class: {ip_class}\n"
                            f"First usable address: {first_usable}\n"
                            f"Last usable address: {last_usable}\n"
                            f"Number of subnets: {calculate_subnets(network, int(new_subnet_prefix)) if new_subnet_prefix else 'N/A'}\n"
                            f"Compressed IPv6: {ip_obj.compressed}")

    except ValueError as e:
        messagebox.showerror("Error", str(e))
    except Exception as e:
        messagebox.showerror("Unexpected Error", f"An unexpected error occurred: {e}")


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
root.title(texts["title"])

# Load flag images
us_flag = load_flag_image("images/us.png")
gr_flag = load_flag_image("images/gr.png")

# Create labels and entry fields
ip_label = tk.Label(root, text=texts["ip_address"])
ip_label.grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
mask_label = tk.Label(root, text=texts["subnet_mask"])
mask_label.grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
new_subnet_label = tk.Label(root, text=texts["new_subnet_prefix"])
new_subnet_label.grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)

ip_address_field = tk.Entry(root)
ip_address_field.grid(row=0, column=1, padx=10, pady=5)
subnet_mask_field = tk.Entry(root)
subnet_mask_field.grid(row=1, column=1, padx=10, pady=5)
new_subnet_prefix_field = tk.Entry(root)
new_subnet_prefix_field.grid(row=2, column=1, padx=10, pady=5)

# Create buttons
calculate_button = tk.Button(root, text=texts["calculate"], command=calculate, bg="light blue")
calculate_button.grid(row=3, column=0, pady=10)
clear_button = tk.Button(root, text=texts["clear"], command=clear_fields, bg="light gray")
clear_button.grid(row=3, column=1, pady=10)
copy_button = tk.Button(root, text=texts["copy_results"], command=copy_results, bg="light green")
copy_button.grid(row=3, column=2, pady=10)

# Create export to CSV button
export_button = tk.Button(root, text=texts["export_to_csv"], command=export_to_csv, bg="light yellow")
export_button.grid(row=3, column=3, pady=10)

# Create export to PDF button
pdf_export_button = tk.Button(root, text=texts["export_to_pdf"], command=export_to_pdf, bg="light pink")
pdf_export_button.grid(row=3, column=4, pady=10)


# Create flag buttons for language selection
flag_frame = tk.Frame(root)
flag_frame.grid(row=0, column=4, padx=10, pady=5, sticky=tk.NE)

us_flag_button = tk.Button(flag_frame, image=us_flag, command=lambda: change_language("en"))
us_flag_button.pack(side=tk.LEFT, padx=2)
gr_flag_button = tk.Button(flag_frame, image=gr_flag, command=lambda: change_language("el"))
gr_flag_button.pack(side=tk.LEFT, padx=2)

# Create result display
result_text = tk.StringVar()
result_label = tk.Label(root, textvariable=result_text, justify=tk.LEFT)
result_label.grid(row=4, column=0, columnspan=3, sticky=tk.W, padx=10, pady=5)

# Create visualize button
visualize_button = tk.Button(root, text="Visualize", command=lambda: visualize_network(network, new_subnet_prefix), bg="lavender")
visualize_button.grid(row=0, column=2,padx=10, pady=10, sticky=tk.NE)

# Create debug text area
debug_text = tk.Text(root, height=10, width=50)
debug_text.grid(row=5, column=0, columnspan=3, padx=10, pady=5)
debug_text.config(state=tk.DISABLED)

# Configure grid
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)

root.mainloop()
