#include <stdio.h>
#include <omp.h>
#define N 1000
int main(){
    double t0 = omp_get_wtime();
    int a[N], b[N], i;
    omp_lock_t locka, lockb;
    omp_init_lock(&locka);
    omp_init_lock(&lockb);
    #pragma omp sections nowait
    {
        #pragma omp section
        {
            omp_set_lock(&locka);
            for (i=0; i<N; i++) a[i] = i;
            omp_set_lock(&lockb);
            for (i=0; i<N; i++) b[i] = N - a[i];
            omp_unset_lock(&lockb);
            omp_unset_lock(&locka);
        }
        #pragma omp section
        {
            omp_set_lock(&lockb);
            for (i=0; i<N; i++) b[i] = N-i;
            omp_set_lock(&locka);
            for (i=0; i<N; i++) a[i] = b[i] + i;
            omp_unset_lock(&locka);
            omp_unset_lock(&lockb);
        }
    }
    omp_destroy_lock(&locka);
    omp_destroy_lock(&lockb);
    printf("Completed sections. a[0]=%d b[0]=%d\n", a[0], b[0]);
    double t1 = omp_get_wtime();
    printf("Tiempo = %.3f ms\n", (t1-t0)*1000.0);
    return 0;
}
