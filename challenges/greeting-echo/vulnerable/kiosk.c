#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

void grant_access(void) {
    const char *flag = getenv("FLAG");
    printf("관리자 전용: %s\n", flag ? flag : "(no flag)");
}

int main(void) {
    char echo_buf[32];
    char name[64];
    char line[16];
    long n;
    size_t total, cap;

    setvbuf(stdout, NULL, _IONBF, 0);

    printf("몇 바이트를 돌려받을까요 (0-64)? ");
    if (!fgets(line, sizeof(line), stdin)) return 0;
    n = strtol(line, NULL, 10);
    if (n < 0) n = 0;
    if (n > 120) n = 120;
    write(1, echo_buf, (size_t)n);
    printf("\n");

    printf("이름을 입력하세요: ");
    total = 0;
    cap = sizeof(name) * 3;
    while (total < cap) {
        ssize_t got = read(0, name + total, cap - total);
        if (got <= 0) break;
        total += (size_t)got;
    }
    printf("환영합니다\n");
    return 0;
}
