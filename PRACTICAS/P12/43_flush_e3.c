#include <stdio.h>
#include <stdlib.h>
#include <omp.h>

#define ARRAY_SIZE 1000000
int data_array[ARRAY_SIZE];
int flag = 0;
long long sum = 0; 
double start_time;

void fill_rand() {
    printf("Hilo %d: Llenando el arreglo...\n", omp_get_thread_num());
    for (int i = 0; i < ARRAY_SIZE; i++) {
        data_array[i] = rand() % 100;
    }
}

long long sum_array() {
    long long total = 0;
    printf("Hilo %d: Sumando el arreglo...\n", omp_get_thread_num());
    for (int i = 0; i < ARRAY_SIZE; i++) {
        total += data_array[i];
    }
    return total;
}

int main() {
    start_time = omp_get_wtime();
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
                
                if (tmp_flag == 1)
                    break;
            }
            #pragma omp flush 
            sum = sum_array();
        }
    }
    double elapsed_time = omp_get_wtime() - start_time;
    printf("Estado de la bandera final (flag): %d\n", flag);
    printf("Suma total del arreglo: %lld\n", sum);
    printf("Tiempo: %.4f\n", elapsed_time);
    return 0;
}