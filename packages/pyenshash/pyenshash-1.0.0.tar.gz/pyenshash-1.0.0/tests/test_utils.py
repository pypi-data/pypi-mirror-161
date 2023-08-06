from pyenshash import utils

namehashes = {
    "doge.eth": "0xfe94b0062af588710195999f20198adf2ec594f7df73306b225963575c95ec9e",
    "vitalik.eth": "0xee6c4522aab0003e8d14cd40a6af439055fd2577951148c14b6cea9a53475835",
    "hello.eth": "0x810b85f0418528b1ba4aa88307c7a24bc2409b383186b78f8ceabf59d9073845",
    "namehash.eth": "0xb77df99501b1a61ba48c3363d91305ffc66af627a77efca2fa2bf7b66e04babd",
    "test.doge.eth": "0x8213e77d0f33097e92c689dbf3c0e80e2adcb260b037fa5e61e2bcad04796578",
    "funny.name.here.eth": "0x5d68f26adf1de3f24472e63d0433611fac8f24c537cd007f13c230be6526eb22",
}

labelhashes = {
    "doge": "0xf94adcdd39eb156b60766264ff00058b4ed540a41fcd1e3f0ef433285885f736",
    "vitalik": "0xaf2caa1c2ca1d027f1ac823b529d0a67cd144264b2789fa2ea4d63a67c7103cc",
    "hello": "0x1c8aff950685c2ed4bc3174f3472287b56d9517b9c948127319a09a7a36deac8",
    "namehash": "0x2f9f6920d444f6a44b73ae904ab5dc602f622a7a2f757100457cdfecf4f1bec0",
    "test": "0x9c22ff5f21f0b81b113e63f7db6da94fedef11b2119b4088b89664fb9a3cb658",
    "funny": "0x54ef6a7164821545c481efa280eb15da756f348426bba625692a485daae58a48",
}

token_ids = {
    "0xf94adcdd39eb156b60766264ff00058b4ed540a41fcd1e3f0ef433285885f736": "112758170328470946947235957911183094586171214231483134082786148404895550928694",
    "0xaf2caa1c2ca1d027f1ac823b529d0a67cd144264b2789fa2ea4d63a67c7103cc": "79233663829379634837589865448569342784712482819484549289560981379859480642508",
    "0x1c8aff950685c2ed4bc3174f3472287b56d9517b9c948127319a09a7a36deac8": "12910348618308260923200348219926901280687058984330794534952861439530514639560",
    "0x2f9f6920d444f6a44b73ae904ab5dc602f622a7a2f757100457cdfecf4f1bec0": "21540358135152565469230365080716356634483302591677147634923040095737457262272",
}


def test_namehashes():
    for name, hash in namehashes.items():
        assert utils.namehash(name) == hash, f"Bad hash for name {name}"


def test_labelhashes():
    for label, hash in labelhashes.items():
        assert utils.labelhash(label) == hash, f"Bad hash for label {label}"


def test_token_ids():
    for hash, token in token_ids.items():
        assert (
            utils.token_id_from_labelhash(hash) == token
        ), f"Bad token for labelhash {hash}"
        assert (
            utils.labelhash_from_token_id(token) == hash
        ), f"Bad hash for token {token}"
