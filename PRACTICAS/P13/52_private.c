#include <stdio.h>
#include <omp.h>
void wrong_func(){
    int tmp = 0;
    #pragma omp parallel private(tmp)
    {
        #pragma omp for
        for (int j = 0; j<1000; ++j)
            tmp += j;
        
        printf("%d: %d\n", omp_get_thread_num(), tmp);
    }
    printf("%d\n", tmp);
}

int main(){
    double i_time, f_time;
    i_time = omp_get_wtime();
    wrong_func();
    f_time = omp_get_wtime();
    printf("Time:%f", f_time - i_time);
    return 0;
}