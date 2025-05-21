import customtkinter as ctk
from ui.app_ui import AppUI

class MainApplication:
    def __init__(self):
        # Configurações iniciais do CustomTkinter (tema, cor)
        ctk.set_appearance_mode("System")  # Pode ser "System", "Dark", "Light"
        ctk.set_default_color_theme("blue")  # Temas: "blue", "green", "dark-blue"

        self.root = ctk.CTk()
        self.app_ui = AppUI(self.root)
        self.root.mainloop()

if __name__ == "__main__":
    app = MainApplication()