#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <omp.h>
#define N 500
#define RA N
#define CA N
#define CB N
#define RB N
void multiply_parallel(int A[RA][CA], int B[RB][CB], int C[RA][CB]) {
    int i, j, k, suma;
    #pragma omp parallel for private(i, k, suma)
    for (j=0; j<RA; j++){
        for (i=0; i<CB; i++){
            suma = 0;
            for (k=0; k<CA; k++){
                suma += A[j][k] * B[k][i];
            }
            C[j][i] = suma;
        }
    }
}
void initialize_matrices(int A[RA][CA], int B[RB][CB]) {
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            A[i][j] = rand() % 10;
            B[i][j] = rand() % 10;
        }
    }
}
int main() {
    int A[RA][CA], B[RB][CB], C[RA][CB];
    double start_time, end_time;
    srand(time(NULL));
    initialize_matrices(A, B);
    start_time = omp_get_wtime();
    multiply_parallel(A, B, C);
    end_time = omp_get_wtime();
    printf("--- Multiplicacion Paralela (%dx%d) ---\n", N, N);
    printf("Hilos usados: %d\n", omp_get_max_threads());
    printf("Tiempo: %f segundos\n", end_time - start_time);
    return 0;
}