#include <stdio.h>
#include <omp.h>
void do_it(){ int k; for(k=0;k<500000;k++); printf("do_it done by %d\n", omp_get_thread_num()); }
void end_it(){ int k; for(k=0;k<200000;k++); printf("end_it done by %d\n", omp_get_thread_num()); }
int main(){
    double t0 = omp_get_wtime();
    #pragma omp parallel
    {
        #pragma omp single
        {
        #pragma omp task
            do_it();
        #pragma omp task
            end_it();
        }
        #pragma omp barrier
    }
    double t1 = omp_get_wtime();
    printf("Tiempo = %.3f ms\n", (t1-t0)*1000.0);
    return 0;
}
