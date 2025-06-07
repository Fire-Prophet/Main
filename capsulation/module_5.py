import os

class FileSystemManager:
    def list_directory_contents(self, path='.'):
        return os.listdir(path)

    def create_directory(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
            return True
        return False
