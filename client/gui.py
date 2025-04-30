import tkinter as tk
from PIL import Image, ImageTk
from tkinter import messagebox
from ttkbootstrap.scrolled import ScrolledFrame
import ttkbootstrap as ttk
import time
import os
import paint
import io
import base64
import Chat
import pickle


class GUI:
    def __init__(self):
        self.__root = tk.Tk()
        self.__bg_color = "#222222"
        self.requests_queue = []
        self.answer = None
        self.roomId = None
        self.username = None
        self.active = True

    def on_close(self):
        print("wiondow closed")
        self.clear_window()
        self.__root.destroy()
        self.destroy()
        self.active = False
        

    def start(self):
        height, width = (900, 1200)
        self.center_window(height, width)
        self.__root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.setup_mainMenu()
        # self.show_chat(chats)

        self.__root.mainloop()
        return

    def center_window(self, height, width):
        screen_width =  self.__root.winfo_screenwidth()
        screen_height =  self.__root.winfo_screenheight()

        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        self.__root.geometry(f'{width}x{height}+{x}+{y}')


    def clear_window(self):
        for widget in self.__root.winfo_children():
            widget.destroy()


    def roomJoin(self, host=False):
        def leave_room():
            request = f"EXIT+{self.roomId}+{self.username}"
            if host:
                request = f"CLSE+{self.roomId}"
            self.answer = None
            self.requests_queue.append(request)
            self.gameAbort = True
            


        def start_Game():
            btn.config(state="disabled")
            self.answer = None
            request = f"STRT+{self.roomId}"
            self.requests_queue.append(request)
            while not self.answer:
                time.sleep(0.1)
            
            msgCode = self.answer[:4]
            if msgCode == "CNFM":
                self.gamestarted = True
                self.suggestion = self.answer[4::]
                self.requests_queue.append("skip")
            else:
                btn.config(state="normal")
                messagebox.showerror("error", self.answer[4::])

            self.answer = None
            

        self.clear_window()

        players_lst = self.answer[4::]
        self.answer = None

        print(players_lst)

        players = players_lst.split("+")
        roomId = players[0]
        players = players[1::]

        roomId_label = tk.Label(self.__root, text=f"{roomId}'s room", font=("Arial", 50), bg=self.__bg_color, fg="white", pady=20)
        roomId_label.pack()

        for player in players:
            player_label = tk.Label(self.__root, text=f"{player}", font=("Arial", 30), bg=self.__bg_color, fg="white")
            player_label.pack(pady=10)

        if host:
            btn = tk.Button(self.__root, text="Start Game", command=start_Game, font=("Arial", 30))
            btn.pack(pady=30)
        
        self.requests_queue.append("skip")

        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "menu.png")

        original = Image.open(path)
        resized = original.resize((75, 75))  # Resize as needed
        self.__image = ImageTk.PhotoImage(resized)  # Store as self.image to prevent garbage collection

        image_button = tk.Button(self.__root, image=self.__image, command=leave_room)
        image_button.pack(anchor="sw", side="bottom")

        self.gamestarted = False
        self.gameAbort = False
        while not self.gamestarted and not self.gameAbort:
            time.sleep(0.2)
            self.requests_queue.append("skip")
            self.__root.update()
            if self.answer:
                return True
        
        return False
        
    #create a game lobby
    def createGame(self):
        self.requests_queue.clear()
        self.answer = None
        def createRoom():
            #send server create game request
            username = name.get()
            if not username:
                messagebox.showerror("error", "Please fill all the fileds")
                return
            
            request = f"CRTR+{username}"
            # print(request)
            self.answer = None
            self.requests_queue.append(request)

            while not self.answer:
                time.sleep(0.1)
            
            msgCode = self.answer[:4]
            print(msgCode)
            if msgCode == "EROR":
                messagebox.showerror("error", self.answer[4::])
                self.answer = None
                return
            else:
                self.roomId = username
                self.username = username
                print("CNFM")
                update = self.roomJoin(True)
                while update:
                    if self.answer == "KICK":
                        break
                    update = self.roomJoin(True)
                
                if self.gameAbort:
                    print("left room")
                    self.setup_mainMenu()
                if self.gamestarted:
                    print("game has started")
                    self.game_start(True)
                    return


                

        self.clear_window()
        title_label = tk.Label(self.__root, text="Create Game", font=("Arial", 50), bg=self.__bg_color, fg="white", pady=20)
        title_label.pack()

        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "menu.png")

        original = Image.open(path)
        resized = original.resize((75, 75))  # Resize as needed
        self.__image = ImageTk.PhotoImage(resized)  # Store as self.image to prevent garbage collection

        image_button = tk.Button(self.__root, image=self.__image, command=self.setup_mainMenu)
        image_button.pack(anchor="sw", side="bottom")

        options_frame = tk.Frame(self.__root, bg=self.__bg_color)
        options_frame.pack(pady=200)

        name_label = tk.Label(options_frame, text="Enter Name", font=("Arial", 30), bg=self.__bg_color, fg="white", pady=20)
        name_label.pack()
        name = tk.Entry(options_frame, font=("Arial", 30))
        name.pack()

        btn = tk.Button(options_frame, text="Create Game", command=createRoom, font=("Arial", 30))
        btn.pack(pady=30)


    def joinGame(self):
        self.requests_queue.clear()
        self.answer = None
        def joinRoom():
            username = name.get()
            id = roomId.get()
            if not username or not id:
                messagebox.showerror("error", "Please fill all the fileds")
                return
            
            self.answer = None
            request = f"JOIN+{id}+{username}"
            self.requests_queue.append(request)

            while not self.answer:
                time.sleep(0.1)

            msgCode = self.answer[:4]
            print(self.answer)
            if msgCode == "EROR":
                messagebox.showerror("error", self.answer[4::])
                self.answer = None
                return
            else:
                print("CNFM")
                self.roomId = id
                self.username = username
                update = self.roomJoin()
                while update:
                    time.sleep(0.1)
                    # print(self.answer)
                    if self.answer == "KICK":
                        self.gameAbort = True
                        break
                    if self.answer[:4] == "STRT":
                        self.gamestarted = True
                        self.suggestion = self.answer[4::]
                        self.answer = None
                        self.requests_queue.append("GSRT")
                        break
                    update = self.roomJoin()

                if self.gameAbort:
                    print("left room")
                    self.setup_mainMenu()
                if self.gamestarted:
                    print("game has started")
                    self.game_start()
                    return



        self.clear_window()
        title_label = tk.Label(self.__root, text="Join Game", font=("Arial", 50), bg=self.__bg_color, fg="white", pady=20)
        title_label.pack()

        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "menu.png")

        original = Image.open(path)
        resized = original.resize((75, 75))  # Resize as needed
        self.__image = ImageTk.PhotoImage(resized)  # Store as self.image to prevent garbage collection

        image_button = tk.Button(self.__root, image=self.__image, command=self.setup_mainMenu)
        image_button.pack(anchor="sw", side="bottom")

        options_frame = tk.Frame(self.__root, bg=self.__bg_color)
        options_frame.pack(pady=150)

        name_label = tk.Label(options_frame, text="Enter Name", font=("Arial", 30), bg=self.__bg_color, fg="white", pady=20)
        name_label.pack()
        name = tk.Entry(options_frame, font=("Arial", 30))
        name.pack()

        roomId_label = tk.Label(options_frame, text="Enter Room Id", font=("Arial", 30), bg=self.__bg_color, fg="white", pady=20)
        roomId_label.pack()
        roomId = tk.Entry(options_frame, font=("Arial", 30))
        roomId.pack()

        btn = tk.Button(options_frame, text="Join Game", command=joinRoom, font=("Arial", 30))
        btn.pack(pady=30)


    def setup_mainMenu(self):
        self.clear_window()

        self.__root.title("Gartic Phone")
        self.__root.configure(background=self.__bg_color)
        title_label = tk.Label(self.__root, text="Gartic Phone", font=("Arial", 50), bg=self.__bg_color, fg="white", pady=20)
        title_label.pack()

        options_frame = tk.Frame(self.__root, bg=self.__bg_color)
        options_frame.pack(pady=200)
        create_game = tk.Button(options_frame, text ="Create Game", command=self.createGame, fg=self.__bg_color, font=("Arial", 30), width=15)
        join_game = tk.Button(options_frame, text ="Join Game", command=self.joinGame, fg=self.__bg_color, font=("Arial", 30), width=15)
        create_game.pack(pady=20)
        join_game.pack()


    def image_to_draw(self):
        def submit():
            sentence_content = sentence.get()
            if not sentence_content:
                messagebox.showerror("EROR", "please send something")
                return
            
            # print(sentence_content)

            submit_btn.config(state='disabled')
            sentence.config(state='disabled')

            self.answer = None

            #send sentence
            request = f"SENT+{sentence_content}"
            self.requests_queue.append(request)

            self.sentence_to_draw()


        self.clear_window()
        if self.answer == "END":
            self.game_end()
            return
        
        img = self.answer

        if img == "ERR":
            print("somebody left")
            self.destroy()
            return

        self.__root.title("Gartic Phone")
        self.__root.configure(background=self.__bg_color)
        title_label = tk.Label(self.__root, text="Gartic Phone", font=("Arial", 40), bg=self.__bg_color, fg="white", pady=20)
        title_label.pack()

        paint_frame = tk.Frame(self.__root, bg=self.__bg_color)
        paint_frame.pack(pady=2)

        header_frame = tk.Frame(paint_frame, bg="#00BCD4")
        header_frame.pack()
        header = tk.Label(header_frame, text="Describe the scene!", font=("Arial", 20), bg="#00BCD4",fg="white", width=60)
        header.pack()

        image_frame = tk.Frame(paint_frame)
        image_frame.pack()
        #image
        img_stream = io.BytesIO(img)
        image = Image.open(img_stream)
        self.__image = ImageTk.PhotoImage(image)  # Store as self.image to prevent garbage collection

        image_display = tk.Label(image_frame, image=self.__image)
        image_display.pack()

        sentence = tk.Entry(image_frame, font=("Arial", 20), width=50)
        sentence.pack()

        submit_btn = tk.Button(paint_frame, text ="Submit Drawing", command=submit, fg=self.__bg_color, font=("Arial", 20), width=15)
        submit_btn.pack()

        # im = Image.open(io.BytesIO(img))
        # im.show()

    
    def sentence_to_draw(self):
        def submit():
            submit_drawing_btn.config(state="disabled")
            cnv.disable_draw()

            image = cnv.image
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_bytes = img_byte_arr.getvalue()
            self.answer = None
            self.requests_queue.append(f"IMG{base64.b64encode(img_bytes).decode('utf-8')}")

            while not self.answer:
                time.sleep(0.1)
                self.__root.update()
            
            
            self.image_to_draw()



        # if __name__ == "__main__":
        #     self.answer = "Pizza running from hambuerger"

        while not self.answer:
            time.sleep(0.1)
            self.__root.update()
        
        # if self.answer == "END":
        #     self.game_end()
        #     return

        # print(self.answer)
        sentence = self.answer

        if sentence == "ERR":
            print("somebody left")
            self.destroy()
            return

        self.clear_window()

        self.__root.title("Gartic Phone")
        self.__root.configure(background=self.__bg_color)
        title_label = tk.Label(self.__root, text="Gartic Phone", font=("Arial", 40), bg=self.__bg_color, fg="white", pady=20)
        title_label.pack()

        paint_frame = tk.Frame(self.__root, bg=self.__bg_color)
        paint_frame.pack(pady=2)

        header_frame = tk.Frame(paint_frame, bg="#00BCD4")
        header_frame.pack()
        header = tk.Label(header_frame, text="Draw the sentence!", font=("Arial", 20), bg="#00BCD4",fg="white", width=60)
        header.pack()
        sentence_label = tk.Label(header_frame, text=f"{sentence}", font=("Arial", 30), bg="#00BCD4",fg="white", width=43)
        sentence_label.pack()

        paint_ui_frame = tk.Frame(paint_frame)
        paint_ui_frame.pack()
        #canvas
        cnv = paint.PaintGUI(1000, 550, paint_frame)

        submit_drawing_btn = tk.Button(paint_frame, text ="Submit Drawing", command=submit, fg=self.__bg_color, font=("Arial", 20), width=15)
        submit_drawing_btn.pack()

    #game started:
    def game_start(self, host=False):
        self.clear_window()

        def send_sentence():
            sentence_content = sentence.get()
            if not sentence_content:
                sentence_content = placeholder
                sentence.insert(0, placeholder)

            print(sentence_content)

            submit.config(state='disabled')
            sentence.config(state='disabled')

            self.answer = None

            #send sentence
            request = f"SENT+{sentence_content}"
            self.requests_queue.append(request)

            self.sentence_to_draw()



        def on_entry_click(event):
            if sentence.get() == placeholder:
                sentence.delete(0, "end")  # delete all the text in the sentence
                sentence.config(fg='black')


        def on_focusout(event):
            if sentence.get() == '':
                sentence.insert(0, placeholder)
                sentence.config(fg='grey')


        if not host:
            while not self.answer:
                time.sleep(0.1)
                self.__root.update()
            
            if self.answer != "CNFM":
                print("EROR")
                return

        self.__root.configure(background=self.__bg_color)
        title_label = tk.Label(self.__root, text="Gartic Phone", font=("Arial", 50), bg=self.__bg_color, fg="white", pady=20)
        title_label.pack()
        
        placeholder = self.suggestion

        label = tk.Label(self.__root, text="Write a sentence", font=("Arial", 30), bg=self.__bg_color, fg="white", pady=20)
        label.pack()

        sentence = tk.Entry(self.__root, font=("Arial", 20), width=50, fg='grey')
        sentence.insert(0, placeholder)
        sentence.bind('<FocusIn>', on_entry_click)
        sentence.bind('<FocusOut>', on_focusout)
        sentence.pack()

        submit = tk.Button(self.__root, text ="Submit", command=send_sentence, fg=self.__bg_color, font=("Arial", 20))
        submit.pack()


    #game ended:
    def game_end(self):
        self.answer = None
        self.clear_window()
        self.requests_queue.append("obj")
        while not self.answer:
            time.sleep(0.1)
            self.__root.update()
        
        chats = pickle.loads(self.answer)

        # with open('data.pkl', 'wb') as f:
        #     pickle.dump(chats, f)
        
        self.show_chat(chats)

    
    def show_chat(self, chats):
        def move_chat(index):
            print(index)
            for i in range(len(self.chats)):
                self.btns[i].config(state='normal')
                self.chats[i].unpack()

            self.btns[index].config(state="disabled")
            self.chats[index].pack()

        self.btns = []
        self.chats = []
        for i in range(len(chats)):
            btn = tk.Button(self.__root, text=f"{chats[i][0]}'s chat", command=lambda i=i: move_chat(i))
            btn.pack(anchor="e", side="top")
            self.btns.append(btn)
            chat = Chat(self.__root, chats[i][0], chats[i][1])
            self.chats.append(chat)
    

    def destroy(self):
        del self
        return



class Chat:
    def __init__(self, root, host, msgs):
        self.root = root
        
        self.frame = ScrolledFrame(self.root, autohide=False, width=1000, height=800)

        text = tk.Label(self.frame, text=f"{host}'s chat", font= ('Helvetica bold', 14))
        text.pack(pady=20)


        self.photos_refrences = []
        for i in range(len(msgs)):
            if i % 2 == 0: #sentence
                sen = tk.Label(self.frame, text=f"{msgs[i]}", font= ('Helvetica bold', 14), bd=5, relief="solid")
                sen.pack(pady=5)
            else: #image
                image = Image.open(io.BytesIO(msgs[i]))
                new_size = (500, 500)  # for example 200x200 pixels
                image = image.resize(new_size, Image.LANCZOS)

                photo = ImageTk.PhotoImage(image)
                label = tk.Label(self.frame, image=photo, bd=5, relief="solid")
                label.pack(pady=5)
                self.photos_refrences.append(photo)


    def pack(self):
        self.frame.pack()


    def unpack(self):
        self.frame.pack_forget()




if __name__ == "__main__":
    with open('client\data.pkl', 'rb') as f:
        chats = pickle.load(f)
    x = GUI()
    x.start()