import tkinter as tk
import cv2
from PIL import Image, ImageTk
import face_recognition
import numpy as np
import os
import pickle
from tkinter import ttk, simpledialog, messagebox
import logging
import webbrowser
from datetime import datetime,date
from openpyxl import load_workbook#
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

LARGEFONT = ("Helvetica", 16)

dbfile = open("face_encoding_data", "rb")
db = pickle.load(dbfile)
known_face_encodings, known_face_names = db
print(known_face_names)

def face_authenticate(ret, frame):
    global known_face_encodings, known_face_names
    face_locations = []
    face_encodings = []
    face_names = []

    if True:
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1])

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Not in class"
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]
            face_names.append(name)
    return face_names

class ThemedStyle(ttk.Style):
    def __init__(self):
        super().__init__()
        self.theme_use('vista')


class tkinterApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.style = ThemedStyle()
        container = ttk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        file_handler = logging.FileHandler('conference.log')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        self.frames = {}

        self.video_source = 0
        self.vid = cv2.VideoCapture(self.video_source)

        for F in (StartPage, RegisterPage, LogPage, FrontCameraPage, AttendancePage):
            frame = F(container, self, self.vid)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    def get_video_capture(self):
        return self.vid

class StartPage(tk.Frame):
    def __init__(self, parent, controller, vid):
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text="Welcome!", font=LARGEFONT, justify="center", background="gray95")
        label.pack(anchor="center", pady=10)

        button1 = ttk.Button(self, text="Register for Conference", command=lambda: self.go_to_register_page(controller))
        button1.pack(anchor="center", pady=10)

        button2 = ttk.Button(self, text="Attend Conference", command=lambda: self.go_to_front_camera_page(controller))
        button2.pack(anchor="center", pady=10)

        button3 = ttk.Button(self, text="Track Attendance", command=lambda: self.go_to_attendance_page(controller))
        button3.pack(anchor="center", pady=10)

        button3 = ttk.Button(self, text="Admin Logs", command=lambda: self.go_to_log_page(controller))
        button3.pack(anchor="center", pady=10)

    def go_to_register_page(self, controller):
        controller.show_frame(RegisterPage)
        controller.logger.info('Register for Conference page accessed.')

    def go_to_front_camera_page(self, controller):
        controller.show_frame(FrontCameraPage)
        controller.logger.info('Attend conference page accessed.')

    def go_to_log_page(self, controller):
        controller.show_frame(LogPage)
        controller.logger.info('Admin Logs page accessed.')

    def go_to_attendance_page(self, controller):
        controller.show_frame(AttendancePage)
        controller.logger.info('Track Attendance page accessed.')

class RegisterPage(tk.Frame):
    def __init__(self, parent, controller, vid):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label = ttk.Label(self, text="Register for Conference", font=LARGEFONT, anchor="center")
        label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        self.vid = vid

        self.cameraFrame = tk.Frame(self, bg="gray")
        self.cameraFrame.grid(row=1, column=0, columnspan=2, sticky="nsew")

        self.lmain = tk.Label(self.cameraFrame)
        self.lmain.grid(row=1, column=0, columnspan=2, sticky="nsew")

        self.variable = tk.StringVar()
        self.message = tk.Label(self, textvariable=self.variable, fg="green")
        self.message.grid(row=2, columnspan=2)

        self.waring_var = tk.StringVar()
        self.waring = tk.Label(self, textvariable=self.waring_var, fg="red")
        self.waring.grid(row=3, columnspan=2)

        ttk.Label(self, text="User ID").grid(row=4, column=0)
        self.id_entry = ttk.Entry(self)
        self.id_entry.grid(row=4, column=1)

        ttk.Label(self, text="First Name").grid(row=5, column=0)
        self.name_entry = ttk.Entry(self)
        self.name_entry.grid(row=5, column=1)

        ttk.Label(self, text="Last Name").grid(row=6, column=0)
        self.lastname_entry = ttk.Entry(self)
        self.lastname_entry.grid(row=6, column=1)

        self.capture_button = ttk.Button(self, text="Register", command=self.capture_frame)
        self.capture_button.grid(row=7, column=0, columnspan=2)

        button2 = ttk.Button(self, text="Home Page", command=lambda: self.go_to_home_page(controller))
        button2.grid(row=8, column=0, columnspan=2, pady=10)

        self.is_capturing = False  # Flag to indicate capturing

        self.start_capture()

    def go_to_home_page(self, controller):
        controller.show_frame(StartPage)

    def update_warning(self, label):
        self.waring_var.set(label)

    def start_capture(self):
        self.capture = self.after(10, self.update)

    def is_camera_in_use(self):
        try:
            cap = self.vid
            if not cap.isOpened():
                return True
            ret, frame = cap.read()
            if not ret:
                return True
        except cv2.error:
            return True
        return False

    def capture_frame(self):
        self.update_label("")
        self.update_warning("")
        ret, frame = self.vid.read()
        if not self.is_camera_in_use():
            self.controller.logger.info('Camera initialised.')
        else:
            self.controller.logger.info('Camera initialisation failed.')
        if ret:
            id_text = self.id_entry.get()
            name_text = self.name_entry.get()
            lastname_text = self.lastname_entry.get()

            if id_text == "":
                self.update_warning("User ID Empty")
                self.controller.logger.info('User ID Empty')
            elif name_text == "":
                self.update_warning("First Name Empty")
                self.controller.logger.info('First Name Empty')
            elif lastname_text == "":
                self.update_warning("Last Name Empty")
                self.controller.logger.info('Last Name Empty')
            else:
                path = "images/"
                paths = path + id_text + "/"
                filename = f"{id_text}_{name_text}_{lastname_text}.png"

                if os.path.exists(paths):
                    self.update_warning("User already exists")
                    self.controller.logger.info(f'{id_text} User already exists')
                else:
                    try:
                        os.makedirs(paths)
                        print(f"Folder '{paths}' created successfully.")
                    except OSError as e:
                        print(f"Failed to create folder '{paths}': {e}")

                    cv2.imwrite(paths + filename, frame)
                    self.controller.logger.info(f'{name_text} with {id_text} has registered.')
                    print(f"Frame Captured and Saved as: {filename}")
                    self.update_label("Registration Successful")
                    self.id_entry.delete(0, tk.END)
                    self.name_entry.delete(0, tk.END)
                    self.lastname_entry.delete(0, tk.END)

    def update(self):
        ret, frame = self.vid.read()
        if ret:
            frame = cv2.flip(frame, 1)
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            img = Image.fromarray(cv2image)
            self.imgtk = ImageTk.PhotoImage(image=img)
            self.lmain.configure(image=self.imgtk)
        self.capture = self.after(10, self.update)

    def update_label(self, label):
        self.variable.set(label)

    def convert_to_tkinter_image(self, frame):
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        photo = ImageTk.PhotoImage(image=image)
        return photo

    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()


class FrontCameraPage(tk.Frame):
    def __init__(self, parent, controller, vid):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = ttk.Label(self, text="Authenticate", font=LARGEFONT, justify="center")
        label.pack(anchor="center", pady=10)

        self.vid = vid

        self.cameraFrame = tk.Frame(self, background="gray")
        self.cameraFrame.pack()

        self.buttonFrame = tk.Frame(self, background="white")
        self.buttonFrame.pack(pady=10)

        self.capture = None
        self.lmain = ttk.Label(self.cameraFrame)
        self.lmain.pack()

        self.var = tk.StringVar()
        self.warning = ttk.Label(self, textvariable=self.var, foreground="red")
        self.warning.pack(pady=10)

        self.btn_snapshot = ttk.Button(self, text="Authenticate", command=self.authenticate)
        self.btn_snapshot.pack(pady=10)

        button2 = ttk.Button(self, text="Home Page", command=lambda: self.go_to_home_page(controller))
        button2.pack(pady=10)

        self.update()

    def go_to_home_page(self, controller):
        controller.show_frame(StartPage)

    def is_camera_in_use(self):
        try:
            cap = self.vid
            if not cap.isOpened():
                return True
            ret, frame = cap.read()
            # cap.release()
            if not ret:
                return True
        except cv2.error:
            return True
        return False

    def authenticate(self):
        ret, frame = self.vid.read()
        if not self.is_camera_in_use():
            self.controller.logger.info('Camera initialised.')
        else:
            self.controller.logger.info('Camera initialisation failed.')
        if ret:
            face_list = face_authenticate(ret, frame)
            print(face_list)

            if len(face_list) > 1:
                self.update_label(
                    "Authentication Failed : Multiple faces detected, Please try again!")
                self.controller.logger.info('More than 1 person has tried to authenticate.')
            elif len(face_list) == 0:
                self.update_label("Authentication Failed : No face detected, Please try again!")
                self.controller.logger.info('No face detected')
            else:
                if face_list[0] != "Not in class":
                    name=os.listdir(f"images/{face_list[0]}/")[0]
                    name=os.path.splitext(os.path.basename(name))[0]
                    workbook = load_workbook('Track_Conference_attendees.xlsx')
                    sheet = workbook.active
                    data = [[date.today(),datetime.now().time().strftime("%H:%M:%S"),face_list[0]
                             ,name.split("_")[1],name.split("_")[2]]]

                    for row in data:
                        sheet.append(row)

                    workbook.save('Track_Conference_attendees.xlsx')
                    webbrowser.open('https://meet.google.com/ndv-bmhg-qrh/', new=2)
                    self.controller.show_frame(StartPage)
                    self.vid.release()
                    self.controller.logger.info(f'{face_list[0]} has joined the conference.')
                else:
                    self.update_label("Authentication Failed : Unregistered Attendee, Please register!")
                    self.controller.logger.info('Unregistered Attendee tried to authenticate.')

    def update(self):
        ret, frame = self.vid.read()
        if ret:
            frame = cv2.flip(frame, 1)
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            img = Image.fromarray(cv2image)
            self.imgtk = ImageTk.PhotoImage(image=img)
            self.lmain.configure(image=self.imgtk)
        self.capture = self.after(10, self.update)

    def update_label(self, label):
        self.var.set(label)

    def convert_to_tkinter_image(self, frame):
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        photo = ImageTk.PhotoImage(image=image)
        return photo

    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()


class LogPage(tk.Frame):
    def __init__(self, parent, controller, vid):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label = ttk.Label(self, text="Log File of Conference", font=LARGEFONT, justify="center")
        label.pack(anchor="center", pady=10)

        log_button = ttk.Button(self, text="View Log", command=self.check_passcode)
        log_button.pack(pady=10)

        button2 = ttk.Button(self, text="Home Page", command=lambda: self.go_to_home_page(controller))
        button2.pack(pady=10)

    def go_to_home_page(self, controller):
        controller.show_frame(StartPage)

    def check_passcode(self):
        passcode = simpledialog.askstring("Passcode", "Enter Passcode", show='*')
        if passcode == '3839':  # Replace 'your_passcode_here' with the actual passcode
            self.open_log_file()
        elif passcode is not None:
            self.controller.logger.info("Incorrect passcode entered.")
            messagebox.showerror("Invalid Passcode", "Incorrect passcode entered.")

    def open_log_file(self):
        webbrowser.open('conference.log')

class AttendancePage(tk.Frame):
    def __init__(self, parent, controller, vid):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label = ttk.Label(self, text="Attendance", font=LARGEFONT, justify="center")
        label.pack(anchor="center", pady=10)

        log_button = ttk.Button(self, text="Get Attendance", command=self.check_passcode)
        log_button.pack(pady=10)

        button2 = ttk.Button(self, text="Home Page", command=lambda: self.go_to_home_page(controller))
        button2.pack(pady=10)

    def go_to_home_page(self, controller):
        controller.show_frame(StartPage)

    def check_passcode(self):
        passcode = simpledialog.askstring("Passcode", "Enter Passcode", show='*')
        if passcode == '3839':  # Replace 'your_passcode_here' with the actual passcode
            email=simpledialog.askstring("Email", "Enter Email")
            if email is not None: self.send_email(email)
        elif passcode is not None:
            self.controller.logger.info("Incorrect passcode entered.")
            messagebox.showerror("Invalid Passcode", "Incorrect passcode entered.")

    def send_email(self,email):
        sender_email = 'securefaceconnect@gmail.com' # Use your email
        receiver_email = email
        subject = 'Attendance List'
        body = 'Please find the below attachment for the list of attendees till now.'

        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = receiver_email
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))

        filename = 'Track_Conference_attendees.xlsx'
        attachment = open('Track_Conference_attendees.xlsx', 'rb')
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename= {filename}')
        message.attach(part)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, 'nhxu bvaw fvox cmxe')  # Use your email app password

        server.sendmail(sender_email, receiver_email, message.as_string())
        server.quit()
        self.controller.logger.info(f"Email sent to {email}")
        messagebox.showinfo("Email","Email Sent!")

app = tkinterApp()
app.title("SecureFace Connect")
app.mainloop()
