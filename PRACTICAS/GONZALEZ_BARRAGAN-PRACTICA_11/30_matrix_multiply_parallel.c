#include <stdio.h>
#include <stdlib.h>
#include <omp.h>
void multiply_par(int RA, int CA, int RB, int CB, int a[], int b[], int c[]) {
    #pragma omp parallel for
    for (int i=0;i<RA;i++)
        for (int j=0;j<CB;j++) {
            int sum = 0;
            for (int k=0;k<CA;k++)
                sum += a[i*CA + k] * b[k*CB + j];
            c[i*CB + j] = sum;
        }
}
int main(){
    double t0 = omp_get_wtime();
    int RA=400, CA=400, RB=400, CB=400;
    int *a = malloc(RA*CA*sizeof(int));
    int *b = malloc(RB*CB*sizeof(int));
    int *c = malloc(RA*CB*sizeof(int));
    for (int i=0;i<RA*CA;i++) a[i]=i%5;
    for (int i=0;i<RB*CB;i++) b[i]=i%7;
    multiply_par(RA,CA,RB,CB,a,b,c);
    printf("c[0]=%d c[1]=%d\n", c[0], c[1]);
    free(a); free(b); free(c);
    double t1 = omp_get_wtime();
    printf("Tiempo = %.3f ms\n", (t1-t0)*1000.0);
    return 0;
}
