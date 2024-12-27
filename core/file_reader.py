
class FileReader:
    def read_file(self, file_path: str) -> list:
        # Logic to read and parse the file
        if file_path:
            try:
                with open(file_path, "r") as file:
                    return file.readlines()
            except Exception as e:
                print ("Error", f"Failed to open file: {e}")

