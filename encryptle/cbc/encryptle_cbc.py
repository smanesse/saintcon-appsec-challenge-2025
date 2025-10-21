from flask import Flask, request, make_response, jsonify
import random
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import os
import json
from datetime import datetime, timezone

app = Flask(__name__)
KEY = os.urandom(16)
EXP = 60
SHARED_DIR = "/shared"

num_tries = 0
top_score = 0


def write_score(score):
    with open(os.path.join(SHARED_DIR, "encryptle_cbc_score.txt"), "wt") as f:
        f.write(str(score))


def get_score(guess, word):
    score = 0
    if len(guess) != len(word):
        return 0
    for i in range(len(guess)):
        if guess[i] == word[i]:
            score += 3
        elif guess[i] in word:
            score += 1
    return score


def random_line(fname):
    with open(fname, "rt") as f:
        c = next(f)
        for num, l in enumerate(f, 2):
            if random.randrange(num):
                continue
            c = l
        return c.strip()


def check_nonce(nonce):
    with open("nonce.txt", "rt") as f:
        nonces = set([x.strip() for x in f.readlines()])
        if nonce in nonces:
            return False
    with open("nonce.txt", "at") as f:
        f.write(nonce + "\n")
    return True


def generate_nonce():
    return os.urandom(32).hex()


def check_time(ts):
    return int(datetime.now(timezone.utc).timestamp()) - ts <= EXP


def encrypt_cbc(plaintext):
    iv = os.urandom(16)
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plaintext.encode()) + padder.finalize()
    cipher = Cipher(algorithms.AES(KEY), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    return (iv + ciphertext).hex()


def decrypt_cbc(encrypted_hex):
    encrypted_data = bytes.fromhex(encrypted_hex)
    iv = encrypted_data[:16]
    ciphertext = encrypted_data[16:]
    cipher = Cipher(algorithms.AES(KEY), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
    return plaintext.decode()


@app.route("/")
def cbc():
    with open("cbc.html", "rt") as f:
        html = f.read()
    solution = random_line("4.txt")
    d = {"word": solution,
         "ts": int(datetime.now(timezone.utc).timestamp()),
         "nonce": generate_nonce()}
    blob = json.dumps(d)
    ciphertext = encrypt_cbc(blob)
    
    # Write solution to shared directory in test mode
    if os.environ.get('TEST_MODE'):
        try:
            with open(os.path.join(SHARED_DIR, "solution.txt"), "wt") as f:
                f.write(solution)
        except Exception as e:
            print(f"Failed to write solution file: {e}")
    
    resp = make_response(html)
    resp.set_cookie("answer", ciphertext)
    return resp


@app.route("/check", methods=['POST'])
def cbc_check():
    global num_tries
    global top_score
    if num_tries >= 5:
        return "You have exceeded your number of tries.", 429
    solution = decrypt_cbc(request.cookies.get("answer"))
    try:
        solution = json.loads(solution)
        if check_time(solution['ts']) and check_nonce(solution['nonce']):
            num_tries += 1
            guess = request.get_json().get('guess').lower()
            score = get_score(guess, solution['word'])
            if score > top_score:
                top_score = score
            
            # max tries or max score, finish and write score
            if num_tries == 5 or score == 3 * 4:  # max score
                write_score(top_score)
            
            # Check if guess is exactly correct
            if guess == solution['word'].lower():
                return jsonify({
                    "answer": solution['word'],
                    "score": score,
                    "correct": True,
                    "tries": num_tries,
                    "message": f"Correct! The word was: {solution['word']}"
                }), 200
            else:
                # Check if this is the final try
                if num_tries >= 5:
                    message = f"Score: {score}. The word was: {solution['word']}."
                else:
                    message = f"Score: {score}. The word was: {solution['word']}. Try again!"
                return jsonify({
                    "answer": solution['word'],
                    "score": score,
                    "correct": False,
                    "tries": num_tries,
                    "message": message
                }), 200
    except:
        pass
    return "Something was wrong with your request.", 400
