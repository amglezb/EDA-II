#include <stdio.h>
#include <omp.h>
static long num_steps = 200000;
double step;
int main(){
    double t0 = omp_get_wtime();
    int i, nthreads=0;
    double x, pi = 0.0;
    step = 1.0 / (double)num_steps;
    #pragma omp parallel
    {
        int id = omp_get_thread_num();
        int nthrds = omp_get_num_threads();
        if (id==0) nthreads = nthrds;
        for (i=id ; i<num_steps ; i=i+nthrds){
            x = (i+0.5)*step;
        #pragma omp critical
            pi += (4.0/(1.0+x*x)) * step;
        }
    }
    printf("PI = %f\n", pi);
    double t1 = omp_get_wtime();
    printf("Tiempo = %.3f ms\n", (t1-t0)*1000.0);
    return 0;
}
