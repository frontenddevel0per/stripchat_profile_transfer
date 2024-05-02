import customtkinter
from win10toast import ToastNotifier
import webbrowser
from PIL import Image
from datetime import datetime

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

app = customtkinter.CTk()
app.title("Stripchat Profile Transfer")
app.iconbitmap("icon.ico")
app.geometry("1280x720")
app.grid_columnconfigure(1, weight=1)
app.grid_rowconfigure(0, weight=1)

TG_IMAGE = customtkinter.CTkImage(
    light_image=Image.open("tg-logo.png"),
    dark_image=Image.open("tg-logo.png"),
    size=(40, 40),
)
GITHUB_IMAGE = customtkinter.CTkImage(
    light_image=Image.open("github-mark.png"),
    dark_image=Image.open("github-mark.png"),
    size=(40, 40),
)


def start_transition():
    if all(
        len(x) > 3
        for x in [
            login_source_entry.get(),
            password_source_entry.get(),
            login_reciever_entry.get(),
            password_reciever_entry.get(),
        ]
    ) and any(
        [
            info_switch.get() == "on",
            photos_switch.get() == "on",
            videos_switch.get() == "on",
            broadcast_switch.get() == "on",
        ]
    ):
        transition_config = {
            "my_info": (
                {
                    "main_bio": bio_checkbox.get() == "on",
                    "panels": panels_checkbox.get() == "on",
                    "background": background_checkbox.get() == "on",
                }
                if info_switch.get() == "on"
                and any(
                    [
                        bio_checkbox.get() == "on",
                        panels_checkbox.get() == "on",
                        background_checkbox.get() == "on",
                    ]
                )
                else False
            ),
            "photos": photos_switch.get() == "on",
            "videos": videos_switch.get() == "on",
            "broadcast_settings": (
                {
                    "show_activities": checkbox1.get() == "on",
                    "prices": checkbox2.get() == "on",
                    "cover_image": checkbox3.get() == "on",
                    "teaser_video": checkbox4.get() == "on",
                    "record_show": checkbox5.get() == "on",
                    "tip_menu": checkbox6.get() == "on",
                    "extensions": checkbox7.get() == "on",
                }
                if broadcast_switch.get() == "on"
                and any(
                    [
                        checkbox1.get() == "on",
                        checkbox2.get() == "on",
                        checkbox3.get() == "on",
                        checkbox4.get() == "on",
                        checkbox5.get() == "on",
                        checkbox6.get() == "on",
                        checkbox7.get() == "on",
                    ]
                )
                else False
            ),
        }

        print(transition_config)
        from copy_profile_min import ProfileTransfer

        newProfileTransfer = ProfileTransfer()
        output = newProfileTransfer.start_transfer(
            login_source_entry.get(),
            password_source_entry.get(),
            login_reciever_entry.get(),
            password_reciever_entry.get(),
            transition_config,
        )
        if output == "":
            toast = ToastNotifier()
            toast.show_toast(
                "Success",
                "Profile transition is done!",
                duration=20,
                threaded=True,
            )
        else:
            now_str = datetime.now().strftime("%d-%m-%Y %H-%M-%S")
            with open(f"Error {now_str}.txt", "w") as error_txt:
                error_txt.write(output)
            toast = ToastNotifier()
            toast.show_toast(
                "Error",
                "Error while transiting profile :(",
                duration=20,
                threaded=True,
            )
    else:
        print("Bad inputs, please fill them")


sidemenu_frame = customtkinter.CTkFrame(
    app, width=140, corner_radius=10, fg_color="#B0A5FF"
)  # C0B5FF
sidemenu_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
sidemenu_frame.grid_rowconfigure(1, weight=1)
main_frame = customtkinter.CTkFrame(
    app, width=1040, corner_radius=10, fg_color="#E0B5FF"
)
main_frame.grid(row=0, column=1, padx=(20, 0), pady=0, rowspan=1, sticky="nsew")
main_frame.grid_columnconfigure(3, weight=1)
main_frame.grid_rowconfigure((1, 2), weight=1)


def toggle_switch():
    if broadcast_var.get() == "on":
        checkbox1.grid(row=2, column=2, padx=(50, 20), pady=(10, 10), sticky="w")
        checkbox2.grid(row=3, column=2, padx=(50, 20), pady=(10, 10), sticky="w")
        checkbox3.grid(row=4, column=2, padx=(50, 20), pady=(10, 10), sticky="w")
        checkbox4.grid(row=5, column=2, padx=(50, 20), pady=(10, 10), sticky="w")
        checkbox5.grid(row=6, column=2, padx=(50, 20), pady=(10, 10), sticky="w")
        checkbox6.grid(row=7, column=2, padx=(50, 20), pady=(10, 10), sticky="w")
        checkbox7.grid(row=8, column=2, padx=(50, 20), pady=(10, 10), sticky="w")
    else:
        checkbox1.grid_forget()
        checkbox2.grid_forget()
        checkbox3.grid_forget()
        checkbox4.grid_forget()
        checkbox5.grid_forget()
        checkbox6.grid_forget()
        checkbox7.grid_forget()


def toggle_info():
    if info_var.get() == "on":
        bio_checkbox.grid(row=2, column=0, padx=(50, 20), pady=(10, 10), sticky="w")
        panels_checkbox.grid(row=3, column=0, padx=(50, 20), pady=(10, 10), sticky="w")
        background_checkbox.grid(
            row=4, column=0, padx=(50, 20), pady=(10, 10), sticky="w"
        )
    else:
        bio_checkbox.grid_forget()
        panels_checkbox.grid_forget()
        background_checkbox.grid_forget()


sidemenu_title = customtkinter.CTkLabel(
    sidemenu_frame,
    text="Profile Transfer",
    font=customtkinter.CTkFont(size=20, weight="bold", family="Comic Sans"),
)
sidemenu_title.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="nsew")
sidemenu_version = customtkinter.CTkLabel(
    sidemenu_frame,
    text="Version: v1.1",
    font=customtkinter.CTkFont(size=14, family="Comic Sans", weight="bold"),
    anchor="s",
)
sidemenu_version.grid(row=2, column=0, padx=20, pady=(20, 10))

buttons_frame = customtkinter.CTkFrame(
    sidemenu_frame, width=100, corner_radius=10, fg_color="#B0A5FF"
)
buttons_frame.grid(row=3, column=0, padx=20, pady=(20, 10), sticky="nsew")
telegram_button = customtkinter.CTkButton(
    buttons_frame,
    fg_color="transparent",
    image=TG_IMAGE,
    text="",
    width=50,
    height=50,
    command=lambda: webbrowser.open("https://t.me/frontenddevel0per"),
)
telegram_button.grid(row=0, column=0, sticky="nsew")
github_button = customtkinter.CTkButton(
    buttons_frame,
    fg_color="transparent",
    image=GITHUB_IMAGE,
    text="",
    width=50,
    height=50,
    command=lambda: webbrowser.open("https://github.com/frontenddevel0per"),
)
github_button.grid(row=0, column=1, padx=(20, 0), sticky="nsew")

"""SETTINGS FRAME"""
settings_label = customtkinter.CTkLabel(
    main_frame,
    text="Settings",
    font=customtkinter.CTkFont(size=20, weight="bold", family="Comic Sans"),
    anchor="n",
)
settings_label.grid(row=0, column=0, padx=20, pady=(20, 10), columnspan=3)

inputs_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
inputs_frame.grid(row=1, column=0, padx=50, sticky="n")

config_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
config_frame.grid(row=1, column=1, sticky="n")

from_where_label = customtkinter.CTkLabel(
    inputs_frame,
    text="Source account:",
    font=customtkinter.CTkFont(size=18, weight="bold", family="Comic Sans"),
    anchor="n",
)
from_where_label.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="w")
login_source_label = customtkinter.CTkLabel(
    inputs_frame,
    text="Login:",
    font=customtkinter.CTkFont(size=14, family="Comic Sans"),
    anchor="s",
)
login_source_label.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")
login_source_entry = customtkinter.CTkEntry(inputs_frame, placeholder_text="login")
login_source_entry.grid(row=2, column=0, padx=20, sticky="w")

password_source_label = customtkinter.CTkLabel(
    inputs_frame,
    text="Password:",
    font=customtkinter.CTkFont(size=14, family="Comic Sans"),
    anchor="s",
)
password_source_label.grid(row=3, column=0, padx=20, pady=(0, 10), sticky="w")
password_source_entry = customtkinter.CTkEntry(
    inputs_frame, placeholder_text="password"
)
password_source_entry.grid(row=4, column=0, padx=20, sticky="w")


where_to_insert_label = customtkinter.CTkLabel(
    inputs_frame,
    text="Reciever account:",
    font=customtkinter.CTkFont(size=18, weight="bold", family="Comic Sans"),
    anchor="n",
)
where_to_insert_label.grid(row=5, column=0, padx=20, pady=(30, 0), sticky="w")

login_reciever_label = customtkinter.CTkLabel(
    inputs_frame,
    text="Login:",
    font=customtkinter.CTkFont(size=14, family="Comic Sans"),
    anchor="s",
)
login_reciever_label.grid(row=6, column=0, padx=20, pady=(0, 10), sticky="w")
login_reciever_entry = customtkinter.CTkEntry(inputs_frame, placeholder_text="login")
login_reciever_entry.grid(row=7, column=0, padx=20, sticky="w")

password_reciever_label = customtkinter.CTkLabel(
    inputs_frame,
    text="Password:",
    font=customtkinter.CTkFont(size=14, family="Comic Sans"),
    anchor="s",
)
password_reciever_label.grid(row=8, column=0, padx=20, pady=(0, 10), sticky="w")
password_reciever_entry = customtkinter.CTkEntry(
    inputs_frame, placeholder_text="password"
)
password_reciever_entry.grid(row=9, column=0, padx=20, sticky="w")


Config_label = customtkinter.CTkLabel(
    config_frame,
    text="Config:",
    font=customtkinter.CTkFont(size=18, weight="bold", family="Comic Sans"),
    anchor="n",
)
Config_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

info_var = customtkinter.StringVar(value="on")
info_switch = customtkinter.CTkSwitch(
    config_frame,
    text="Info",
    variable=info_var,
    onvalue="on",
    offvalue="off",
    font=customtkinter.CTkFont(size=16, family="Comic Sans"),
    command=toggle_info,
)
info_switch.grid(row=1, column=0, padx=20, pady=(10, 10), sticky="w")
bio_var = customtkinter.StringVar(value="on")
bio_checkbox = customtkinter.CTkCheckBox(
    config_frame,
    text="Main bio",
    variable=bio_var,
    onvalue="on",
    offvalue="off",
)
bio_checkbox.grid(row=2, column=0, padx=(50, 20), pady=(10, 10), sticky="w")
panels_var = customtkinter.StringVar(value="on")
panels_checkbox = customtkinter.CTkCheckBox(
    config_frame,
    text="Panels",
    variable=panels_var,
    onvalue="on",
    offvalue="off",
)
panels_checkbox.grid(row=3, column=0, padx=(50, 20), pady=(10, 10), sticky="w")
background_var = customtkinter.StringVar(value="on")
background_checkbox = customtkinter.CTkCheckBox(
    config_frame,
    text="Background",
    variable=background_var,
    onvalue="on",
    offvalue="off",
)
background_checkbox.grid(row=4, column=0, padx=(50, 20), pady=(10, 10), sticky="w")
photos_var = customtkinter.StringVar(value="on")
photos_switch = customtkinter.CTkSwitch(
    config_frame,
    text="Photos",
    variable=photos_var,
    onvalue="on",
    offvalue="off",
    font=customtkinter.CTkFont(size=16, family="Comic Sans"),
)
photos_switch.grid(row=1, column=1, padx=20, pady=(10, 10), sticky="w")
videos_var = customtkinter.StringVar(value="on")
videos_switch = customtkinter.CTkSwitch(
    config_frame,
    text="Videos",
    variable=videos_var,
    onvalue="on",
    offvalue="off",
    font=customtkinter.CTkFont(size=16, family="Comic Sans"),
)
videos_switch.grid(row=2, column=1, padx=20, pady=(10, 10), sticky="w")
broadcast_var = customtkinter.StringVar(value="on")
broadcast_switch = customtkinter.CTkSwitch(
    config_frame,
    text="Broadcast settings",
    variable=broadcast_var,
    onvalue="on",
    offvalue="off",
    font=customtkinter.CTkFont(size=16, family="Comic Sans"),
    command=toggle_switch,
)
broadcast_switch.grid(row=1, column=2, padx=20, pady=(10, 10), sticky="w")

check_var1 = customtkinter.StringVar(value="on")
checkbox1 = customtkinter.CTkCheckBox(
    config_frame,
    text="Show activities",
    variable=check_var1,
    onvalue="on",
    offvalue="off",
)
checkbox1.grid(row=2, column=2, padx=(50, 20), pady=(10, 10), sticky="w")
check_var2 = customtkinter.StringVar(value="on")
checkbox2 = customtkinter.CTkCheckBox(
    config_frame, text="Prices", variable=check_var2, onvalue="on", offvalue="off"
)
checkbox2.grid(row=3, column=2, padx=(50, 20), pady=(10, 10), sticky="w")
check_var3 = customtkinter.StringVar(value="on")
checkbox3 = customtkinter.CTkCheckBox(
    config_frame, text="Cover Image", variable=check_var3, onvalue="on", offvalue="off"
)
checkbox3.grid(row=4, column=2, padx=(50, 20), pady=(10, 10), sticky="w")
check_var4 = customtkinter.StringVar(value="on")
checkbox4 = customtkinter.CTkCheckBox(
    config_frame, text="Teaser video", variable=check_var4, onvalue="on", offvalue="off"
)
checkbox4.grid(row=5, column=2, padx=(50, 20), pady=(10, 10), sticky="w")
check_var5 = customtkinter.StringVar(value="on")
checkbox5 = customtkinter.CTkCheckBox(
    config_frame, text="Record Show", variable=check_var5, onvalue="on", offvalue="off"
)
checkbox5.grid(row=6, column=2, padx=(50, 20), pady=(10, 10), sticky="w")
check_var6 = customtkinter.StringVar(value="on")
checkbox6 = customtkinter.CTkCheckBox(
    config_frame, text="Tip Menu", variable=check_var6, onvalue="on", offvalue="off"
)
checkbox6.grid(row=7, column=2, padx=(50, 20), pady=(10, 10), sticky="w")
check_var7 = customtkinter.StringVar(value="on")
checkbox7 = customtkinter.CTkCheckBox(
    config_frame, text="Extensions", variable=check_var7, onvalue="on", offvalue="off"
)
checkbox7.grid(row=8, column=2, padx=(50, 20), pady=(10, 10), sticky="w")

start_button = customtkinter.CTkButton(
    main_frame,
    text="Start transition",
    fg_color=("#A016FF", "#B448FF"),
    command=start_transition,
)
start_button.grid(
    row=2, column=0, columnspan=2, padx=(50, 20), pady=(10, 50), sticky="s"
)


app.mainloop()
