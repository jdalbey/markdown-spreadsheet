
class FileReader:
    def read_file(self, file_path: str) -> str:
        # Logic to read the file
        if file_path:
            try:
                with open(file_path, "r") as file:
                    return file.read()
            except Exception as e:
                print ("Error", f"Failed to open file: {e}")

