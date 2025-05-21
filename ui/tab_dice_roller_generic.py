import customtkinter as ctk
from core.dice_roller import roll_generic_dice # Importa a nova função

class DiceRollerGenericTab:
    def __init__(self, tab_widget):
        self.tab_widget = tab_widget

        # --- Frame Principal para a Aba ---
        self.main_frame = ctk.CTkFrame(self.tab_widget, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Frame para os inputs
        input_frame = ctk.CTkFrame(self.main_frame)
        input_frame.pack(pady=10)

        # Input para quantidade de dados
        self.num_dice_label = ctk.CTkLabel(master=input_frame, text="Qtd. Dados:")
        self.num_dice_label.pack(side="left", padx=(0,5), pady=5)
        self.num_dice_entry = ctk.CTkEntry(master=input_frame, width=50, placeholder_text="Ex: 3")
        self.num_dice_entry.insert(0, "1") # Valor padrão
        self.num_dice_entry.pack(side="left", padx=(0,10), pady=5)

        # Separador "d"
        self.d_label = ctk.CTkLabel(master=input_frame, text="d")
        self.d_label.pack(side="left", padx=(0,5), pady=5)
        
        # Dropdown para tipo de dado
        dice_types = ["4", "6", "8", "10", "12", "20", "100"]
        self.dice_type_var = ctk.StringVar(value="20") # Valor padrão d20
        self.dice_type_menu = ctk.CTkOptionMenu(master=input_frame, values=dice_types, variable=self.dice_type_var)
        self.dice_type_menu.pack(side="left", padx=(0,10), pady=5)

        # Botão para rolar
        self.roll_button = ctk.CTkButton(master=input_frame, text="Rolar!", command=self.perform_roll)
        self.roll_button.pack(side="left", padx=10, pady=5)

        # Frame para resultados
        result_frame = ctk.CTkFrame(self.main_frame)
        result_frame.pack(pady=10, fill="x")

        self.result_label_title = ctk.CTkLabel(master=result_frame, text="Resultado:", font=ctk.CTkFont(weight="bold"))
        self.result_label_title.pack(pady=(0,5))
        
        self.result_text_individual = ctk.CTkLabel(master=result_frame, text="Rolagens Individuais: N/A", justify="left", anchor="w")
        self.result_text_individual.pack(fill="x", padx=10)
        
        self.result_text_total = ctk.CTkLabel(master=result_frame, text="Soma Total: N/A", font=ctk.CTkFont(weight="bold"), justify="left", anchor="w")
        self.result_text_total.pack(fill="x", padx=10)

    def perform_roll(self):
        try:
            num_dice_str = self.num_dice_entry.get()
            dice_type_str = self.dice_type_var.get()

            if not num_dice_str or not dice_type_str: # Checagem simples de campos vazios
                self.result_text_individual.configure(text="Rolagens Individuais: Erro - campos vazios")
                self.result_text_total.configure(text="Soma Total: Erro")
                return

            num_dice = int(num_dice_str)
            dice_type = int(dice_type_str)

            if num_dice <= 0 or dice_type <= 0:
                self.result_text_individual.configure(text="Rolagens Individuais: Erro - valores devem ser positivos")
                self.result_text_total.configure(text="Soma Total: Erro")
                return

            rolls, total_sum = roll_generic_dice(num_dice, dice_type)

            self.result_text_individual.configure(text=f"Rolagens Individuais: {', '.join(map(str, rolls))}")
            self.result_text_total.configure(text=f"Soma Total: {total_sum}")

        except ValueError:
            self.result_text_individual.configure(text="Rolagens Individuais: Erro - input inválido (use números)")
            self.result_text_total.configure(text="Soma Total: Erro")
        except Exception as e: # Captura genérica para outros erros inesperados
            self.result_text_individual.configure(text=f"Rolagens Individuais: Erro - {e}")
            self.result_text_total.configure(text="Soma Total: Erro")