#include <stdio.h>
#include <stdlib.h>
#include <omp.h>
#define RA 500
#define CA 1000
#define CB 500
int A[RA][CA];
int B[CA][CB];
int C[RA][CB];
void initialize_matrices() {
    int i, j;
    for (i = 0; i < RA; i++) {
        for (j = 0; j < CA; j++) {
            A[i][j] = rand() % 10;
        }
    }
    for (i = 0; i < CA; i++) {
        for (j = 0; j < CB; j++) {
            B[i][j] = rand() % 10;
        }
    }
    for (i = 0; i < RA; i++) {
        for (j = 0; j < CB; j++) {
            C[i][j] = 0;
        }
    }
}
void multiply_serial() {
    int i, j, k, suma;
    for (i = 0; i < RA; i++) {
        for (j = 0; j < CB; j++) {
            suma = 0;
            for (k = 0; k < CA; k++) {
                suma += A[i][k] * B[k][j];
            }
            C[i][j] = suma;
        }
    }
}

int main() {
    double inicio, fin;
    initialize_matrices();
    inicio = omp_get_wtime();
    multiply_serial();
    fin = omp_get_wtime();
    printf("Tiempo: %f\n", fin - inicio);
    return 0;
}