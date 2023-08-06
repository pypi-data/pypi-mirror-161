from Crypto.Hash import keccak


def label_from_name(name: str):
    return name.split(".")[0]


def labelhash(label: str):
    keccak = keccak256(label)
    return "0x" + keccak


def token_id_from_labelhash(labelhash: str):
    return str(int(labelhash, 16))


def labelhash_from_token_id(token_id: str):
    labelhash = hex(int(token_id))[2:]
    padded_labelhash = labelhash.rjust(64, "0")
    return "0x" + padded_labelhash


def namehash(name: str):
    node = "0000000000000000000000000000000000000000000000000000000000000000"
    labelhashes = list(map(labelhash, name.split(".")))
    print(labelhashes)
    for _, label in enumerate(reversed(labelhashes)):
        node = keccak256(bytes.fromhex(node + label[2:]))

    return "0x" + node


def str_to_bin(str):
    return str.encode("ascii")


def keccak256(data):
    keccak_hash = keccak.new(digest_bits=256)
    if type(data) == str:
        data = str_to_bin(data)
    keccak_hash.update(data)
    return keccak_hash.hexdigest()
