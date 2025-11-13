#include <stdio.h>
#include <omp.h>
int fibonacci_p(int n){
    if (n < 2) return n;
    int x, y;
    #pragma omp task shared(x)
    x = fibonacci_p(n-1);
    #pragma omp task shared(y)
    y = fibonacci_p(n-2);
    #pragma omp taskwait
    return x + y;
}
int main () {
    double t0 = omp_get_wtime();
    int NUM = 16;
    int res = 0;
    #pragma omp parallel
    {
    #pragma omp single
        res = fibonacci_p(NUM);
    }
    printf("fibonacci(%d) = %d\n", NUM, res);
    double t1 = omp_get_wtime();
    printf("Tiempo = %.3f ms\n", (t1-t0)*1000.0);
    return 0;
}
