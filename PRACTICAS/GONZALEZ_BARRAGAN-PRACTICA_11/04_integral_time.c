#include <stdio.h>
#include <omp.h>
static long num_steps = 1000000;
double step;
int main(){
    double t0 = omp_get_wtime();
    int i;
    double x, pi, sum = 0.0;
    step = 1.0 / (double)num_steps;
    for (i=0; i<num_steps; i++){
        x = (i+0.5)*step;
        sum = sum + 4.0/(1.0+x*x);
    }
    pi = step * sum;
    printf("PI = %f\n", pi);
    double t1 = omp_get_wtime();
    printf("Tiempo = %.3f ms\n", (t1-t0)*1000.0);
    return 0;
}
