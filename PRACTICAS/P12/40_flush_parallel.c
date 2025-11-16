#include <stdio.h>
#include <stdlib.h>
#include <omp.h>
#include <time.h>

#define N 10000000 
double *A;
int flag = 0;

void fill_rand() {
    srand(time(NULL)); 
    int i;
    for (i = 0; i < N; i++) {
        A[i] = (double)rand() / RAND_MAX;
    }
}

double sum_array() {
    double total_sum = 0.0;
    int i;
    for (i = 0; i < N; i++) {
        total_sum += A[i];
    }
    return total_sum;
}

int main(){
    double sum = 0.0, runtime;
    A = (double *) malloc(N * sizeof(double));
    if (A == NULL) {
        printf("Error: No se pudo asignar memoria para el arreglo A.\n");
        return 1;
    }
    runtime = omp_get_wtime();
    #pragma omp parallel sections num_threads(2)
    {
        #pragma omp section
        {
            fill_rand(); 
            #pragma omp flush 
            flag = 1;         
            #pragma omp flush(flag) 
        }
        #pragma omp section
        {
            #pragma omp flush(flag) 
            while (flag == 0) {
                #pragma omp flush(flag) 
            }
            
            #pragma omp flush 
            sum = sum_array();
        }
    }
    runtime = omp_get_wtime() - runtime;
    printf("Sum = %lf\nTime = %lf\n", sum, runtime);
    free(A);
    return 0;
}