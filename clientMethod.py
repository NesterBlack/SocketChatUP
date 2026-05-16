import tkinter
import tkinter as tk
import os
from tkinter import filedialog
import socket
import pickle

def send_data(sock, data):
    payload = pickle.dumps(data)
    sock.sendall(len(payload).to_bytes(4, "big") + payload)

def recv_data(sock):
    raw_len = b""
    while len(raw_len) < 4:
        chunk = sock.recv(4 - len(raw_len))
        if not chunk:
            raise ConnectionResetError
        raw_len += chunk
    msg_len = int.from_bytes(raw_len, "big")
    data = b""
    while len(data) < msg_len:
        chunk = sock.recv(msg_len - len(data))
        if not chunk:
            raise ConnectionResetError
        data += chunk
    return pickle.loads(data)

def on_file_click(event, file_content: bytes, file_name):
    print("rectangle clicked!")
    downloads_path = os.path.join(os.path.expanduser("~"), "Downloads", file_name)
    with open(downloads_path, "wb") as f:
        print(file_name, file_content)
        f.write(file_content)


def draw_round_rect(canvas, x1, y1, x2, y2, radius=25, color=(0,0,0), **kwargs):
    points = [x1+radius, y1, x2-radius, y1, x2, y1, x2, y1+radius,
              x2, y2-radius, x2, y2, x2-radius, y2, x1+radius, y2,
              x1, y2, x1, y2-radius, x1, y1+radius, x1, y1]
    return canvas.create_polygon(points, **kwargs, smooth=True, fill="#%02x%02x%02x"%color)

class Message:
    def __init__(self, author, text):
        self.author = author
        self.text = text
        self.message_id = int()
class AuthorName:
    def __init__(self, author):
        self.author = author

class File:
    def __init__(self, path, author):
        self.author = author
        self.message_id = int()
        self.file_name = os.path.basename(path)
        print(self.file_name)
        with open(path, "rb") as file:
            self.content = file.read()
            print(type(self.content))
            print(self.content)


class ClientMethod:
    def __init__(self, root: tkinter.Tk, client: socket.socket, is_server: bool):
        self.client = client
        self.root = root
        self.is_serer = is_server

        self.my_name = "Moderator"
        self.state = "name_input"
        if not is_server:
            self.state = "ip_input"
        self.offset = 0

        self.massages = []
        self.all_rooms = {}
        self.room_name = None

        self.current_files_path = tuple()

        self.ipLabel = None
        self.inputServerName = None
        self.inputName = None
        self.greate = None
        self.label_name = None
        self.roomL = None
        self.leaveB = None
        self.sendB = None
        self.getFileB = None
        self.inputLine = None
        self.inputName = None
        self.inputServerName = None

    def draw(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        if self.is_serer:
            self.ipLabel = tk.Label(self.root, text=socket.gethostbyname('localhost'), font=("Arial", 20))
            self.ipLabel.place(relx=0.5, rely=0, anchor="n")

        if self.state == "ip_input":
            self.label_ip = tk.Label(self.root, text="input server ip")
            self.inputIp = tk.Entry(self.root, width=55)
            self.greate = tk.Button(self.root, text="greate", command=self.connect)

            self.label_ip.place(relx=0.5, rely=.45, anchor="n")
            self.inputIp.place(relx=0, rely=.5)
            self.greate.place(relx=.875, rely=.495)

        elif self.state == "pr_chat":
            self.inputLine = tk.Entry(self.root, width=50)
            self.sendB = tk.Button(self.root, text="Send", command=self.get_input)
            self.getFileB = tk.Button(self.root, text="File", command=self.get_file)
            self.leaveB = tk.Button(self.root, text="Leave", command=self.leave_server)

            self.inputLine.place(x=10, rely=.9, relwidth=1.0, width=-105)
            self.sendB.place(relx=1, rely=.895, x = -50)
            self.getFileB.place(relx=1, rely=.895, x = -85)
            self.leaveB.place(relx=1, x=-50)
            self.roomL = tk.Label(self.root, text=self.room_name, font=("Arial", 11))
            if self.is_serer:
                self.roomL.place(relx=0.5, y=30, anchor="n")
            else:
                self.roomL.place(relx=0.5, rely=0, anchor="n")


            canvas = tk.Canvas(self.root, bg="#%02x%02x%02x" % (240, 240, 240))
            # canvas.bind("<Configure>", self.draw_call)
            canvas.place(x=0,
                         y=35,
                         relwidth=1.0,
                         relheight=1.0,
                         height=-120)
            if self.current_files_path:
                file_group_tag = "file_rect"
                draw_round_rect(canvas, 0, 0, 100, 100,25, (150,150,150), tags=file_group_tag)
                canvas.create_text(50, 30, text="Files", fill="white", font = ("Amiri", 20, "bold"), tags=file_group_tag)
                canvas.create_text(50, 60, text=f"{len(self.current_files_path)} files", fill="white", font = ("Amiri", 12, "bold"), tags=file_group_tag)
                canvas.move(file_group_tag, 20, 400)

            y = 0
            self.root.update_idletasks()
            x_east = canvas.winfo_width()-10
            print(f"canvas: {x_east}")
            for index, data in enumerate(self.massages):
                if type(data) == Message:
                    if data.author == self.my_name:
                        canvas.create_text(x_east, y + self.offset + 20, text=data.text, font=("Arial", 9), anchor="ne")
                    else:
                        canvas.create_text(10, y + self.offset + 20, text=data.text, font=("Arial", 9), anchor="nw")
                    y += 15
                elif type(data) == AuthorName:
                    if data.author == self.my_name:
                        canvas.create_text(x_east, y + self.offset + 20, text=data.author, font=("Arial", 11, "bold"), anchor="ne")
                    else:
                        canvas.create_text(10, y + self.offset + 20, text=data.author, font=("Arial", 11, "bold"), anchor="nw")
                    y += 25
                elif type(data) == File:
                    send_file_group_tag = f"send_file_group_tag{y}"
                    rect = draw_round_rect(canvas, 0, 0, 100, 100, 25, (150, 150, 150), tags=send_file_group_tag)
                    text = canvas.create_text(50, 30, text=data.file_name, fill="white", font = ("Amiri", 15, "bold"), tags=send_file_group_tag)


                    if data.author == self.my_name:
                        x = x_east-110
                    else:
                        x = 20

                    canvas.move(send_file_group_tag, x, y + self.offset + 20)

                    canvas.tag_bind(rect, "<Button-1>", lambda event: on_file_click(event, data.content, data.file_name))
                    y += 105

        elif self.state == "name_input":
            self.label_name = tk.Label(self.root, text="your name")
            self.inputName = tk.Entry(self.root, width=55)
            self.greate = tk.Button(self.root, text="greate", command=self.new_name)

            self.label_name.place(relx=0.5, rely=.5, y=-20, anchor="n")
            self.inputName.place(x=10, rely=0.5, relwidth=1.0, width=-70)
            self.greate.place(relx=1, rely=.495, x = -50)

        elif self.state == "menu":
            hostB = tk.Button(self.root, text="host", command=lambda: self.change_state("host"))
            joinB = tk.Button(self.root, text="join", command=lambda: self.change_state("join"))

            hostB.place(relx=.4, rely=.5)
            joinB.place(relx=.6, rely=.5)
        elif self.state == "host":
            self.label_name = tk.Label(self.root, text="server name")
            self.inputServerName = tk.Entry(self.root, width=55)
            self.greate = tk.Button(self.root, text="greate", command=self.host_server)

            self.label_name.place(relx=0.45, rely=.45)
            self.inputServerName.place(x=10, rely=.5, relwidth=1.0, width=-70)
            self.greate.place(relx=1, rely=.495, x=-50)
        elif self.state == "join":
            x = 10
            y = 10
            buttons = list()
            for id_r in self.all_rooms:
                print(f"ID: {id_r}")
                btn = tk.Button(self.root, text=self.all_rooms[id_r], command=lambda id_r=id_r: self.join_server(id_r))
                print(btn)
                # print(btn.)
                buttons.append(btn)
            print(self.all_rooms, "rooms")
            for b in buttons:
                print(b)
                if x >= 380 - b.winfo_width():
                    x = 10
                    y += 25
                b.place(x=x, y=y)
                x += b.winfo_width() + 10

    def draw_call(self, event):
        self.draw()

    def print_message(self, ):
        for msg in self.massages:
            try:
                print(msg.text, end=" ")
            except AttributeError:
                print(msg.author, end=" ")
        print()

    def change_state(self, state_new):
        self.state = state_new
        self.draw()
        if state_new == "join":
            send_data(self.client, "/get_all_rooms")

    def get_input(self, ):
        input = self.inputLine.get()

        if self.current_files_path:
            for path in self.current_files_path:
                if os.path.exists(path):
                    send_data(self.client, File(path, self.my_name))
            self.current_files_path = tuple()

        if input.split():
            data_input = input
            send_data(self.client, Message(self.my_name, data_input))

        self.inputLine.delete(0, tk.END)

    def get_file(self,):
        self.current_files_path = filedialog.askopenfilenames(
            title="Select a file",
            filetypes=(("Python codes", "*.py"), ("All files", "*.*"))
        )

        if not self.current_files_path:
            self.current_files_path = None
        self.draw()

    def get_message(self, data):
        self.massages = data
        self.draw()
        print(data, "data")

    def key_press(self, event):
        if event.keycode == 13:
            if self.state == "name_input":
                self.new_name()
            elif self.state == "pr_chat":
                self.get_input()

    def scroll_chat(self, event: tkinter.Event):
        self.offset += (event.delta / abs(event.delta)) * 10
        self.draw()

    def new_name(self, ):
        self.my_name = self.inputName.get()
        if self.my_name.split():
            send_data(self.client, "/state menu")
            send_data(self.client, f"/name {self.my_name}")
            self.state = "menu"
            self.draw()
        else:
            self.inputName.delete(0, tk.END)

    def host_server(self, ):
        server_name = self.inputServerName.get()
        send_data(self.client, f"/host_r {server_name}")
        self.room_name = server_name
        self.change_state("pr_chat")

    def join_server(self, id_r):
        send_data(self.client, f"/join_r {id_r}")
        self.room_name = self.all_rooms[id_r]
        self.change_state("pr_chat")
        send_data(self.client, f"/get_all_message {id_r}")
        print(id_r)

    def leave_server(self, ):
        send_data(self.client, "/leave_r")
        self.massages.clear()
        self.state = "menu"
        self.draw()

    def connect(self):
        ip = self.inputIp.get()
        try:
            self.client = socket.create_connection((ip, 5555))
            self.state = "name_input"
            self.draw()
            print("connected, cool")
        except socket.gaierror:
            self.errorLabel = tk.Label(self.root, text="error ip, pls try again", fg="#b80000")
            self.errorLabel.place(relx=0.5, rely=.42, anchor="n")
