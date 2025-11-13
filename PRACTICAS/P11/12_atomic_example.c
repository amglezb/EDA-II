#include <stdio.h>
#include <omp.h>
double funcBig(double v){ double s=0; for(long k=0;k<200000;k++) s += v*(k%5); return s; }
double getNumber(){ return 1.0; }
int main(){
    double t0 = omp_get_wtime();
    int A = 0;
    #pragma omp parallel
    {
        double tmp, B;
        B = getNumber();
        tmp = funcBig(B);
    #pragma omp atomic
        A += (int)tmp;
    }
    printf("A = %d\n", A);
    double t1 = omp_get_wtime();
    printf("Tiempo = %.3f ms\n", (t1-t0)*1000.0);
    return 0;
}
