#include <iostream>

using namespace std;

void print() {
    cout << "First overload\n";
}

template <typename T> 
void print(const T& t) {
    cout << "Second overload" << t << endl;
}

template <typename First, typename... Rest> 
void print(const First& first, const Rest&... rest) {
    cout << "Third overload" << first << ", ";
    print(rest...); // <name>... -- синтаксис раскрытия пакета параметров   
}

int main()
{
    print(); // первая перегрузка -- 
    print(1); // вторая перегрузка

    // третья перегрузка (variadic template),
    // рекурсивно вызывающая печать остатка строки
    print(10, 20);
    print(100, 200, 300);
    print("first", 2, "third", 3.14159);
}
