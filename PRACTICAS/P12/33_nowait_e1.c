#include <stdio.h>
#include <omp.h>
#include <stdlib.h>

#define NUM_THREADS 4
#define TAM 100

double work1(int id) {
    return (double)id * 1.5;
}

double work2(int i, double *A) {
    return (double)i / 10.0;
}

double work3(double *C, int i) {
    return C[i] * 2.0;
}

double work4(int id) {
    return (double)id * 100.0;
}

int main() {
    double t0 = omp_get_wtime();
    double *A, *B, *C;
    int i;
    
    A = (double*)malloc(NUM_THREADS * sizeof(double));
    B = (double*)malloc(TAM * sizeof(double));
    C = (double*)malloc(TAM * sizeof(double));

    for (i = 0; i < NUM_THREADS; i++) {
        A[i] = 0.0;
    }
    
    omp_set_num_threads(NUM_THREADS);

    #pragma omp parallel shared(A, B, C) private(i)
    {
        int id;

        id = omp_get_thread_num();
        
        A[id] = work1(id);
        printf("Thread %d finish work1\n", id);

        #pragma omp barrier

        #pragma omp for
        for (i = 0; i < TAM; i++){
            C[i] = work2(i, A); 
        }
        printf("Thread %d finish work2\n", id);
        
        #pragma omp for nowait
        for (i = 0; i < TAM; i++){
            B[i] = work3(C, i);
        }
        printf("Thread %d finish work3\n", id);
        
        A[id] = work4(id);
        printf("Thread %d finish work4\n", id);
    }

    printf("\n--- Verificación de Resultados ---\n");
    for (i = 0; i < NUM_THREADS; i++) {
        printf("A[%d] = %f\n", i, A[i]);
    }
    printf("B[0] = %f, B[TAM-1] = %f\n", B[0], B[TAM-1]);
    
    free(A);
    free(B);
    free(C);
    double t1 = omp_get_wtime();
    printf("Tiempo = %.3f ms\n", (t1-t0)*1000.0);
    return 0;
}