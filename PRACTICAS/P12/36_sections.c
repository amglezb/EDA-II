#include <stdio.h>
#include <omp.h>
#include <unistd.h>
#define NUM_THREADS 4
void section_a(int id) {
    printf("Section A executed by thread %d.\n", id);
    usleep(100000);
}
void section_b(int id) {
    printf("Section B executed by thread %d.\n", id);
    usleep(200000);
}
void section_c(int id) {
    printf("Section C executed by thread %d.\n", id);
    usleep(150000);
}
int main() {
    int id;
    double start_time, end_time;
    omp_set_num_threads(NUM_THREADS);
    start_time = omp_get_wtime();
    #pragma omp parallel
    {
        #pragma omp sections
        {
            #pragma omp section
            section_a(omp_get_thread_num());
            #pragma omp section
            section_b(omp_get_thread_num());
            #pragma omp section
            section_c(omp_get_thread_num());
        }
        id = omp_get_thread_num();
        printf("Parallel block thread %d.\n", id);
        #pragma omp barrier
    }
    end_time = omp_get_wtime();
    printf("Tiempo: %f.\n", end_time - start_time);
    return 0;
}