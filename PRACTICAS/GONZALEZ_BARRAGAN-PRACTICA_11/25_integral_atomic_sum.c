#include <stdio.h>
#include <omp.h>
static long num_steps = 500000;
double step;
int main(){
    double t0 = omp_get_wtime();
    int i;
    double x, pi = 0.0;
    step = 1.0 / (double)num_steps;
    #pragma omp parallel
    {
        double sum = 0.0;
        int id = omp_get_thread_num();
        int nthrds = omp_get_num_threads();
        for(i=id;i<num_steps;i+=nthrds){
            x = (i+0.5)*step;
            sum += 4.0/(1.0+x*x);
        }
        sum *= step;
    #pragma omp atomic
        pi += sum;
    }
    printf("PI = %f\n", pi);
    double t1 = omp_get_wtime();
    printf("Tiempo = %.3f ms\n", (t1-t0)*1000.0);
    return 0;
}
