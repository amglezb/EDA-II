#include <stdio.h>
#include <omp.h>
void func(){
    int tmp = 0;
    #pragma omp parallel for firstprivate(tmp)
    for (int j = 0; j<1000; ++j) {
        tmp += j;
    }
    printf("tmp (example) = %d\n", tmp);
}
int main(){ double t0 = omp_get_wtime(); func(); double t1 = omp_get_wtime(); printf("Tiempo = %.3f ms\n", (t1-t0)*1000.0); return 0; }
