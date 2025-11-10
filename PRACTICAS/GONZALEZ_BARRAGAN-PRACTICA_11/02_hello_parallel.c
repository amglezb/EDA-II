#include <stdio.h>
#include <omp.h>
int main() {
    double t0 = omp_get_wtime();
    #pragma omp parallel
    {
        int ID = omp_get_thread_num();
        printf("Hello(%d)", ID);
        printf("world!!(%d)\n", ID);
    }
    double t1 = omp_get_wtime();
    printf("Tiempo = %.3f ms\n", (t1-t0)*1000.0);
    return 0;
}
