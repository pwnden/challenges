# Second security experiments

Six scenarios add prepared starting knowledge to the current version 6 catalog.
Players read it in the problem pane and use the declared web or file/terminal
tools. The authoring workflow, solutions and publication finish in this repository.

| Scenario | Primary topic | Proposed level | Tools | Evidence |
| --- | --- | --- | --- | --- |
| [사용자 구분 값 바꾸기](../challenges/paper-session/README.md) | web-authentication-sessions | 입문 | Web | Changing a browser role cookie changes a real authorization response. |
| [공개 폴더 밖의 문서](../challenges/path-parcel/README.md) | web-information-disclosure | 초급 | Web | A relative path reads an actual file outside the public directory. |
| [비밀번호 후보 찾기](../challenges/hash-lantern/README.md) | crypto-hashes-authentication | 입문 | Files, terminal | One of six candidates matches the unsalted SHA-256 record. |
| [확장자가 바뀐 파일](../challenges/false-label/README.md) | forensics-files-metadata | 입문 | Files, terminal | Signature bytes and an archive parser identify the supplied file. |
| [DNS 조회에 담긴 데이터](../challenges/dns-detour/README.md) | forensics-network-evidence | 초급 | Files, terminal | Actual loopback DNS messages carry ordered, retransmitted Base32 chunks. |
| [팀 문서의 읽기 권한](../challenges/borrowed-badge/README.md) | cloud-identity-policies | 초급 | Web | A denied current read and broadly allowed historical reads expose a policy gap. |

The `dns-detour` scenario teaches evidence analysis from a supplied capture. The `borrowed-badge` scenario
uses the misc compatibility category and a labelled local policy subset; its
learning area remains cloud and infrastructure security. The policy's star
action and resource matching, default denial and explicit denial precedence
are declared and tested. It is separate from a provider's complete IAM implementation.

## Shared starting notes

Ten [concept notes](../knowledge/README.md) cover the actual terms and tool
operations needed to begin. `--concept` connects them through `BRIEFING.md` and
the generated author record. `tools/content.py` embeds their contents into
the existing `::knowledge` block in the deployed README. Format validation
rejects an outdated compiled brief. The website displays the explanation locally
without requiring a separate learning service or an external reference visit.

These documents and author references provide the current content reuse.
The version 6 runtime consumes the compiled player document. Structured concept
relationships and a graph UI belong to the later learning model.

## Verification

Run from the challenges checkout:

```sh
python3 -B tools/content.py --check
python3 -B tools/validate.py
python3 -B -m unittest discover -s tools -p 'test_*.py'
python3 -B tools/verify.py
python3 -B tools/check_isolation.py
```

All twelve catalog problems passed format and actual solution checks on Linux/WSL;
declared service patches and resource cleanup also passed. The author regression
suite has 57 passing tests. Network checks established reachable host/peer controls,
then blocked Internet IPv4/IPv6/DNS, host and peer access inside the isolated network
while same-problem HTTP passed.

The file solutions invoke the same sha256sum, tar and base32 programs supplied to
the player. Source evidence regenerates the password record and archive. The archive
has fixed time and OS-independent gzip metadata. Actual local UDP traffic regenerates
the DNS record; reordered copies, missing chunks and conflicting data are tested.
The seven evidence/policy tests also pass in pinned Python 3.13.15, alongside host
Python 3.14.7. The `borrowed-badge`, `path-parcel` and `paper-session` scenarios test normal and invalid
requests, attack recovery, patch denial and continued normal use.

The UI package's md4x 0.0.30 parser recognized the four compiled briefing sections
in each new scenario, including the embedded starting knowledge.

Independent target-learner review and final difficulty assessment remain required
before publication. The author records state that status. Browser Plugin visual
and interactive checks were unavailable. Technical execution and HTTP checks do
not establish that separate learning or visual review.

## Author references

- Browser cookie storage and request behavior: [MDN cookies](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies).
- Relative file input and normalized containment: [OWASP path traversal](https://community.owasp.org/attacks/Path_Traversal).
- Password hashing and candidate costs: [OWASP password storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html).
- DNS question/response format: [RFC 1035](https://www.rfc-editor.org/rfc/rfc1035.html).
- Base32 representation: [RFC 4648](https://www.rfc-editor.org/rfc/rfc4648.html).
- Resource pattern scope: [AWS Resource element](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_resource.html), used as a learning reference for the explicitly limited local evaluator.
