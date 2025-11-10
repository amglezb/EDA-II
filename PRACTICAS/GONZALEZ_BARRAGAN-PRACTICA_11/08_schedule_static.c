#include <stdio.h>
#include <omp.h>
#define THREADS 4
#define N 8
int main ( ) {
    double t0 = omp_get_wtime();
    int i;
    #pragma omp parallel for schedule(static) num_threads(THREADS)
    for (i = 0; i < N; i++) {
        int k; for(k=0;k<200000*(i+1);++k);
        printf("Thread %d iteration %d.\n", omp_get_thread_num(), i);
    }
    double t1 = omp_get_wtime();
    printf("Tiempo = %.3f ms\n", (t1-t0)*1000.0);
    return 0;
}
