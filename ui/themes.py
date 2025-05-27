import json
from typing import Dict, Any
import os

# Temas predefinidos
THEME_DARK = {
    "name": "Dark",
    "colors": {
        "primary": "#3498db",      # Azul
        "secondary": "#2ecc71",    # Verde
        "danger": "#e74c3c",       # Vermelho
        "warning": "#f1c40f",      # Amarelo
        "info": "#3498db",         # Azul
        "success": "#2ecc71",      # Verde
        "background": "#2c3e50",   # Azul escuro
        "surface": "#34495e",      # Azul acinzentado
        "text": "#ecf0f1",         # Branco acinzentado
        "text_secondary": "#95a5a6" # Cinza claro
    }
}

THEME_LIGHT = {
    "name": "Light",
    "colors": {
        "primary": "#2980b9",      # Azul mais escuro
        "secondary": "#27ae60",    # Verde mais escuro
        "danger": "#c0392b",       # Vermelho mais escuro
        "warning": "#f39c12",      # Laranja
        "info": "#2980b9",         # Azul mais escuro
        "success": "#27ae60",      # Verde mais escuro
        "background": "#ecf0f1",   # Branco acinzentado
        "surface": "#bdc3c7",      # Cinza claro
        "text": "#2c3e50",         # Azul muito escuro
        "text_secondary": "#7f8c8d" # Cinza médio
    }
}

THEME_ELARIA = {
    "name": "Elaria",
    "colors": {
        "primary": "#8e44ad",      # Roxo
        "secondary": "#16a085",    # Verde água
        "danger": "#c0392b",       # Vermelho escuro
        "warning": "#d35400",      # Laranja escuro
        "info": "#2980b9",         # Azul escuro
        "success": "#27ae60",      # Verde escuro
        "background": "#2c3e50",   # Azul muito escuro
        "surface": "#34495e",      # Azul acinzentado escuro
        "text": "#ecf0f1",         # Branco acinzentado
        "text_secondary": "#95a5a6" # Cinza claro
    }
}

THEME_MYSTIC = {
    "name": "Mystic",
    "colors": {
        "primary": "#9b59b6",      # Roxo
        "secondary": "#1abc9c",    # Verde água
        "danger": "#e74c3c",       # Vermelho
        "warning": "#e67e22",      # Laranja
        "info": "#3498db",         # Azul
        "success": "#2ecc71",      # Verde
        "background": "#34495e",   # Azul escuro
        "surface": "#2c3e50",      # Azul muito escuro
        "text": "#ecf0f1",         # Branco acinzentado
        "text_secondary": "#bdc3c7" # Cinza claro
    }
}

# Dicionário com todos os temas disponíveis
AVAILABLE_THEMES = {
    "dark": THEME_DARK,
    "light": THEME_LIGHT,
    "elaria": THEME_ELARIA,
    "mystic": THEME_MYSTIC
}

class ThemeManager:
    """Gerenciador de temas do aplicativo."""
    
    def __init__(self):
        self.current_theme = "dark"
        self.themes = AVAILABLE_THEMES
        self._load_custom_themes()
    
    def _load_custom_themes(self) -> None:
        """Carrega temas customizados do diretório de temas."""
        themes_dir = "themes"
        if not os.path.exists(themes_dir):
            os.makedirs(themes_dir)
        
        for filename in os.listdir(themes_dir):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(themes_dir, filename), "r", encoding="utf-8") as f:
                        theme_data = json.load(f)
                        theme_name = os.path.splitext(filename)[0]
                        if self._validate_theme(theme_data):
                            self.themes[theme_name] = theme_data
                except Exception as e:
                    print(f"Erro ao carregar tema {filename}: {e}")
    
    def _validate_theme(self, theme_data: Dict[str, Any]) -> bool:
        """Valida se um tema tem todas as cores necessárias."""
        required_colors = set(THEME_DARK["colors"].keys())
        if not isinstance(theme_data, dict) or "colors" not in theme_data:
            return False
        theme_colors = set(theme_data["colors"].keys())
        return required_colors.issubset(theme_colors)
    
    def get_theme(self, theme_name: str = None) -> Dict[str, Any]:
        """Retorna o tema especificado ou o tema atual."""
        if theme_name is None:
            theme_name = self.current_theme
        return self.themes.get(theme_name, THEME_DARK)
    
    def set_theme(self, theme_name: str) -> bool:
        """Define o tema atual."""
        if theme_name in self.themes:
            self.current_theme = theme_name
            return True
        return False
    
    def save_custom_theme(self, theme_name: str, theme_data: Dict[str, Any]) -> bool:
        """Salva um tema customizado."""
        if not self._validate_theme(theme_data):
            return False
        
        themes_dir = "themes"
        if not os.path.exists(themes_dir):
            os.makedirs(themes_dir)
        
        try:
            with open(os.path.join(themes_dir, f"{theme_name}.json"), "w", encoding="utf-8") as f:
                json.dump(theme_data, f, indent=4)
            self.themes[theme_name] = theme_data
            return True
        except Exception as e:
            print(f"Erro ao salvar tema {theme_name}: {e}")
            return False
    
    def get_available_themes(self) -> Dict[str, str]:
        """Retorna um dicionário com os nomes dos temas disponíveis."""
        return {name: theme.get("name", name) for name, theme in self.themes.items()} 