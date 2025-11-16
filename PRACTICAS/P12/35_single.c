#include <stdio.h>
#include <omp.h>
#include <unistd.h>

#define NUM_THREADS 4

int main() {
    int id;
    double start_time, end_time;
    omp_set_num_threads(NUM_THREADS);
    start_time = omp_get_wtime();
    #pragma omp parallel
    {
        #pragma omp single
        {
            id = omp_get_thread_num();
            printf("Single block thread %d. Solo un hilo (el primero que llego) esta realizando esta tarea exclusiva.\n", id);
        }
        id = omp_get_thread_num();
        printf("Parallel block thread %d. Este codigo lo ejecuta TODO hilo.\n", id);
        #pragma omp barrier
    }
    end_time = omp_get_wtime();
    printf("Tiempo: %f.\n", end_time - start_time);
    return 0;
}