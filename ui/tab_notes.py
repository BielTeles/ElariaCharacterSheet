import customtkinter as ctk
from typing import Optional # Para o 'event=None'

# Import da classe Personagem para type hinting
# Não é estritamente necessário para a execução se o personagem
# for sempre passado corretamente, mas bom para clareza.
# from core.character import Personagem # Descomente se preferir import explícito

PLACEHOLDER_NOTAS = (
    "Suas anotações da campanha aqui...\n\n"
    "- NPCs importantes\n"
    "- Lugares visitados\n"
    "- Pistas e Segredos\n"
    "- Objetivos da Aventura"
)

class NotesTab:
    """
    Gerencia a aba de Anotações na interface do usuário.
    Permite ao usuário registrar e salvar notas de texto livre
    associadas ao personagem.
    """
    personagem: Any # Deveria ser 'Personagem', mas evitando import direto para simplicidade aqui
    notes_textbox: ctk.CTkTextbox

    def __init__(self, tab_widget: ctk.CTkFrame, personagem_atual: Any): # 'Any' para personagem_atual por ora
        self.tab_widget = tab_widget
        self.personagem = personagem_atual

        self.main_frame = ctk.CTkFrame(self.tab_widget, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.notes_textbox = ctk.CTkTextbox(
            master=self.main_frame,
            wrap="word",
            font=("Arial", 12)
        )
        self.notes_textbox.pack(fill="both", expand=True)

        # Carrega as notas do personagem ao iniciar a aba
        self.load_data_from_personagem()

        # Atualiza o objeto personagem quando o texto muda
        self.notes_textbox.bind("<KeyRelease>", self._update_personagem_notes)

    def load_data_from_personagem(self) -> None:
        """
        Carrega as notas do objeto Personagem para o CTkTextbox.
        Chamado quando a aba é inicializada ou quando uma nova ficha é carregada.
        """
        # Limpa o conteúdo atual do textbox
        self.notes_textbox.delete("0.0", "end")
        
        if hasattr(self.personagem, 'notas') and self.personagem.notas:
            self.notes_textbox.insert("0.0", self.personagem.notas)
        else:
            self.notes_textbox.insert("0.0", PLACEHOLDER_NOTAS)

    def _update_personagem_notes(self, event: Optional[Any] = None) -> None: # event é passado pelo bind
        """Atualiza o atributo 'notas' no objeto Personagem com o texto atual do CTkTextbox."""
        if hasattr(self.personagem, 'notas'):
            current_text = self.notes_textbox.get("0.0", "end-1c") # Pega todo o texto, menos o newline final
            if self.personagem.notas != current_text:
                self.personagem.notas = current_text
            # print(f"Personagem.notas atualizado.") # Para debug