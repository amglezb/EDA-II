#include<stdio.h>
#include<omp.h>
#define MAX 5
int main() {
    double ave=0.0, A[MAX];
    int i;
    for (i=0; i<MAX; i++) {
        A[i] = i+1.0;
    }
    double i_time, f_time;
    i_time = omp_get_wtime();
    #pragma omp parallel for reduction(+: ave)
    for (i=0; i<MAX; i++) {
        ave += A[i];
    }
    ave /= MAX;
    f_time = omp_get_wtime();
    printf("%f\nTime:%f", ave, f_time - i_time);
    return 0;
}