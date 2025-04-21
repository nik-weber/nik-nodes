import os

class VideoPicker:
    # Variável de classe para armazenar o índice atual entre execuções
    current_index = 1  

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "directory_path": ("STRING", {"default": ""}),
                "video_number": ("INT", {"default": 1, "min": 1}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")  # Dois outputs: caminho e nome do arquivo
    RETURN_NAMES = ("file_path", "file_name")  # Nomes dos outputs
    FUNCTION = "load_video"
    CATEGORY = "N!K Nodes"

    def load_video(self, directory_path, video_number):
        if not directory_path:
            raise ValueError("O caminho da pasta não foi fornecido.")

        # Coleta e ordena os arquivos MP4 em ordem alfabética
        file_paths = self.crawl_directories(directory_path)
        file_paths.sort(key=lambda x: os.path.basename(x).lower())

        total_files = len(file_paths)
        if total_files == 0:
            raise ValueError("Nenhum arquivo MP4 encontrado na pasta especificada.")

        # Verifica se o número do vídeo é válido (seed 0 não tem correspondência)
        if video_number < 1 or video_number > total_files:
            raise ValueError(f"Vídeo {video_number} não corresponde a nenhum arquivo disponível.")

        # Obtém o caminho completo e o nome do arquivo sem a extensão
        selected_file = file_paths[video_number - 1]
        file_name = os.path.splitext(os.path.basename(selected_file))[0]

        # Retorna ambos: caminho completo e nome do arquivo sem extensão
        return (selected_file, file_name)

    def crawl_directories(self, directory):
        supported_format = "mp4"
        file_paths = []

        # Caminha pela pasta e subpastas para encontrar arquivos MP4
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(supported_format):
                    full_path = os.path.join(root, file)
                    file_paths.append(full_path)

        return file_paths
