#include <stdio.h>
#include <omp.h>
#define MAX 5
int main() {
    double t0 = omp_get_wtime();
    double ave=0.0, A[MAX];
    int i;
    for (i=0; i<MAX; i++) {
        A[i] = i+1.0;
    }
    #pragma omp parallel for reduction(+: ave)
    for (i=0; i<MAX; i++) {
        ave += A[i];
    }
    ave /= MAX;
    printf("%f\n",ave);
    double t1 = omp_get_wtime();
    printf("Tiempo = %.3f ms\n", (t1-t0)*1000.0);
    return 0;
}
