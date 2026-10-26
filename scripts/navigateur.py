"""Chrome sans interface et serveur du socle, pour les scripts de vérification.

`chrome()` trouve le navigateur (variable CHROME, puis google-chrome, chromium,
chromium-browser, puis le chemin de macOS). `servi(dossier)` sert un dossier avec
`serve.mjs` du socle, le serveur que les cours utiliseront : types MIME compris,
et sans cache, de sorte que deux prises successives ne partagent pas un ancien module.
"""

import contextlib
import os
import shutil
import socket
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

SOCLE = Path(__file__).resolve().parent.parent
CHROME_MACOS = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def chrome():
    if os.environ.get("CHROME"):
        return os.environ["CHROME"]
    for nom in ("google-chrome", "chromium", "chromium-browser"):
        if shutil.which(nom):
            return shutil.which(nom)
    return CHROME_MACOS


def taille(texte):
    """« 390x844 » -> (390, 844) : une taille de fenêtre, largeur puis hauteur."""
    largeur, hauteur = texte.lower().split("x")
    return int(largeur), int(hauteur)


def lance_chrome(url, *options, largeur=1504, hauteur=856, delai=90, reprises=1):
    """Charge `url` (thème clair forcé, temps virtuel de 12 s) ; `options` : --screenshot=…, --dump-dom.

    Chrome sans interface se bloque parfois : après `delai` secondes, il est relancé
    `reprises` fois, puis `subprocess.TimeoutExpired` remonte à l'appelant."""
    commande = [chrome(), "--headless=new", "--disable-gpu", "--hide-scrollbars", "--blink-settings=preferredColorScheme=1",
                f"--window-size={largeur},{hauteur}", "--virtual-time-budget=12000", *options, url]
    for essai in range(reprises + 1):
        try:
            return subprocess.run(commande, capture_output=True, text=True, timeout=delai)
        except subprocess.TimeoutExpired:
            if essai == reprises:
                raise


def port_libre():
    with socket.socket() as s:
        s.bind(("localhost", 0))
        return s.getsockname()[1]


def attend(url, serveur, secondes=10):
    """Attend que le serveur réponde (une 404 est une réponse) ; échoue s'il meurt ou se tait."""
    fin = time.monotonic() + secondes
    while time.monotonic() < fin:
        if serveur.poll() is not None:
            raise RuntimeError("serve.mjs s'est arrêté (port occupé ?)")
        try:
            urllib.request.urlopen(url, timeout=1)
            return
        except urllib.error.HTTPError:
            return
        except OSError:
            time.sleep(0.1)
    raise RuntimeError(f"le serveur ne répond pas : {url}")


@contextlib.contextmanager
def servi(dossier):
    """Sert `dossier` sur un port libre ; rend l'URL de base (`http://localhost:PORT`)."""
    port = port_libre()
    serveur = subprocess.Popen(["node", str(SOCLE / "serve.mjs"), str(port)], cwd=dossier,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        attend(f"http://localhost:{port}/", serveur)
        yield f"http://localhost:{port}"
    finally:
        serveur.terminate()
        serveur.wait()
