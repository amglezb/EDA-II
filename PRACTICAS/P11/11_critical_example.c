#include <stdio.h>
#include <omp.h>
float big_job(int i){ float s=0; for(long k=0;k<100000;k++) s += (k%3); return s; }
float consume(float v){ return v*0.1f; }
int main(){
    double t0 = omp_get_wtime();
    int niters = 10;
    float res = 0;
    #pragma omp parallel
    {
        float B;
        int i, id, nthrds;
        id = omp_get_thread_num();
        nthrds = omp_get_num_threads();
        for (i=id ; i<niters ; i+=nthrds){
            B = big_job(i);
    #pragma omp critical
            res += consume(B);
        }
    }
    printf("res = %f\n", res);
    double t1 = omp_get_wtime();
    printf("Tiempo = %.3f ms\n", (t1-t0)*1000.0);
    return 0;
}
