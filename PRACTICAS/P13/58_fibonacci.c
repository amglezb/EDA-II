#include <stdio.h>
#include <stdlib.h>
#include <omp.h>
#define NUM 10
int fibonacci_p(int n){
    int x, y;
    printf("%d\n", omp_get_thread_num());
    if (n < 2)
        return n;
    #pragma omp task shared(x)
    x = fibonacci_p(n-1);
    #pragma omp task shared(y)
    y = fibonacci_p(n-2);
    #pragma omp taskwait
    return x + y;
}

int main () {
    int res = 0;
    double i_time, f_time, time;
    i_time = omp_get_wtime();
    #pragma omp parallel
    {
        #pragma omp master
        {
            res = fibonacci_p(NUM);
        }
    }
    f_time = omp_get_wtime();
    time = f_time - i_time;
    printf("Fibonacci de %d es: %d\n", NUM, res);
    printf("Tiempo: %f segundos\n", time);
    
    return 0;
}