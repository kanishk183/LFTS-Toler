import hashlib


def calculate_sha256(file_path):
    sha256_hash = hashlib.sha256()

    with open(file_path, "rb") as file:
        while chunk := file.read(4096):
            sha256_hash.update(chunk)

    return sha256_hash.hexdigest()


if __name__ == "__main__":
    test_file = "/home/kt_18/lfts-test-data/file1.txt"

    file_hash = calculate_sha256(test_file)

    print(file_hash)