void multiply(int A[RA][CA], int B[RB][CB], int C[RA][CB]) {
    int i, j, k, suma;
    for (i = 0; i < CB; i++){
        for (j = 0; j < RA; j++){
            suma = 0;
            for (k = 0; k < CA; k++){
                suma += A[j][k] * B[k][i];
                C[j][i] = suma;
            }
        }
    }
}