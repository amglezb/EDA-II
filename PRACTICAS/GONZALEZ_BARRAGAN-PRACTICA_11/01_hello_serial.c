#include <stdio.h>
#include <stdlib.h>
#include <omp.h>
#include <time.h>

int main() {
    double t0 = omp_get_wtime();
    int ID = 0;
    printf("Hello(%d)", ID);
    printf("world!!(%d)\n", ID);

    double t1 = omp_get_wtime();
    double elapsed_ms = (t1 - t0) * 1000.0;
    printf("Tiempo = %.3f ms\n", elapsed_ms);
    return 0;
}
