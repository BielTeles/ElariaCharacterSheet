import customtkinter as ctk
from ui.app_ui import AppUI
import multiprocessing

class MainApplication:
    """
    Classe principal que inicializa e executa a interface gráfica da
    Ficha de Personagem Elaria RPG.
    """
    root: ctk.CTk
    app_ui: AppUI

    def __init__(self) -> None:
        # Configurações iniciais do CustomTkinter (tema, cor)
        ctk.set_appearance_mode("dark")  # Modo escuro por padrão
        ctk.set_default_color_theme("dark-blue")  # Tema base para o CustomTkinter

        self.root = ctk.CTk()
        self.app_ui = AppUI(self.root)
        self.root.mainloop()

if __name__ == "__main__":
    # Necessário para o multiprocessing no Windows
    multiprocessing.freeze_support()
    app = MainApplication()