import os


class File:
    def __init__(self, filename):
        self.filename = filename

    def read(self):
        with open(self.filename, 'r') as file:
            return file.read()

    def add(self, text):
        with open(self.filename, 'a') as file:
            file.write(text)
            file.close()

    def create(self):
        open(self.filename, 'w')


class FileManager:
    @staticmethod
    def create_file(filename):
        with open(filename, 'w') as file:
            file.write('')
            file.close()

    @staticmethod
    def add(filename, text):
        with open(filename, 'a') as file:
            file.write(text)
            file.close()

    @staticmethod
    def rewrite(filename, text):
        with open(filename, 'w') as file:
            file.write(text)
            file.close()

    @classmethod
    def rename(cls, old_name, new_name):
        with open(old_name, 'r') as file:
            content = file.read()
            file.close()

        cls.create_file(new_name)
        cls.add(new_name, content)

        os.remove(old_name)

    @staticmethod
    def read(filename):
        with open(filename, 'r') as file:
            return file.read()

    @staticmethod
    def check_instance(filename):
        return os.path.exists(filename)
