#include<stdio.h>
#include<omp.h>

static long num_steps = 100000;
double step;

int main(){
    int i;
    double x, pi, sum = 0.0, start, time;
    
    step = 1.0 / (double)num_steps;

    start = omp_get_wtime();
    
    for (i = 0; i < num_steps; i++){
        x = (i + 0.5) * step;
        sum = sum + 4.0 / (1.0 + x * x);
    }

    time = omp_get_wtime() - start;

    pi = step * sum;
    printf("PI = %f\n", pi);
    printf("Time = $.2f\n", time);
}
