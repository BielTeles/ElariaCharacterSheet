import PyPDF2
import os

class ElariaSystemPDFReader:
    """
    Classe para ler e extrair informações dos PDFs do sistema Elaria RPG.
    """
    
    def __init__(self):
        self.pdf_files = []
        self.current_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self._load_pdf_files()
        
    def _load_pdf_files(self):
        """Carrega os arquivos PDF do sistema encontrados no diretório."""
        for file in os.listdir(self.current_directory):
            if file.startswith("Elaria RPG") and file.endswith(".pdf"):
                self.pdf_files.append(os.path.join(self.current_directory, file))
                
    def extract_text_from_pdf(self, pdf_path):
        """
        Extrai o texto de um arquivo PDF específico.
        
        Args:
            pdf_path (str): Caminho para o arquivo PDF
            
        Returns:
            str: Texto extraído do PDF
        """
        try:
            with open(pdf_path, 'rb') as file:
                # Criar o leitor PDF
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Extrair texto de todas as páginas
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                    
                return text
        except Exception as e:
            print(f"Erro ao ler o PDF {pdf_path}: {str(e)}")
            return ""
            
    def extract_text_from_page(self, pdf_path, page_number):
        """
        Extrai o texto de uma página específica do PDF.
        
        Args:
            pdf_path (str): Caminho para o arquivo PDF
            page_number (int): Número da página (começando em 0)
            
        Returns:
            str: Texto extraído da página
        """
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                if page_number < len(pdf_reader.pages):
                    return pdf_reader.pages[page_number].extract_text()
                else:
                    print(f"Página {page_number} não existe no PDF {pdf_path}")
                    return ""
        except Exception as e:
            print(f"Erro ao ler a página {page_number} do PDF {pdf_path}: {str(e)}")
            return ""
            
    def get_pdf_info(self, pdf_path):
        """
        Obtém informações básicas sobre o PDF.
        
        Args:
            pdf_path (str): Caminho para o arquivo PDF
            
        Returns:
            dict: Dicionário com informações do PDF
        """
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                info = {
                    "Número de páginas": len(pdf_reader.pages),
                    "Informações do documento": pdf_reader.metadata
                }
                return info
        except Exception as e:
            print(f"Erro ao obter informações do PDF {pdf_path}: {str(e)}")
            return {}
            
    def search_text_in_pdfs(self, search_term):
        """
        Procura um termo em todos os PDFs carregados.
        
        Args:
            search_term (str): Termo a ser procurado
            
        Returns:
            dict: Dicionário com resultados da busca por arquivo
        """
        results = {}
        
        for pdf_path in self.pdf_files:
            try:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    
                    # Lista para armazenar páginas onde o termo foi encontrado
                    found_pages = []
                    
                    # Procurar em cada página
                    for page_num in range(len(pdf_reader.pages)):
                        text = pdf_reader.pages[page_num].extract_text().lower()
                        if search_term.lower() in text:
                            found_pages.append(page_num)
                    
                    if found_pages:
                        results[os.path.basename(pdf_path)] = found_pages
                        
            except Exception as e:
                print(f"Erro ao procurar no PDF {pdf_path}: {str(e)}")
                
        return results

if __name__ == "__main__":
    # Exemplo de uso
    pdf_reader = ElariaSystemPDFReader()
    
    # Listar PDFs encontrados
    print("PDFs encontrados:")
    for pdf in pdf_reader.pdf_files:
        print(f"- {os.path.basename(pdf)}")
        
    # Exemplo de busca
    if pdf_reader.pdf_files:
        primeiro_pdf = pdf_reader.pdf_files[0]
        
        # Obter informações do primeiro PDF
        info = pdf_reader.get_pdf_info(primeiro_pdf)
        print("\nInformações do primeiro PDF:")
        for key, value in info.items():
            print(f"{key}: {value}")
            
        # Buscar um termo específico
        termo_busca = "magia"
        print(f"\nBuscando termo '{termo_busca}' nos PDFs:")
        resultados = pdf_reader.search_text_in_pdfs(termo_busca)
        
        if resultados:
            for pdf_name, pages in resultados.items():
                print(f"\nEncontrado em {pdf_name} nas páginas: {pages}")
                
                # Exemplo: extrair texto da primeira página onde o termo foi encontrado
                if pages:
                    primeira_pagina = pages[0]
                    print(f"\nExemplo - Texto da página {primeira_pagina} de {pdf_name}:")
                    texto = pdf_reader.extract_text_from_page(
                        os.path.join(pdf_reader.current_directory, pdf_name),
                        primeira_pagina
                    )
                    print("-" * 80)
                    print(texto)
                    print("-" * 80)
                    break  # Mostrar apenas o primeiro exemplo
        else:
            print("Termo não encontrado em nenhum PDF.") 