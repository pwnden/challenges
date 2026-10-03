"""Runs inside an offline container; reports installation separately from use."""
import base64
import configparser
import hashlib
import hmac
import http.server
import json
import os
import shutil
import socket
import ssl
import struct
import sys
import subprocess
import threading
import time
import zlib
import wave
from pathlib import Path

RESULTS = []
CHILDREN = []


def record(name, passed, **detail):
    row = {"name": name, "passed": bool(passed), **detail}
    RESULTS.append(row)
    print(json.dumps(row), flush=True)


def check(name, argv, expected=None, codes=(0,), timeout=45, kind="functional"):
    started = time.monotonic()
    try:
        result = subprocess.run(argv, capture_output=True, text=True, errors="replace", timeout=timeout)
        output = result.stdout + result.stderr
        record(name, result.returncode in codes and (expected is None or expected in output),
               kind=kind, code=result.returncode, seconds=round(time.monotonic() - started, 2), output=output[-2500:])
        return result
    except (OSError, subprocess.TimeoutExpired) as error:
        record(name, False, kind=kind, error=str(error))


def shell(name, script, expected=None, codes=(0,), timeout=45):
    return check(name, ["bash", "-ec", script], expected, codes, timeout)


def child(argv):
    # Temporary services are local fixture providers, never external targets.
    process = subprocess.Popen(argv, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    CHILDREN.append(process)
    return process


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        body = b'<html><title>pwnden-test</title><a href="/hidden">hidden</a></html>' if self.path == "/" else (b"pwnden-test\n" if self.path == "/hidden" else b"not-found\n")
        self.send_response(200 if self.path in ("/", "/hidden") else 404)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


class FixtureServer(http.server.ThreadingHTTPServer):
    def handle_error(self, request, client_address):
        # TLS probes intentionally abort connections while enumerating ciphers.
        if not isinstance(sys.exc_info()[1], OSError):
            super().handle_error(request, client_address)


def main():
    os.chdir("/workspace")
    missing = [name for name in COMMANDS if shutil.which(name) is None]
    record("command-coverage", not missing, kind="installation", checked=len(COMMANDS), missing=missing)
    status = Path("/proc/self/status").read_text()
    record("nonroot-no-capabilities", os.getuid() == 10001 and "CapEff:\t0000000000000000" in status and "NoNewPrivs:\t1" in status, kind="policy")
    metadata = subprocess.run(["bash", "-ec", "getcap -r /usr /opt; find /usr /opt -type f -perm /6000 -print"], capture_output=True, text=True)
    record("image-privilege-metadata-removed", metadata.returncode == 0 and not metadata.stdout.strip(), kind="policy")
    try:
        socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        record("raw-socket-denied", False, kind="policy")
    except PermissionError:
        record("raw-socket-denied", True, kind="policy")
    shell("readonly-root", '! touch /etc/pwnden-probe 2>/dev/null')
    Path("sample.txt").write_text("pwnden-test\n")
    Path("sample.yaml").write_text("flag: pwnden-test\n")
    Path("words.txt").write_text("hidden\nmissing\n")
    Path("passwords.txt").write_text("wrong\npwnden-test\n")
    check("yq-mike-farah", ["yq", "-r", ".flag", "sample.yaml"], "pwnden-test")
    shell("zstd-roundtrip", "zstd -q sample.txt -o sample.zst; zstd -dc sample.zst", "pwnden-test")
    check("hexdump", ["hexdump", "-C", "sample.txt"], "pwnden-test")
    shell("gpg-offline-roundtrip", "gpg --batch --pinentry-mode loopback --passphrase fixture --symmetric --output sample.gpg sample.txt; gpg --batch --pinentry-mode loopback --passphrase fixture --decrypt sample.gpg", "pwnden-test")
    check("hashid-candidate", ["hashid", hashlib.md5(b"pwnden-test").hexdigest()], "MD5")
    check("crunch-bounded", ["crunch", "1", "1", "ab"], "a\nb")
    Path("hash.txt").write_text(hashlib.md5(b"pwnden-test").hexdigest() + "\n")
    shell("john-jumbo-raw-md5", "john --format=raw-md5 --wordlist=passwords.txt --pot=john.pot hash.txt; john --show --format=raw-md5 --pot=john.pot hash.txt", "pwnden-test")
    shell("hashcat-cpu", "hashcat -m 0 -a 0 -D 1 --potfile-disable --quiet -o hashcat.output hash.txt passwords.txt; cat hashcat.output", "pwnden-test", timeout=120)
    shell("john-zip-conversion", "zip -q -P pwnden-test encrypted.zip sample.txt; zip2john encrypted.zip > zip.hash; john --wordlist=passwords.txt --pot=zip.pot zip.hash; john --show --pot=zip.pot zip.hash", "pwnden-test")
    check("rsa-fermat", ["RsaCtfTool", "-n", "3233", "-e", "17", "--attack", "fermat", "--private"], "PRIVATE KEY")
    header = base64.urlsafe_b64encode(b'{"alg":"HS256","typ":"JWT"}').rstrip(b"=")
    payload = base64.urlsafe_b64encode(b'{"sub":"pwnden-test"}').rstrip(b"=")
    body = header + b"." + payload
    signature = base64.urlsafe_b64encode(hmac.new(b"fixture", body, hashlib.sha256).digest()).rstrip(b"=")
    # The pinned upstream CLI exits 1 even after a successful local decode.
    check("jwt-local-decode", ["jwt_tool.py", (body + b"." + signature).decode()], 'sub = "pwnden-test"', codes=(1,))
    config = configparser.ConfigParser()
    config.read(Path.home() / ".jwt_tool/jwtconf.ini")
    record("jwt-local-initialization", config["services"]["proxy"] == "False"
           and not config["services"]["jwksdynamic"]
           and Path(config["input"]["wordlist"]).is_file()
           and not (Path(config["crypto"]["privkey"]).stat().st_mode & 0o077), kind="functional")
    Path("tiny.c").write_text('#include <stdio.h>\nint main(void){puts("pwnden-test");return 0;}\n')
    check("compile-fixture", ["gcc", "-g", "-O0", "-o", "tiny", "tiny.c"])
    check("checksec-elf", ["checksec", "--file=tiny"], "NX enabled")
    check("radare2-static", ["radare2", "-q", "-c", "iI", "tiny"], "elf")
    check("rizin-static", ["rizin", "-q", "-c", "iI", "tiny"], "elf")
    # A self-authored PE64 with one section and a literal; no imported samples.
    pe = bytearray(1024)
    pe[:2] = b"MZ"
    struct.pack_into("<I", pe, 60, 128)
    pe[128:132] = b"PE\x00\x00"
    struct.pack_into("<HHIIIHH", pe, 132, 0x8664, 1, 0, 0, 0, 240, 0x22)
    optional = 152
    struct.pack_into("<H", pe, optional, 0x20b)
    struct.pack_into("<I", pe, optional + 4, 512)
    struct.pack_into("<IIQII", pe, optional + 16, 0x1000, 0x1000, 0x140000000, 0x1000, 512)
    struct.pack_into("<II", pe, optional + 56, 0x2000, 512)
    struct.pack_into("<H", pe, optional + 68, 3)
    struct.pack_into("<I", pe, optional + 108, 16)
    section = optional + 240
    pe[section:section + 8] = b".text\x00\x00\x00"
    struct.pack_into("<IIII", pe, section + 8, 512, 0x1000, 512, 512)
    struct.pack_into("<I", pe, section + 36, 0x60000020)
    pe[512:525] = b"\xc3pwnden-test\x00"
    Path("tiny.exe").write_bytes(pe)
    check("floss-static-string", ["floss", "--only", "static", "--", "tiny.exe"], "pwnden-test")
    Path("capa-rule.yml").write_text('rule:\n  meta:\n    name: pwnden fixture string\n    authors: [pwnden]\n    scopes:\n      static: file\n      dynamic: process\n  features:\n    - string: pwnden-test\n')
    check("capa-local-rule", ["capa", "-r", "capa-rule.yml", "tiny"], "pwnden fixture string")
    check("ltrace-child", ["ltrace", "./tiny"], "puts(")
    check("gef-child", ["gdb-gef", "-q", "-batch", "-ex", "file tiny", "-ex", "break main", "-ex", "run", "-ex", "context"], "main", timeout=60)
    check("pwndbg-child", ["pwndbg", "-q", "-batch", "-ex", "file tiny", "-ex", "start", "-ex", "context"], "main", timeout=60)
    Path("hook.js").write_text('console.log("pwnden-frida-child");\n')
    check("frida-spawn-own-child", ["frida", "-q", "-f", "./tiny", "-l", "hook.js", "-t", "5"], "pwnden-frida-child", timeout=30)
    if shutil.which("analyzeHeadless"):
        Path("ghidra-project").mkdir()
        check("ghidra-headless", ["analyzeHeadless", "ghidra-project", "Fixture", "-import", "tiny", "-deleteProject", "-max-cpu", "2", "-analysisTimeoutPerFile", "30"], "Import succeeded", timeout=120)
    shell("squashfs-userspace", "mkdir squash-input; cp sample.txt squash-input/; mksquashfs squash-input sample.squashfs -noappend -processors 1 >/dev/null; unsquashfs -cat sample.squashfs sample.txt", "pwnden-test")
    Path("tree.dts").write_text('/dts-v1/; / { fixture = "pwnden-test"; };\n')
    shell("device-tree", "dtc -I dts -O dtb tree.dts -o tree.dtb; dtc -I dtb -O dts tree.dtb", "pwnden-test")
    check("binwalk-signature", ["binwalk", "sample.squashfs"], "Squashfs")
    # Valid PNG with deliberately embedded, human-readable metadata.
    def chunk(kind, data):
        return struct.pack("!I", len(data)) + kind + data + struct.pack("!I", zlib.crc32(kind + data))
    Path("sample.png").write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack("!IIBBBBB", 1, 1, 8, 2, 0, 0, 0)) + chunk(b"tEXt", b"Comment\x00pwnden-test") + chunk(b"IDAT", zlib.compress(b"\x00\xff\x00\x00")) + chunk(b"IEND", b""))
    check("zsteg-png", ["zsteg", "sample.png"], "pwnden-test")
    with wave.open("carrier.wav", "wb") as audio:
        audio.setparams((1, 2, 44100, 44100, "NONE", "not compressed"))
        audio.writeframes(b"\x01\x00" * 44100)
    shell("stegseek-wordlist", "steghide embed -cf carrier.wav -ef sample.txt -sf hidden.wav -p pwnden-test -f; stegseek hidden.wav passwords.txt extracted.txt -f; cat extracted.txt", "pwnden-test")
    Path("email.bin").write_bytes(b"fixture@example.com\n" * 100)
    shell("bulk-extractor-file", "bulk_extractor -j 2 -o bulk-output email.bin; cat bulk-output/email.txt", "fixture@example.com", timeout=90)
    Path("scalpel.conf").write_text(r"jpg y 200000 \xff\xd8\xff \xff\xd9" + "\n")
    Path("carve.bin").write_bytes(b"\xff\xd8\xff\xe0" + b"pwnden-test" * 500 + b"\xff\xd9")
    shell("scalpel-file-carving", "scalpel -c scalpel.conf -o carve-output carve.bin; find carve-output -name '*.jpg'", ".jpg")
    tcp = struct.pack("!HHIIBBHHH", 18080, 42000, 1, 1, 0x50, 0x18, 1024, 0, 0) + b"HTTP/1.0 200 OK\r\nContent-Length: 12\r\n\r\npwnden-test\n"
    ip = struct.pack("!BBHHHBBH4s4s", 0x45, 0, 20 + len(tcp), 1, 0, 64, 6, 0, bytes([192, 0, 2, 1]), bytes([192, 0, 2, 2])) + tcp
    packet = bytes.fromhex("0000000000020000000000010800") + ip
    Path("sample.pcap").write_bytes(struct.pack("<IHHIIII", 0xa1b2c3d4, 2, 4, 0, 0, 65535, 1) + struct.pack("<IIII", 1, 0, len(packet), len(packet)) + packet)
    shell("tcpflow-offline", "tcpflow -r sample.pcap -o tcpflows; rg pwnden-test tcpflows", "pwnden-test")
    Path("sample.py").write_text('eval("pwnden-test")\n')
    Path("semgrep-rule.yml").write_text('rules:\n  - id: fixture-eval\n    languages: [python]\n    message: pwnden-test\n    severity: WARNING\n    pattern: eval(...)\n')
    check("semgrep-local-rule", ["semgrep", "--metrics=off", "--config", "semgrep-rule.yml", "--json", "sample.py"], "fixture-eval", timeout=60)
    Path("packages").mkdir()
    Path("packages/package-lock.json").write_text(json.dumps({"name": "fixture", "lockfileVersion": 3, "packages": {"node_modules/lodash": {"version": "4.17.15"}}}))
    check("syft-file-sbom", ["syft", "dir:packages", "-o", "json"], "lodash", timeout=60)
    check("grype-offline-db", ["grype", "dir:packages", "-o", "json"], "CVE-", timeout=90)
    check("trivy-offline-db", ["trivy", "fs", "--scanners", "vuln", "--cache-backend", "memory", "--format", "json", "packages"], "CVE-", timeout=90)
    synthetic_token = "ghp_" + hashlib.sha256(b"pwnden-only-synthetic-not-a-key").hexdigest()[:36]
    Path("fake-secret.txt").write_text('# deliberately synthetic fixture\naccess_token = "' + synthetic_token + '"\n')
    check("gitleaks-local-file", ["gitleaks", "detect", "--no-git", "--source", ".", "--redact", "--report-path", "leaks.json"], "leaks found", codes=(1,), timeout=60)
    # Key-only signing uses no public signing/transparency services or TUF fetch.
    Path("signing-config.json").write_text(json.dumps({"mediaType": "application/vnd.dev.sigstore.signingconfig.v0.2+json", "rekorTlogConfig": {}, "tsaConfig": {}}))
    shell("cosign-offline-key-signature", "COSIGN_PASSWORD=fixture cosign generate-key-pair >/dev/null; COSIGN_PASSWORD=fixture cosign sign-blob --key cosign.key --signing-config signing-config.json --bundle signature.json sample.txt; cosign verify-blob --key cosign.pub --bundle signature.json --insecure-ignore-tlog --offline sample.txt", "Verified OK", timeout=60)
    Path("tampered.txt").write_text("changed fixture\n")
    check("cosign-tampering-rejected", ["cosign", "verify-blob", "--key", "cosign.pub", "--bundle", "signature.json", "--insecure-ignore-tlog", "--offline", "tampered.txt"], "invalid signature", codes=(1,), timeout=60)
    shell("minio-client-local-copy", "mc --config-dir /tmp/mc cp sample.txt copied.txt; cmp sample.txt copied.txt")
    # Real requests and bounded discovery against a loopback fixture server.
    server = FixtureServer(("127.0.0.1", 18080), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = "http://127.0.0.1:18080"
    check("wget-http", ["wget", "-qO-", url + "/hidden"], "pwnden-test")
    check("httpie-http", ["http", "--ignore-stdin", "--body", url + "/hidden"], "pwnden-test")
    check("gobuster-http", ["gobuster", "dir", "-u", url, "-w", "words.txt", "-t", "2", "--no-progress"], "hidden")
    check("feroxbuster-http", ["feroxbuster", "-u", url, "-w", "words.txt", "-t", "2", "--depth", "1", "--no-recursion", "--no-state", "--silent"], "hidden")
    check("whatweb-http", ["whatweb", "--color=never", url], "pwnden-test")
    check("httpx-projectdiscovery", ["httpx", "-u", url, "-title", "-silent"], "pwnden-test")
    check("katana-http", ["katana", "-u", url, "-d", "1", "-c", "2", "-p", "1", "-silent"], "/hidden")
    check("rustscan-connect", ["rustscan", "-a", "127.0.0.1", "-p", "18080", "-b", "2", "--ulimit", "256", "--", "--unprivileged", "-sT", "-Pn", "-n"], "18080")
    Path("nuclei-fixture.yaml").write_text('id: pwnden-fixture\ninfo:\n  name: local fixture\n  author: pwnden\n  severity: info\nhttp:\n  - method: GET\n    path: ["{{BaseURL}}/hidden"]\n    matchers:\n      - type: word\n        words: ["pwnden-test"]\n')
    check("nuclei-local-template", ["nuclei", "-u", url, "-t", "/workspace/nuclei-fixture.yaml", "-silent"], "pwnden-fixture", timeout=60)
    check("cewl-small-wordlist", ["cewl", "--depth", "0", url], "hidden")
    shell("tls-fixture-key", "openssl req -x509 -newkey rsa:2048 -nodes -days 1 -subj /CN=pwnden-test -keyout tls.key -out tls.crt >/dev/null 2>&1")
    tls = FixtureServer(("127.0.0.1", 18443), Handler)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain("tls.crt", "tls.key")
    tls.socket = context.wrap_socket(tls.socket, server_side=True)
    threading.Thread(target=tls.serve_forever, daemon=True).start()
    check("sslscan-local-tls", ["sslscan", "--no-colour", "127.0.0.1:18443"], "pwnden-test", timeout=60)
    check("testssl-local-tls", ["testssl", "--quiet", "--warnings", "batch", "--fast", "--server-defaults", "127.0.0.1:18443"], "pwnden-test", timeout=90)
    tls.shutdown()
    shell("libfuzzer-build", "printf '#include <stddef.h>\n#include <stdint.h>\nint LLVMFuzzerTestOneInput(const uint8_t*d,size_t n){return 0;}\n' > fuzz.c; clang -fsanitize=fuzzer fuzz.c -o fuzz")
    check("libfuzzer-runs", ["./fuzz", "-runs=100", "-rss_limit_mb=512"], "Done 100 runs")
    Path("hfuzz.c").write_text('#include <unistd.h>\n#include <stdlib.h>\nint main(void){char c;if(read(0,&c,1)==1&&c==\'A\')abort();return 0;}\n')
    Path("hfuzz-seeds").mkdir()
    Path("hfuzz-seeds/seed").write_text("A")
    check("honggfuzz-instrument", ["hfuzz-clang", "-o", "hfuzz-target", "hfuzz.c"])
    check("honggfuzz-bounded-run", ["honggfuzz", "-i", "hfuzz-seeds", "-W", "hfuzz-output", "-n", "1", "--run_time", "2", "--stdin_input", "--", "./hfuzz-target"], timeout=30)
    record("honggfuzz-real-crash", any("SIGABRT" in path.name for path in Path("hfuzz-output").glob("*")), kind="functional")
    Path("forge/src").mkdir(parents=True)
    Path("forge/src/Fixture.sol").write_text('pragma solidity >=0.8.0; contract Fixture { function value() public pure returns(uint256){return 42;} }\n')
    check("forge-local-compiler", ["forge", "build", "--root", "forge", "--offline", "--use", "/usr/local/bin/solc"], "Compiler run successful", timeout=90)
    chain = child(["anvil", "--host", "127.0.0.1", "--port", "18545", "--silent"])
    for _ in range(50):
        try:
            with socket.create_connection(("127.0.0.1", 18545), timeout=.1):
                break
        except OSError:
            time.sleep(.1)
    check("cast-local-chain", ["cast", "block-number", "--rpc-url", "http://127.0.0.1:18545"], "0")
    chain.terminate()
    Path("apk-project/smali").mkdir(parents=True)
    Path("apk-project/apktool.yml").write_text('version: 2.7.0\napkFileName: fixture.apk\nisFrameworkApk: false\nusesFramework:\n  ids: [1]\nsdkInfo:\n  minSdkVersion: "21"\n  targetSdkVersion: "28"\nversionInfo:\n  versionCode: "1"\n  versionName: "1.0"\ndoNotCompress: []\n')
    Path("apk-project/AndroidManifest.xml").write_text('<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="invalid.pwnden.fixture"><application android:label="pwnden-test"/></manifest>\n')
    Path("apk-project/smali/Fixture.smali").write_text('.class public Linvalid/pwnden/Fixture;\n.super Ljava/lang/Object;\n.method public static value()Ljava/lang/String;\n    .registers 1\n    const-string v0, "pwnden-test"\n    return-object v0\n.end method\n')
    check("apktool-build-fixture", ["apktool", "b", "apk-project", "-o", "fixture.apk"], "Built apk", timeout=90)
    check("apktool-decode-fixture", ["apktool", "d", "fixture.apk", "-o", "apk-decoded"], "Baksmaling", timeout=90)
    shell("jadx-dex-decompile", "jadx --no-res -d jadx-output fixture.apk; rg pwnden-test jadx-output", "pwnden-test", timeout=90)
    if shutil.which("msfvenom"):
        check("msfvenom-custom-fixture", ["msfvenom", "-p", "generic/custom", "PAYLOADFILE=/workspace/sample.txt", "-f", "raw", "-o", "msf.bin"], "Saved as:", timeout=90)
        record("msfvenom-generated-bytes", Path("msf.bin").exists() and Path("msf.bin").read_bytes() == Path("sample.txt").read_bytes(), kind="functional")
    # The engine is present; actual memory dumps, symbols, AD services and device
    # scenarios require their own per-problem fixtures and are not claimed here.
    check("volatility-cli-startup", ["vol", "-h"], "Volatility", timeout=60, kind="startup")
    check("netexec-cli-startup", ["nxc", "--version"], "1.5.1", codes=(0, 1), timeout=60, kind="startup")
    server.shutdown()
    record("resource-observations", True, kind="measurement", **{
        name: Path("/sys/fs/cgroup", name).read_text().strip()
        for name in ("memory.peak", "pids.peak", "cpu.stat") if Path("/sys/fs/cgroup", name).exists()
    })


try:
    main()
finally:
    for process in CHILDREN:
        if process.poll() is None:
            process.terminate()
        process.wait(timeout=10)
raise SystemExit(0 if all(row["passed"] for row in RESULTS) else 1)
