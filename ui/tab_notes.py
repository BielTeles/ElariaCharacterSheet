import customtkinter as ctk

class NotesTab:
    def __init__(self, tab_widget, personagem_atual): # Adicionado personagem_atual
        self.tab_widget = tab_widget
        self.personagem = personagem_atual # Guarda a referência

        self.main_frame = ctk.CTkFrame(self.tab_widget, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.notes_textbox = ctk.CTkTextbox(
            master=self.main_frame,
            wrap="word", 
            font=("Arial", 12) 
        )
        self.notes_textbox.pack(fill="both", expand=True)

        # Carrega as notas do personagem ao iniciar
        if hasattr(self.personagem, 'notas'):
            self.notes_textbox.insert("0.0", self.personagem.notas if self.personagem.notas else "Suas anotações da campanha aqui...\n\n- NPCs importantes\n- Lugares visitados\n- Pistas e Segredos\n- Objetivos da Aventura")
        else:
             self.notes_textbox.insert("0.0", "Suas anotações da campanha aqui...\n\n- NPCs importantes\n- Lugares visitados\n- Pistas e Segredos\n- Objetivos da Aventura")


        # Atualiza o objeto personagem quando o texto muda
        # O evento <KeyRelease> é disparado toda vez que uma tecla é solta
        self.notes_textbox.bind("<KeyRelease>", self._update_personagem_notes)

    def _update_personagem_notes(self, event=None): # event é passado pelo bind
        """Atualiza o atributo 'notas' no objeto Personagem."""
        current_text = self.notes_textbox.get("0.0", "end-1c") # Pega todo o texto, menos o newline final
        self.personagem.notas = current_text
        # print(f"Personagem.notas atualizado.") # Para debug