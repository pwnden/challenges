#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(void) {
    char name[64];
    int is_staff = 0;

    setvbuf(stdout, NULL, _IONBF, 0);
    printf("이름을 입력하세요: ");
    if (!fgets(name, sizeof(name) * 4, stdin))
        return 0;
    name[strcspn(name, "\n")] = '\0';
    printf("환영합니다, %s\n", name);

    if (is_staff) {
        const char *flag = getenv("FLAG");
        printf("직원 전용 자료: %s\n", flag ? flag : "(no flag)");
    } else {
        printf("손님 접근만 허용됩니다.\n");
    }
    return 0;
}
