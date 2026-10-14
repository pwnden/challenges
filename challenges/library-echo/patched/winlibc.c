#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

static const char *CMD = "echo $FLAG";

__attribute__((naked)) void pop_rdi_ret(void) {
    __asm__("pop %rdi\n\tret\n");
}

int main(void) {
    char buf[64];
    size_t total = 0, cap = sizeof(buf);
    ssize_t got;

    setvbuf(stdout, NULL, _IONBF, 0);
    printf("이름을 입력하세요: ");
    while (total < cap) {
        got = read(0, buf + total, cap - total);
        if (got <= 0) break;
        total += (size_t)got;
    }
    printf("환영합니다\n");
    return 0;
}
