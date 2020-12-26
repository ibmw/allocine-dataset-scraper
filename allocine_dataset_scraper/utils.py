def read_file(filepath):
    with open(filepath, "r") as reader:
        return reader.read()


def write_file(data, filepath):
    with open(filepath, "w") as writer:
        writer.write(data)
