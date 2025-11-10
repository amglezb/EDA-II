#include <stdio.h>
#include <omp.h>
#include <stdlib.h>
#define N 100000
double *A;
int flag = 0;
void fill_rand(){
    for (int i=0;i<N;i++) A[i] = (double)(rand()%100)/100.0;
}
double sum_array(){
    double s=0.0;
    for(int i=0;i<N;i++) s += A[i];
    return s;
}
int main(){
    double t0 = omp_get_wtime();
    A = malloc(sizeof(double)*N);
    #pragma omp parallel sections num_threads(2)
    {
        #pragma omp section
            {
                fill_rand();
        #pragma omp flush
        #pragma omp atomic write
                flag = 1;
        #pragma omp flush(flag)
            }
        #pragma omp section
            {
                int tmp_flag;
                while (1) {
                #pragma omp flush(flag)
                #pragma omp atomic read
                    tmp_flag = flag;
                    if (tmp_flag == 1) break;
                }
                #pragma omp flush
                double sum = sum_array();
                printf("Sum = %lf\n", sum);
            }
    }
    free(A);
    double t1 = omp_get_wtime();
    printf("Tiempo = %.3f ms\n", (t1-t0)*1000.0);
    return 0;
}
