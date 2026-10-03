"""Sign a stable lab document with a temporary RSA key, distributing only its public key."""
import os
from pathlib import Path
import subprocess
import tempfile

DOCUMENT = b'Lab delivery document\nBatch: LAB-17\nRevision: 2\nQuantity: 120\nDestination: Depot-C\nApproved by: Sender\nConfirmation code: pwnden{delivery_7c28e4a1}\n'
OLD_DOCUMENT = DOCUMENT.replace(b'Revision: 2', b'Revision: 1').replace(b'7c28e4a1', b'91b3d6f0')


def run(*args):
    return subprocess.run(['openssl', *map(str, args)], capture_output=True, check=True)


def build(output):
    output.mkdir(parents=True, exist_ok=True)
    copies = {'copy-a.txt': DOCUMENT.replace(b'Depot-C', b'Depot-D').replace(b'7c28e4a1', b'4f06a9c2'),
              'copy-b.txt': OLD_DOCUMENT, 'copy-c.txt': DOCUMENT}
    for name, data in copies.items():
        (output / name).write_bytes(data)
    with tempfile.TemporaryDirectory(prefix='delivery-signing-', dir='/tmp') as name:
        private = Path(name) / 'private.pem'
        run('genpkey', '-algorithm', 'RSA', '-pkeyopt', 'rsa_keygen_bits:2048', '-out', private)
        private.chmod(0o600)
        run('pkey', '-in', private, '-pubout', '-out', output / 'sender-public.pem')
        run('dgst', '-sha256', '-sign', private, '-out', output / 'delivery.sig', output / 'copy-b.txt')
        run('dgst', '-sha256', '-sign', private, '-out', output / 'delivery-v2.sig', output / 'copy-c.txt')
    (output / 'trust-note.txt').write_text('Sender public key and approval policy delivered through the trusted lab channel.\nApproved batch: LAB-17. Approved revision: 2.\nSignature: RSA-2048, SHA-256, PKCS#1 v1.5.\nRevision 1 signature: delivery.sig (previous genuine approval).\nRevision 2 signature: delivery-v2.sig (current approval).\nsignature=delivery-v2.sig\nA valid signature on revision 1 does not make it the current approved delivery.\nFilenames and dates do not establish authenticity or current approval.\nKeys and documents are generated for this exercise; no real signing key is used.\n')
    for path in output.iterdir():
        path.chmod(0o644)
        os.utime(path, (1700000000, 1700000000))


if __name__ == '__main__':
    build(Path(__file__).resolve().parents[1] / 'files')
