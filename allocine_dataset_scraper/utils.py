def read_file(filepath: str) -> str:
    with open(filepath, "r") as reader:
        return reader.read()


def write_file(data: str, filepath: str):
    with open(filepath, "w") as writer:
        writer.write(data)
