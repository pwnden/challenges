#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

static void run_command(const char *cmd) {
    if (cmd && strcmp(cmd, "STATUS") == 0) {
        printf("상태: 정상\n");
    } else if (cmd && strcmp(cmd, "SHOW-ADMIN-LOG") == 0) {
        const char *flag = getenv("FLAG");
        printf("관리자 기록: %s\n", flag ? flag : "(no flag)");
    } else {
        printf("알 수 없는 명령입니다.\n");
    }
}

__attribute__((naked)) void pop_rdi_ret(void) {
    __asm__("pop %rdi\n\tret\n");
}

int main(void) {
    char cmd[8];
    char buf[64];
    size_t total, cap;
    ssize_t got;

    setvbuf(stdout, NULL, _IONBF, 0);

    printf("명령을 입력하세요 (STATUS): ");
    total = 0;
    cap = sizeof(cmd) - 1;
    while (total < cap) {
        got = read(0, cmd + total, cap - total);
        if (got <= 0) break;
        total += (size_t)got;
        if (memchr(cmd + total - got, '\n', (size_t)got)) break;
    }
    cmd[total] = 0;
    cmd[strcspn(cmd, "\n")] = 0;
    run_command(cmd);

    printf("메모를 입력하세요: ");
    total = 0;
    cap = sizeof(buf) * 3;
    while (total < cap) {
        got = read(0, buf + total, cap - total);
        if (got <= 0) break;
        total += (size_t)got;
    }
    printf("메모가 저장되었습니다.\n");
    return 0;
}
