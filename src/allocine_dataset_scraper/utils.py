def read_file(filepath: str) -> str:
    with open(filepath, "r") as reader:
        return reader.read()
