import customtkinter as ctk

class NotesTab:
    def __init__(self, tab_widget):
        self.tab_widget = tab_widget

        # --- Frame Principal para a Aba de Notas ---
        # Usamos o próprio tab_widget como master direto para o Textbox
        # ou podemos adicionar um frame se quisermos padding ou outros elementos.
        # Vamos adicionar um frame para consistência e padding.
        self.main_frame = ctk.CTkFrame(self.tab_widget, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # --- Campo de Texto para Notas ---
        self.notes_textbox = ctk.CTkTextbox(
            master=self.main_frame,
            wrap="word", # Quebra de linha por palavra
            font=("Arial", 12) # Exemplo de fonte, pode ajustar
        )
        self.notes_textbox.pack(fill="both", expand=True)

        # Adicionar um texto inicial de placeholder, se desejar
        self.notes_textbox.insert("0.0", "Suas anotações da campanha aqui...\n\n- NPCs importantes\n- Lugares visitados\n- Pistas e Segredos\n- Objetivos da Aventura")