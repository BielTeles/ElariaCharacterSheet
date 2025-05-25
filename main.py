import customtkinter as ctk
from ui.app_ui import AppUI
import multiprocessing # Importa o módulo multiprocessing

class MainApplication:
    """
    Classe principal que inicializa e executa a interface gráfica da
    Ficha de Personagem Elaria RPG.
    """
    root: ctk.CTk
    app_ui: AppUI

    def __init__(self) -> None:
        # Configurações iniciais do CustomTkinter (tema, cor)
        ctk.set_appearance_mode("System")  # Pode ser "System", "Dark", "Light"
        ctk.set_default_color_theme("blue")  # Temas: "blue", "green", "dark-blue"

        self.root = ctk.CTk()
        self.app_ui = AppUI(self.root)
        self.root.mainloop()

if __name__ == "__main__":
    # Adiciona freeze_support() para compatibilidade com PyInstaller,
    # especialmente no Windows, caso o código ou dependências usem multiprocessing.
    multiprocessing.freeze_support()
    
    app = MainApplication()