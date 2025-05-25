import customtkinter as ctk
from typing import List, Tuple

from core.dice_roller import roll_generic_dice # Importa a função do core

class DiceRollerGenericTab:
    """
    Gerencia a aba do Rolador de Dados Genérico, permitindo ao usuário
    rolar uma quantidade arbitrária de dados de um tipo específico.
    """
    num_dice_entry: ctk.CTkEntry
    dice_type_var: ctk.StringVar
    dice_type_menu: ctk.CTkOptionMenu
    roll_button: ctk.CTkButton
    result_text_individual: ctk.CTkLabel
    result_text_total: ctk.CTkLabel

    def __init__(self, tab_widget: ctk.CTkFrame):
        self.tab_widget = tab_widget

        # --- Frame Principal para a Aba ---
        self.main_frame = ctk.CTkFrame(self.tab_widget, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Frame para os inputs
        input_frame = ctk.CTkFrame(self.main_frame)
        input_frame.pack(pady=10)

        # Input para quantidade de dados
        num_dice_label = ctk.CTkLabel(master=input_frame, text="Qtd. Dados:")
        num_dice_label.pack(side="left", padx=(0,5), pady=5)
        self.num_dice_entry = ctk.CTkEntry(master=input_frame, width=50, placeholder_text="Ex: 3")
        # Poderia adicionar validação para permitir apenas números:
        # vcmd = (self.main_frame.register(self._validate_numeric_input), '%P')
        # self.num_dice_entry = ctk.CTkEntry(..., validate="key", validatecommand=vcmd)
        self.num_dice_entry.insert(0, "1") # Valor padrão
        self.num_dice_entry.pack(side="left", padx=(0,10), pady=5)

        # Separador "d"
        d_label = ctk.CTkLabel(master=input_frame, text="d")
        d_label.pack(side="left", padx=(0,5), pady=5)
        
        # Dropdown para tipo de dado
        dice_types: List[str] = ["4", "6", "8", "10", "12", "20", "100"]
        self.dice_type_var = ctk.StringVar(value="20") # Valor padrão d20
        self.dice_type_menu = ctk.CTkOptionMenu(master=input_frame, values=dice_types, variable=self.dice_type_var)
        self.dice_type_menu.pack(side="left", padx=(0,10), pady=5)

        # Botão para rolar
        self.roll_button = ctk.CTkButton(master=input_frame, text="Rolar!", command=self.perform_roll)
        self.roll_button.pack(side="left", padx=10, pady=5)

        # Frame para resultados
        result_frame = ctk.CTkFrame(self.main_frame)
        result_frame.pack(pady=10, fill="x")

        result_label_title = ctk.CTkLabel(master=result_frame, text="Resultado:", font=ctk.CTkFont(weight="bold"))
        result_label_title.pack(pady=(0,5))
        
        self.result_text_individual = ctk.CTkLabel(master=result_frame, text="Rolagens Individuais: N/A", justify="left", anchor="w")
        self.result_text_individual.pack(fill="x", padx=10)
        
        self.result_text_total = ctk.CTkLabel(master=result_frame, text="Soma Total: N/A", font=ctk.CTkFont(weight="bold"), justify="left", anchor="w")
        self.result_text_total.pack(fill="x", padx=10)

    # Função de validação opcional para o Entry (exemplo)
    # def _validate_numeric_input(self, P: str) -> bool:
    #     """Valida se a entrada é um número ou vazia."""
    #     if P == "" or P.isdigit():
    #         return True
    #     return False

    def perform_roll(self) -> None:
        """
        Executa a rolagem de dados com base nos valores da UI
        e atualiza os labels de resultado.
        """
        try:
            num_dice_str = self.num_dice_entry.get()
            dice_type_str = self.dice_type_var.get()

            if not num_dice_str.strip() or not dice_type_str.strip():
                self.result_text_individual.configure(text="Rolagens Individuais: Erro - campos vazios")
                self.result_text_total.configure(text="Soma Total: Erro")
                return

            num_dice = int(num_dice_str)
            dice_type = int(dice_type_str)

            if num_dice <= 0 or dice_type <= 0:
                self.result_text_individual.configure(text="Rolagens Individuais: Erro - valores devem ser positivos e maiores que zero")
                self.result_text_total.configure(text="Soma Total: Erro")
                return

            rolls, total_sum = roll_generic_dice(num_dice, dice_type)

            if not rolls and total_sum == 0 and num_dice > 0 : # Caso roll_generic_dice retorne inválido
                 self.result_text_individual.configure(text=f"Rolagens Individuais: Erro - dados inválidos ({num_dice}d{dice_type})")
                 self.result_text_total.configure(text="Soma Total: Erro")
                 return

            self.result_text_individual.configure(text=f"Rolagens Individuais: {', '.join(map(str, rolls))}")
            self.result_text_total.configure(text=f"Soma Total: {total_sum}")

        except ValueError:
            self.result_text_individual.configure(text="Rolagens Individuais: Erro - input inválido (use números inteiros)")
            self.result_text_total.configure(text="Soma Total: Erro")
        except Exception as e: # Captura genérica para outros erros inesperados
            self.result_text_individual.configure(text=f"Rolagens Individuais: Erro inesperado - {e}")
            self.result_text_total.configure(text="Soma Total: Erro")