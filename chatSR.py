from clientMethod import *
import threading
import queue

root = tk.Tk()
root.geometry(("%dx%d+%d+%d" % (400, 600, 500, 100)))
root.title("ChatServer")

rooms = {}
clients_info = {}
commands = ["/clear", "/join_r", "/leave_r", "/host_r", "/name", "/state", "/get_all_rooms", "/get_all_message"]

ui_queue = queue.Queue()

def command_input(cl, command: str):
    match command.split()[0]:
        case "/clear":
            room_id = clients_info[cl]["room"]
            rooms[room_id]["messages"].clear()

        case "/name":
            clients_info[cl]["name"] = " ".join(command.split()[1:])
            clients_info[cl]["state"] = "menu"

        case "/host_r":
            room_id = str(len(rooms))
            rooms[room_id] = {}
            rooms[room_id]["name"] = " ".join(command.split()[1:])
            rooms[room_id]["clients"] = []
            rooms[room_id]["messages"] = []
            rooms[room_id]["last_author"] = None
            rooms[room_id]["max_msg_id"] = 0
            rooms[room_id]["clients"].append(cl)
            clients_info[cl]["room"] = room_id
            print(room_id, clients_info[cl]["room"])
            clients_info[cl]["state"] = "pr_chat"

        case "/join_r":
            room_id = command.split()[1]
            rooms[room_id]["clients"].append(cl)
            clients_info[cl]["room"] = room_id
            clients_info[cl]["state"] = "pr_chat"

        case "/leave_r":
            room_id = clients_info[cl]["room"]
            rooms[room_id]["clients"].remove(cl)
            clients_info[cl]["room"] = None
            clients_info[cl]["state"] = "menu"

        case "/get_all_rooms":
            rooms_es = {id: rooms[id]["name"] for id in rooms}
            send_data(cl, rooms_es)

        case "/get_all_message":
            messages = rooms[command.split()[1]]["messages"]
            send_data(cl, messages)

        case "/state":
            clients_info[cl]["state"] = command.split()[1]


def ls_client(cl, address):
    print(f"new client [+][{address}]")
    clients_info[cl] = {"state": "name_input", "name": None, "room": None}

    while True:
        # try:
        data = recv_data(cl)
        if not data:
            break

        if type(data) == str:
            if data.split()[0] in commands:
                command_input(cl, data)

        if type(data) == Message:
            print("New message")
            room_id = clients_info[cl]["room"]
            message_author = clients_info[cl]["name"]
            message_id = rooms[room_id]["max_msg_id"]
            rooms[room_id]["max_msg_id"] += 1

            data.id = message_id

            if rooms[room_id]["last_author"] != message_author:
                rooms[room_id]["messages"].append(AuthorName(message_author))
                rooms[room_id]["last_author"] = message_author


            rooms[room_id]["messages"].append(data)

            for client in rooms[room_id]["clients"]:
                send_data(client, rooms[room_id]["messages"])

            ui_queue.put(("messages", rooms[room_id]["messages"]))
        elif type(data) == File:
            print("New file")
            room_id = clients_info[cl]["room"]
            file_author = clients_info[cl]["name"]
            file_id = rooms[room_id]["max_msg_id"]
            rooms[room_id]["max_msg_id"] += 1

            data.id = file_id

            if rooms[room_id]["last_author"] != file_author:
                rooms[room_id]["messages"].append(AuthorName(file_author))
                rooms[room_id]["last_author"] = file_author


            rooms[room_id]["messages"].append(data)

            for client in rooms[room_id]["clients"]:
                send_data(client, rooms[room_id]["messages"])

            ui_queue.put(("messages", rooms[room_id]["messages"]))

        # except Exception as e:
        #     print(f"Помилка клієнта {address}: {e}")
        #     break

    if cl in clients_info:
        room_id = clients_info[cl].get("room")
        if room_id and room_id in rooms:
            if cl in rooms[room_id]["clients"]:
                rooms[room_id]["clients"].remove(cl)
        clients_info.pop(cl)

    print(f"close client [-]{address}")


def accept_loop(server):
    while True:
        try:
            cl, address = server.accept()
            threading.Thread(target=ls_client, args=(cl, address), daemon=True).start()
        except:
            break


def poll_ui_queue():
    try:
        while True:
            task = ui_queue.get_nowait()
            if task[0] == "messages":
                clientMet.get_message(task[1])
                clientMet.draw()
    except queue.Empty:
        pass
    root.after(100, poll_ui_queue)

def client_loop(client):
    clientMet.draw()

    root.bind("<Key>", clientMet.key_press)
    root.bind("<MouseWheel>", clientMet.scroll_chat)
    while True:
        try:
            data = recv_data(client)
            if clientMet.state == "pr_chat":
                clientMet.get_message(data)
            elif clientMet.state == "join":
                clientMet.all_rooms = data
                clientMet.draw()
        except KeyboardInterrupt:
            break

def main():
    global clientMet, server

    server = socket.create_server(("localhost", 5555))
    client = socket.create_connection(("localhost", 5555))
    clientMet = ClientMethod(root, client, True)

    clientMet.draw()
    root.bind("<Key>", clientMet.key_press)
    root.bind("<MouseWheel>", clientMet.scroll_chat)

    root.after(100, poll_ui_queue)

    threading.Thread(target=accept_loop, args=(server,), daemon=True).start()
    threading.Thread(target=client_loop, args=(client,), daemon=True).start()

    print("server started")

    root.mainloop()


if __name__ == "__main__":
    main()