import sys
import base64
import json
import hashlib
import os
CONTEXT_DIR = "db"
CONTEXT_FILE = os.path.join(CONTEXT_DIR, "provision_context.json")

def load_context():
    os.makedirs(CONTEXT_DIR, exist_ok=True)
    if not os.path.exists(CONTEXT_FILE):
        with open(CONTEXT_FILE, "w") as f:
            json.dump({}, f)
        return {}
    try:
        with open(CONTEXT_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_context(context):
    def encode_bytes(obj):
        if isinstance(obj, bytes):
            return base64.b64encode(obj).decode()
        raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")
    os.makedirs(CONTEXT_DIR, exist_ok=True)
    with open(CONTEXT_FILE, "w") as f:
        json.dump(context, f, indent=2, default=encode_bytes)

def rc4(key, data):
    S = list(range(256))
    j = 0
    out = bytearray()
    # KSA Phase
    for i in range(256):
        j = (j + S[i] + key[i % len(key)]) % 256
        S[i], S[j] = S[j], S[i]
    # PRGA Phase
    i = j = 0
    for char in data:
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        K = S[(S[i] + S[j]) % 256]
        out.append(char ^ K)
    return bytes(out)

def provision_battery():
    context = load_context()
    kek_first_half = context.get('kek_seed_half1')
    kek_second_half = context.get('write_battery_provision_key')
    if kek_first_half is None:
        print("Missing KEK first half")
        return 1
    if kek_second_half is None:
        print("Missing --write-battery-provision-key argument")
        return 1
    if isinstance(kek_first_half, str):
        kek_first_half = base64.b64decode(kek_first_half)
    if isinstance(kek_second_half, str):
        try:
            kek_second_half = bytes.fromhex(kek_second_half)
        except ValueError:
            kek_second_half = base64.b64decode(kek_second_half)
    kek = kek_first_half + kek_second_half

    ipad_enc = context.get('write_battery_provision_ipad')
    opad_enc = context.get('write_battery_provision_opad')
    challenge = context.get('write_battery_provision_challenge')
    expected_response = context.get('write_battery_provision_response')

    if None in (ipad_enc, opad_enc, challenge, expected_response):
        print("Missing one or more required arguments for provisioning")
        return 1

    ipad = base64.b64decode(ipad_enc)
    opad = base64.b64decode(opad_enc)
    challenge_bytes = base64.b64decode(challenge)
    expected_resp_bytes = base64.b64decode(expected_response)

    ipad_decrypted = rc4(kek, ipad)
    opad_decrypted = rc4(kek, opad)
    key_padded = bytes(a ^ b for a, b in zip(ipad_decrypted, opad_decrypted))
    computed_hmac = hashlib.sha256(
        opad_decrypted + hashlib.sha256(ipad_decrypted + challenge_bytes).digest()
    ).digest()

    print(f"Decrypted ipad: {ipad_decrypted.hex()}")
    print(f"Decrypted opad: {opad_decrypted.hex()}")
    print(f"Reconstructed key_padded: {key_padded.hex()}")
    print(f"Expected response: {expected_resp_bytes.hex()}")
    print(f"Computed response: {computed_hmac.hex()}")

    success = computed_hmac == expected_resp_bytes

    result = {
        'kek': kek.hex(),
        'ipad_encrypted': ipad_enc,
        'opad_encrypted': opad_enc,
        'ipad_decrypted': base64.b64encode(ipad_decrypted).decode(),
        'opad_decrypted': base64.b64encode(opad_decrypted).decode(),
        'key_padded': key_padded.hex(),
        'challenge': challenge,
        'expected_response': expected_response,
        'computed_hmac': base64.b64encode(computed_hmac).decode(),
        'success': success
    }
    import os
    result_dir = "db"
    os.makedirs(result_dir, exist_ok=True)
    with open(os.path.join(result_dir, 'provision_result.json'), 'w') as f:
        json.dump(result, f, indent=2)

    print("Provisioning success:", success)
    return 0

def main():
    context = load_context()
    args = sys.argv[1:]
    if args and args[0].endswith('.json'):
        with open(args[0], 'r') as f:
            data = json.load(f)
        context['kek_seed_half1'] = base64.b64decode(data['kek_seed_half1'])
        save_context(context)
        args = args[1:]
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == '--write-battery-provision-key':
            i += 1
            context['write_battery_provision_key'] = args[i]
            save_context(context)
        elif arg == '--write-battery-provision-ipad':
            i += 1
            context['write_battery_provision_ipad'] = args[i]
            save_context(context)
        elif arg == '--write-battery-provision-opad':
            i += 1
            context['write_battery_provision_opad'] = args[i]
            save_context(context)
        elif arg == '--write-battery-provision-challenge':
            i += 1
            context['write_battery_provision_challenge'] = args[i]
            save_context(context)
        elif arg == '--write-battery-provision-response':
            i += 1
            context['write_battery_provision_response'] = args[i]
            save_context(context)
        elif arg == '--provision-battery':
            return provision_battery()
        else:
            print(f"Unknown argument: {arg}")
            return 1
        i += 1
    print("No action specified")
    return 0

if __name__ == '__main__':
    sys.exit(main())
