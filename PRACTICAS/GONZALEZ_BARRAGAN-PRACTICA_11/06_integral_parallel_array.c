#include <stdio.h>
#include <omp.h>
#define NUM_THREADS 4
static long num_steps = 1000000;
double step;
int main(){
    double t0 = omp_get_wtime();
    int i, nthreads;
    double pi, sum[NUM_THREADS];
    step = 1.0 / (double)num_steps;
    omp_set_num_threads(NUM_THREADS);
    #pragma omp parallel
    {
        int i, id, nthrds;
        double x;
        id = omp_get_thread_num();
        nthrds = omp_get_num_threads();
        if (id == 0) nthreads = nthrds;
        for (i=id, sum[id]=0.0 ; i<num_steps ; i=i+nthrds){
            x = (i+0.5)*step;
            sum[id] += 4.0/(1.0+x*x);
        }
    }
    for (i=0, pi=0.0 ; i < nthreads; i++)
        pi += sum[i]*step;
    printf("PI = %f\n", pi);
    double t1 = omp_get_wtime();
    printf("Tiempo = %.3f ms\n", (t1-t0)*1000.0);
    return 0;
}
