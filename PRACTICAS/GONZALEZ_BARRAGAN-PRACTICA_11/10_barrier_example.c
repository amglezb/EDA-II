#include <stdio.h>
#include <omp.h>
#define NUM_THREADS 4
double big_call1(int id){ double s=0; for(long i=0;i<200000;i++) s += (i%7); return s; }
double big_call2(int id){ double s=0; for(long i=0;i<200000;i++) s += (i%11); return s; }
int main(){
    double t0 = omp_get_wtime();
    omp_set_num_threads(NUM_THREADS);
    #pragma omp parallel
    {
        int id = omp_get_thread_num();
        double A;
        A = big_call1(id);
        printf("Thread %d finish big_call1\n", id);
    #pragma omp barrier
        double B = big_call2(id);
        printf("Thread %d finish big_call2\n", id);
    }
    double t1 = omp_get_wtime();
    printf("Tiempo = %.3f ms\n", (t1-t0)*1000.0);
    return 0;
}
