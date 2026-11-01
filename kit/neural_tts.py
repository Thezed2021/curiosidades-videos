#!/usr/bin/env python3
"""Voz neural pt-BR (Kokoro v1.0, voz pm_santa) 100% offline.

Uso como módulo:
    from neural_tts import TTS
    tts = TTS()                      # usa $TTS_ROOT (padrão ~/tts)
    audio = tts.say("Texto falado.")  # np.float32 a 24 kHz
    tts.save_wav(audio, "x.wav")

Uso em linha de comando:
    python3 neural_tts.py "Texto" saida.wav

Fonemas: espeak-ng chamado PALAVRA A PALAVRA (evita "o homem" -> "w omem"),
com tabela fixa para palavras átonas e dicionário LEX para correções.
"""
import json, os, re, subprocess, sys, unicodedata, wave
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TTS_ROOT = os.environ.get("TTS_ROOT", os.path.expanduser("~/tts"))
SR = 24000

# palavras átonas: pronúncia fixa (o espeak isolado as tônica ou funde)
ATONAS = {
    "o": "u", "a": "ɐ", "os": "us", "as": "ɐs", "um": "ũ", "uns": "ũs",
    "do": "du", "da": "dɐ", "dos": "dus", "das": "dɐs", "de": "dʒi",
    "e": "i", "em": "ẽj", "no": "nu", "na": "nɐ", "nos": "nus", "nas": "nɐs",
    "que": "ki", "se": "si", "com": "kõ", "por": "poɾ", "para": "pɐɾɐ",
    "pra": "pɾɐ", "ao": "aw", "aos": "aws", "à": "a", "às": "as",
    "me": "mi", "te": "tʃi", "lhe": "ʎi", "nem": "nẽj", "mas": "mɐs",
    "num": "nũ", "numa": "numɐ", "pelo": "pelu", "pela": "pelɐ",
    "pelos": "pelus", "pelas": "pelɐs", "sem": "sẽj", "ou": "ow",
}

# correções de pronúncia (palavra minúscula -> IPA). Acrescente quando o
# usuário apontar uma palavra falada errada.
LEX = {
}

_WORD = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ'-]+|[0-9]+|[.,!?;:…—]")


class TTS:
    def __init__(self, root=TTS_ROOT, voice="pm_santa"):
        import onnxruntime as ort
        self.espeak = os.path.join(root, "install", "bin", "espeak-ng")
        self.data = os.path.join(root, "install", "share", "espeak-ng-data")
        kdir = os.path.join(root, "kokoro")
        so = ort.SessionOptions()
        so.intra_op_num_threads = max(1, os.cpu_count() or 1)
        self.sess = ort.InferenceSession(os.path.join(kdir, "kokoro-v1.0.onnx"), so,
                                         providers=["CPUExecutionProvider"])
        self.voice = np.load(os.path.join(kdir, f"{voice}.npy")).astype(np.float32)
        self.vocab = json.load(open(os.path.join(HERE, "vocab.json"), encoding="utf-8"))
        self._cache = {}

    # ---------- fonemas ----------
    def _espeak_word(self, w):
        if w in self._cache:
            return self._cache[w]
        env = dict(os.environ, ESPEAK_DATA_PATH=self.data)
        out = subprocess.run([self.espeak, "-v", "pt-br", "-q", "--ipa=3", "--sep=", w],
                             capture_output=True, text=True, env=env).stdout
        ipa = " ".join(out.split())
        self._cache[w] = ipa
        return ipa

    def phonemes(self, text):
        parts = []
        for tok in _WORD.findall(text):
            if re.fullmatch(r"[.,!?;:…—]", tok):
                if parts:
                    parts[-1] += tok
                else:
                    parts.append(tok)
                continue
            low = tok.lower()
            if low in LEX:
                ipa = LEX[low]
            elif low in ATONAS:
                ipa = ATONAS[low]
            else:
                ipa = self._espeak_word(tok)
            parts.append(ipa)
        ph = " ".join(parts)
        ph = unicodedata.normalize("NFD", ph)
        return ph

    def tokens(self, ph):
        return [self.vocab[c] for c in ph if c in self.vocab]

    # ---------- síntese ----------
    def _infer(self, toks, speed):
        style = self.voice[min(len(toks), len(self.voice)) - 1]
        out = self.sess.run(None, {
            "tokens": np.array([[0, *toks, 0]], dtype=np.int64),
            "style": np.asarray(style, dtype=np.float32).reshape(1, -1),
            "speed": np.array([speed], dtype=np.float32),
        })
        return np.asarray(out[0]).ravel().astype(np.float32)

    def say(self, text, speed=1.0):
        """Sintetiza um trecho. Frases longas são divididas por pontuação."""
        chunks = [c.strip() for c in re.split(r"(?<=[.!?;])\s+", text) if c.strip()]
        out = []
        for c in chunks:
            toks = self.tokens(self.phonemes(c))
            while toks:
                piece, toks = toks[:500], toks[500:]
                a = self._infer(piece, speed)
                out.append(a)
                out.append(np.zeros(int(0.12 * SR), np.float32))
        if not out:
            return np.zeros(int(0.2 * SR), np.float32)
        a = np.concatenate(out[:-1])
        # apara silêncio das pontas
        thr = 0.01 * (np.abs(a).max() + 1e-9)
        idx = np.where(np.abs(a) > thr)[0]
        if len(idx):
            a = a[max(0, idx[0] - 240): idx[-1] + 480]
        return a

    @staticmethod
    def save_wav(a, path, sr=SR):
        a = np.clip(a, -1, 1)
        with wave.open(path, "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
            w.writeframes((a * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    t = TTS()
    print(t.phonemes(sys.argv[1]))
    a = t.say(sys.argv[1])
    t.save_wav(a, sys.argv[2])
    print(f"{len(a)/SR:.2f}s -> {sys.argv[2]}")
