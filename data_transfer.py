import tkinter as tk
from tkinter import scrolledtext
import threading
import socket
import sys

class GuiApp:
    def __init__(self, gui_root):
        self.root = gui_root
        self.ip_addr_label = None
        self.ip_addr_entry = None
        self.connect_button = None
        self.listen_button = None
        self.disconnect_button = None
        self.connected_ip_label = None
        self.data_label = None
        self.data_input = None
        self.text_area = None
        self.socket_server = None
        self.client_socket = None
        self.addr = None
        self.listen_ip = '0.0.0.0'
        self.port = 65432

    def update_text_area(self, message):
        self.text_area.configure(state='normal')
        self.text_area.insert(tk.END, message + '\n')
        self.text_area.configure(state='disabled')

def handle_messages(gui):
    def receive_messages():
        while True:
            try:
                message = gui.client_socket.recv(1024)
                if not message:
                    gui.update_text_area('> Client disconnected')
                    Disconnect(gui)
                    break
                gui.update_text_area(f'< {message.decode("utf-8")}')
            except Exception as e:
                gui.update_text_area(f'Error receiving message: {e}')
                Disconnect(gui)
                break

    threading.Thread(target=receive_messages, daemon=True).start()

def Connect(gui):
    gui.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip_addr = gui.ip_addr_entry.get()
    try:
        gui.client_socket.connect((ip_addr, gui.port))
        gui.connected_ip_label.config(text=f'Connected IP: {ip_addr}')
        gui.text_area.delete('1.0', tk.END)
        handle_messages(gui)
    except Exception as e:
        gui.update_text_area(f'> Unexpected error occurred: {e}')

def Listener(gui):
    if gui.client_socket is not None:
        gui.client_socket.close()
        gui.update_text_area('> Client socket closed.')
    
    try:
        gui.socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        gui.socket_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        gui.socket_server.bind((gui.listen_ip, gui.port))
        gui.socket_server.listen(1)
        gui.connected_ip_label.config(text='Listening...')
        
        def accept_connection():
            gui.client_socket, gui.addr = gui.socket_server.accept()
            gui.connected_ip_label.config(text=f'Connected IP: {gui.addr}')
            handle_messages(gui)

        threading.Thread(target=accept_connection).start()
        
    except Exception as e:
        gui.update_text_area(f'> Unexpected error occurred: {e}')

def Disconnect(gui):
    if gui.client_socket is not None:
        gui.client_socket.close()
        gui.client_socket = None
        gui.connected_ip_label.config(text='Connected IP: None')
        gui.update_text_area('> Disconnected from client.')

def on_enter_pressed(event, gui):
    data_text = gui.data_input.get()
    if data_text:
        try:
            if gui.client_socket is not None:
                gui.client_socket.send(data_text.encode('utf-8'))
                gui.update_text_area(f'> {data_text}')
                gui.data_input.delete(0, tk.END)
            else:
                gui.update_text_area('> No connection established.')
        except Exception as e:
            gui.update_text_area(f'> Error sending message: {e}')

def initialize_gui(gui):
    gui.root.title('Data Transfer')
    
    gui.ip_addr_label = tk.Label(gui.root, text='IP ADDRESS:')
    gui.ip_addr_label.grid(row=1, column=0)
    
    gui.ip_addr_entry = tk.Entry(gui.root)
    gui.ip_addr_entry.grid(row=1, column=1)
    
    gui.connect_button = tk.Button(gui.root, text='Connect', command=lambda: Connect(gui))
    gui.connect_button.grid(row=1, column=2)
    
    gui.listen_button = tk.Button(gui.root, text='Listen', command=lambda: Listener(gui))
    gui.listen_button.grid(row=1, column=3)

    gui.disconnect_button = tk.Button(gui.root, text='Disconnect', command=lambda: Disconnect(gui))
    gui.disconnect_button.grid(row=1, column=4)

    gui.connected_ip_label = tk.Label(gui.root, text='Connected IP: None')
    gui.connected_ip_label.grid(row=2, columnspan=5)
    
    gui.data_label = tk.Label(gui.root, text='Data:')
    gui.data_label.grid(row=3, column=0)
    
    gui.data_input = tk.Entry(gui.root)
    gui.data_input.grid(row=3, column=1)
    
    gui.data_input.bind("<Return>", lambda event: on_enter_pressed(event, gui))
    
    gui.text_area = scrolledtext.ScrolledText(gui.root, wrap=tk.WORD, width=40, height=10, font=("Times New Roman", 15))
    gui.text_area.grid(row=4, columnspan=5, pady=10, padx=10)
    
    gui.text_area.configure(state='disabled')

def main():
    """Main function to start the application."""
    root = tk.Tk()
    gui = GuiApp(root)
    initialize_gui(gui)
    root.mainloop()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("KEYBOARD INTERRUPT")
        sys.exit(1)

