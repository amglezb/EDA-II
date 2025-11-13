#include <stdio.h>
#include <omp.h>
void section_a(int id){ printf("section_a run by %d\n", id); }
void section_b(int id){ printf("section_b run by %d\n", id); }
void section_c(int id){ printf("section_c run by %d\n", id); }
int main(){
    double t0 = omp_get_wtime();
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
        #pragma omp master
            {
                printf("Master block thread %d.\n", omp_get_thread_num());
            }
        #pragma omp single
            {
                printf("Single block thread %d.\n", omp_get_thread_num());
            }
            printf("Parallel block thread %d.\n", omp_get_thread_num());
    }
    double t1 = omp_get_wtime();
    printf("Tiempo = %.3f ms\n", (t1-t0)*1000.0);
    return 0;
}
