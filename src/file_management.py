import os
import zipfile
import shutil

# Este módulo fornece a classe FileManager para manipulação de arquivos e pastas,
# incluindo compactação de diretórios em arquivos zip, listagem de subpastas e automação
# do processo de organização de arquivos gerados em extratos. Permite também deletar pastas
# originais após compactação, facilitando o gerenciamento dos dados processados.

class FileManager:
    @staticmethod
    def zip_folder(folder_path, zip_path, delete_original=False):
        """
        Compacta o conteúdo de uma pasta em um arquivo zip.

        :param folder_path: Caminho da pasta a ser compactada.
        :param zip_path: Caminho do arquivo zip de saída.
        :param delete_original: Se True, deleta a pasta original após compactar.
        """
        if os.path.exists(folder_path):
            os.makedirs(os.path.dirname(zip_path), exist_ok=True)
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, start=folder_path)
                        zipf.write(file_path, arcname)
            if delete_original:
                try:
                    shutil.rmtree(folder_path)
                except Exception as e:
                    raise Exception(f"Erro ao deletar a pasta original: {e}")
        else:
            raise Exception(f"Pasta não encontrada: {folder_path}")
    
    @staticmethod
    def zip_all_folders(folders_path, delete_original=False):
        folders_list = FileManager.list_folders(folders_path)
        for folder in folders_list:
            adms = FileManager.list_folders(f"{folders_path}\\{folder}\\Extratos de Cota Capital")
            for adm in adms:
                FileManager.zip_folder(
                    folder_path= f"{folders_path}\\{folder}\\Extratos de Cota Capital\\{adm}",
                    zip_path= f"{folders_path}\\{folder}\\Extratos de Cota Capital\\{adm}.zip",
                    delete_original= delete_original)

    @staticmethod
    def list_folders(folder):
        try:
            return [ name for name in os.listdir(folder) if os.path.isdir(os.path.join(folder, name)) ]
        except:
            return []

# if __name__ == "__main__":
#     load_dotenv()

#     FileManager.zip_all_folders(os.getenv("PATH_BASES"))