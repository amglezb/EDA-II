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
        #pragma omp master
        {
            id = omp_get_thread_num();
            printf("Master block thread %d. El hilo Master (id %d) esta realizando una tarea exclusiva.\n", id, id);
        }
        id = omp_get_thread_num();
        printf("Parallel block thread %d. Este codigo lo ejecuta TODO hilo.\n", id);
        #pragma omp barrier
    }
    end_time = omp_get_wtime();
    printf("\n--- Resultados ---\n");
    printf("Tiempo: %f\n", end_time - start_time);

    return 0;
}