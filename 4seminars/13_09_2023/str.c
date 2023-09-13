char **f() {
        const int slim = 8;
        char s[] = "This is string";
        char **str = (char**)malloc(slim * sizeof(char*));
        int it = 0;
        char* token = strtok(s, " ");

        while (token != NULL) {
                str[it] = (char*)malloc(sizeof(char) * strlen(token) + 1);
                strcpy(str[it], token);
                token = strtok(NULL, " ");
                it ++ ;
        }
        int i = 0;
        /*
        for (i=0; i < it; i++) {
                printf("%s\n", str[i]);
                free((char*)str[i]);
        }
        */
        //free(str);
        str[it] = NULL;
        return str;
}


int main() {
        char **str = f();
        int it = 0;
        while(str[it] != NULL) {
                puts(str[it]);
                it ++;
        }
        return 0;
}
