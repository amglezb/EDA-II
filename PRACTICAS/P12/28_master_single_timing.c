#include <stdio.h>
#include <omp.h>
int main(){
    double t0 = omp_get_wtime();
    #pragma omp parallel
    {
        #pragma omp master
        {
            printf("Master block thread %d.\n", omp_get_thread_num());
        }
        int id = omp_get_thread_num();
        printf("Parallel block thread %d.\n", id);
        #pragma omp single
        {
            printf("Single block thread %d.\n", omp_get_thread_num());
        }
    }
    double t1 = omp_get_wtime();
    printf("Tiempo = %.3f ms\n", (t1-t0)*1000.0);
    return 0;
}
