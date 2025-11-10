#include <stdio.h>
#include <omp.h>
int main(){
    double t0 = omp_get_wtime();
    omp_set_dynamic(0);
    int procs = omp_get_num_procs();
    printf("Procs: %d\n", procs);
    printf("Max threads (before set): %d\n", omp_get_max_threads());
    omp_set_num_threads(procs);
    printf("In parallel (before): %d\n", omp_in_parallel());
    #pragma omp parallel
    {
        int threads = omp_get_num_threads();
        printf("Threads: %d\n", threads);
        int id = omp_get_thread_num();
        printf("ID: %d\n", id);
        printf("In parallel (inside): %d\n", omp_in_parallel());
    }
    double t1 = omp_get_wtime();
    printf("Tiempo = %.3f ms\n", (t1-t0)*1000.0);
    return 0;
}
