
def encode_id_as_hex_string(id: int, length: int = 16) -> str:
    return id.to_bytes(length=length, byteorder="big", signed=False).hex()
