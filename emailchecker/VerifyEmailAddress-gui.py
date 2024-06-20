import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import csv
from pathlib import Path
import threading
import re
import smtplib
import dns.resolver
import os


class EmailVerifierGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Email Verifier")

        self.proxy_label = tk.Label(root, text="Proxy List File:")
        self.proxy_label.grid(row=0, column=0, sticky="w")
        self.proxy_entry = tk.Entry(root)
        self.proxy_entry.grid(row=0, column=1)
        self.proxy_button = tk.Button(root, text="Browse", command=self.browse_proxy_file)
        self.proxy_button.grid(row=0, column=2)

        self.mail_label = tk.Label(root, text="Mail Box File:")
        self.mail_label.grid(row=1, column=0, sticky="w")
        self.mail_entry = tk.Entry(root)
        self.mail_entry.grid(row=1, column=1)
        self.mail_button = tk.Button(root, text="Browse", command=self.browse_mail_file)
        self.mail_button.grid(row=1, column=2)
        
        self.line_label = tk.Label(root, text="From line number:")
        self.line_label.grid(row=2, column=0, sticky="w")
        self.line_entry = tk.Entry(root)
        self.line_entry.grid(row=2, column=1)
        
        self.line_entry.insert(tk.END, "1")

        self.output_label = tk.Label(root, text="Output File Name:")
        self.output_label.grid(row=3, column=0, sticky="w")
        self.output_entry = tk.Entry(root)
        self.output_entry.grid(row=3, column=1)

        self.output_entry.insert(tk.END, "output.csv")
        
        self.LIVE_label = tk.Label(root, text="number of LIVE mails:")
        self.LIVE_label.grid(row=4, column=0, sticky="w")
        self.LIVE_n_label = tk.Label(root, text="0")
        self.LIVE_n_label.grid(row=4, column=0, sticky="w", padx=170)
        
        self.DIE_label = tk.Label(root, text="number of DIE mails:")
        self.DIE_label.grid(row=5, column=0, sticky="w")
        self.DIE_n_label = tk.Label(root, text="0")
        self.DIE_n_label.grid(row=5, column=0, sticky="w", padx=170)
        
        self.UNKNOWN_label = tk.Label(root, text="number of UNKNOWN mails:")
        self.UNKNOWN_label.grid(row=6, column=0, sticky="w")
        self.UNKNOWN_n_label = tk.Label(root, text="0")
        self.UNKNOWN_n_label.grid(row=6, column=0, sticky="w", padx=170)

        self.run_button = tk.Button(root, text="Run", command=self.run_verification)
        self.run_button.grid(row=7, column=0, sticky='w', padx=10)
        self.pause_button = tk.Button(root, text="Pause", command=self.pause_verification)
        self.pause_button.grid(row=7, column=0, sticky='w', padx=65)
        self.exit_button = tk.Button(root, text="Exit", command=self.exit_program)
        self.exit_button.grid(row=7, column=0, sticky='w', padx=130)

        self.log_output = tk.Text(root, height=30, width=100)
        self.log_output.grid(row=8, columnspan=3, padx=10)
        
         # Create tabs
        self.notebook = ttk.Notebook(self.log_output)
        self.notebook.pack(expand=True, fill='both')

        # First tab - Log Output
        self.log_tab = tk.Frame(self.notebook)
        self.notebook.add(self.log_tab, text="Log Output")
        self.create_log_output()

        # Second tab - Table
        self.table_tab = tk.Frame(self.notebook)
        self.notebook.add(self.table_tab, text="Table")
        self.create_table()


        self.running = False
        self.proxy_file = ""
        self.mail_file = ""
        self.output_file = ""
       
       
    def add_to_table(self, email, status, domain):
        self.table.insert("", "end", values=(email, status, domain))
       
    def create_log_output(self):
        self.log_output = tk.Text(self.log_tab, height=30, width=100)
        self.log_output.pack(fill='both', expand=True)

    def create_table(self):
        self.table = ttk.Treeview(self.table_tab, columns=("Email", "Status", "Domain"), show="headings")
        self.table.heading("Email", text="Email")
        self.table.heading("Status", text="Status")
        self.table.heading("Domain", text="Domain")
        self.table.pack(fill='both', expand=True)
       
    def browse_proxy_file(self):
        current_dir = os.getcwd()
        filename = filedialog.askopenfilename(title="Select Proxy List File", filetypes=(("Text files", "*.txt"), ("All files", "*.*")), initialdir=current_dir)
        if filename:
            self.proxy_entry.delete(0, tk.END)
            self.proxy_entry.insert(tk.END, filename)
            self.proxy_file = filename

    def browse_mail_file(self):
        current_dir = os.getcwd()
        filename = filedialog.askopenfilename(title="Select Mail Box File", filetypes=(("Text files", "*.txt"), ("All files", "*.*")), initialdir=current_dir)
        if filename:
            self.mail_entry.delete(0, tk.END)
            self.mail_entry.insert(tk.END, filename)
            self.mail_file = filename

    def run_verification(self):
        if not self.proxy_file or not self.mail_file or not self.output_entry.get():
            self.log_output.insert(tk.END, "Please select Proxy List file, Mail Box file, and specify Output file.\n")
            return
        

        self.running = True
        self.run_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)

        self.output_file = self.output_entry.get()

        # self.log_output.delete(1.0, tk.END)
        self.log_output.insert(tk.END, "Verification started...\n")

        verification_thread = threading.Thread(target=self.start_verification)
        verification_thread.start()

    def pause_verification(self):
        self.running = False
        self.run_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)

    def start_verification(self):
        
        if int(self.line_entry.get()) == 1:
            self.LIVE_n_label['text'] = 0
            self.DIE_n_label['text'] = 0
            self.UNKNOWN_n_label['text'] = 0
                       
            with open(self.output_file, 'w', newline='') as csvfile_create:
                csv_writer = csv.writer(csvfile_create)
                csv_writer.writerow(["Email", "Status", "Domain"])
        else:
            with open(self.mail_file, 'r') as mail_file:
                for line_no, line in enumerate(mail_file, start=1):
                    if not self.running:
                        self.log_output.insert(tk.END, "Verification paused.\n")
                        break

                    if line_no >= int(self.line_entry.get()):
                        with open(self.output_file, 'a', newline='') as csvfile_append:
                            email = line.strip()
                            try:
                                status, domain = self.verify_email(email)
                            except Exception as e:
                                status = "UNKNOWN"
                                domain = "UNKNOWN"
                                
                                # self.log_output.tag_config("UNKNOWN", foreground="orange")                            
                                # self.log_output.insert(tk.END, f"{self.line_entry.get()} => Email: {email}, Status: {status}, Domain: {domain}\n", status)
                                # self.log_output.see(tk.END)
                                # csv_writer = csv.writer(csvfile_append)
                                # csv_writer.writerow([email, status, domain])
                                pass
                                
                            self.add_to_table(email, status, domain)
                            csv_writer = csv.writer(csvfile_append)
                            csv_writer.writerow([email, status, domain])
                            self.log_output.tag_config("LIVE", foreground="green")
                            self.log_output.tag_config("UNKNOWN", foreground="orange")
                            self.log_output.tag_config("DIE", foreground="red")
                            self.log_output.insert(tk.END, f"{self.line_entry.get()} => Email: {email}, Status: {status}, Domain: {domain}\n", status)
                            self.log_output.see(tk.END)
                            # increase line number
                            current_line_number = int(self.line_entry.get())
                            self.line_entry.delete(0, tk.END)
                            self.line_entry.insert(0, current_line_number + 1)
                            if status == "LIVE":
                                current_line_number_LIVE = int(self.LIVE_n_label.cget("text"))
                                self.LIVE_n_label['text'] = current_line_number_LIVE + 1
                            elif status == "DIE":
                                current_line_number_DIE = int(self.DIE_n_label.cget("text"))
                                self.DIE_n_label['text'] = current_line_number_DIE + 1
                            else:
                                current_line_number_UNKNOWN = int(self.UNKNOWN_n_label.cget("text"))
                                self.UNKNOWN_n_label['text'] = current_line_number_UNKNOWN + 1

                else:
                    self.log_output.insert(tk.END, "Nothing todo.\n")
                    self.running = False
                    self.run_button.config(state=tk.NORMAL)
                    

    def verify_email(self, email):
        
        # Address used for SMTP MAIL FROM command
        fromAddress = 'corn@bt.com'

        # Simple Regex for syntax checking
        regex = '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,})$'

        # Email address to verify
        addressToVerify = str(email)

        # Syntax check
        match = re.match(regex, addressToVerify.lower())
        if match is None:
            # print('\033[91m' + 'DIE' + '\033[0m' + " => " + '\033[96m' + email + '\033[91m' + ' Bad Syntax', end='')
            stat = 'DIE'
            return stat, 'UNKNOWN'

        # Get domain for DNS lookup
        splitAddress = addressToVerify.split('@')
        domain = str(splitAddress[1])

        # MX record lookup
        try:
            records = dns.resolver.resolve(domain, 'MX')
            mxRecord = records[0].exchange
            mxRecord = str(mxRecord)
        except:
            # print('\033[91m' + 'DIE' + '\033[0m' + " => " + '\033[96m' + email + '\033[90m' + ' No MX Record found for domain: ' + '\033[95m' + domain, end='')
            stat = 'DIE'
            return stat, domain

        # SMTP lib setup (use debug level for full output)
        server = smtplib.SMTP(timeout=25)
        server.set_debuglevel(0)

        # SMTP Conversation
        try:
            server.connect(mxRecord)
            server.helo(server.local_hostname)  # server.local_hostname(Get local server hostname)
            server.mail(fromAddress)
            code, message = server.rcpt(str(addressToVerify))
            server.quit()

            # Assume SMTP response 250 is success
            if code == 250:
                # print('\033[92m' + "LIVE" + '\033[0m' + " => " + '\033[96m' + email + ' domain: ' + '\033[95m' + domain, end="")
                stat = 'LIVE'
            else:
                # print('\033[91m' + "DIE" + '\033[0m' + " => " + '\033[96m' + email + ' domain: ' + '\033[95m' + domain, end="")
                stat = 'DIE'
        except smtplib.SMTPException as e:
            # print('\033[1m' + "UNKNOWN" + '\033[0m' + " => " + '\033[96m' + email + '\033[91m' + 'SMTP Exception:', end='')
            stat = 'UNKNOWN'
            return stat, domain

        return stat, domain

    def exit_program(self):
        if self.running:
            self.log_output.insert(tk.END, "Please pause the verification before exiting.\n")
        else:
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = EmailVerifierGUI(root)
    root.mainloop()