import threading

from clientMethod import *

# client = socket.create_connection(("192.168.0.179", 5555))


root = tk.Tk()
root.geometry(("%dx%d+%d+%d" % (400, 600, 500, 100)))
root.title("ChatClient")

clientMet = ClientMethod(root, None, False)

def main_loop():
    clientMet.draw()

    root.bind("<Key>", clientMet.key_press)
    root.bind("<MouseWheel>", clientMet.scroll_chat)

    while True:
        if clientMet.client:
            client = clientMet.client
            while True:
                try:
                    data = recv_data(client)
                    if clientMet.state == "pr_chat":
                        clientMet.get_message(data)
                    elif clientMet.state == "join":
                        print(data)
                        clientMet.all_rooms = data
                        clientMet.draw()
                except KeyboardInterrupt:
                    break
            break

chat_loop = threading.Thread(target=main_loop)
chat_loop.start()

root.mainloop()
