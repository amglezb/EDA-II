#include<stdio.h>
#include<omp.h>
#include<unistd.h>
void do_it() {
    double i_time, f_time;
    int thread_id = omp_get_thread_num();
    i_time = omp_get_wtime();
    volatile double dummy = 0.0;
    for (int i = 0; i < 50000; i++) {
        dummy += (double)i * 0.000001;
    }
    f_time = omp_get_wtime();
    printf("task-barrier -> %d: %f [s]\n", thread_id, f_time - i_time);
}
void end_it() {
    double i_time, f_time;
    int thread_id = omp_get_thread_num();
    i_time = omp_get_wtime();
    volatile double dummy = 0.0;
    for (int i = 0; i < 1500000; i++) {
        dummy += (double)i * 0.000001;
    }
    f_time = omp_get_wtime();
    printf("single-task -> %d: %f [s]\n", thread_id, f_time - i_time);
}
int main(){
    double i_time, f_time;
    i_time = omp_get_wtime();
    #pragma omp parallel
    {
        #pragma omp task
        do_it();
        #pragma omp barrier
        #pragma omp master
        printf("Single %d\n", omp_get_thread_num());
        #pragma omp single
        {
            #pragma omp task
            end_it();
        }
    }
    f_time = omp_get_wtime();
    printf("\nTime:%f", f_time - i_time);
    return 0;
}