#include <stdio.h>
#include <omp.h>
void func(){
    int tmp = 0;
    #pragma omp parallel for firstprivate(tmp)
    for (int j = 0; j<1000; ++j)
        tmp += j;
    printf("%d\n", tmp); 
}
int main(){
    double i_time, f_time;
    i_time = omp_get_wtime();
    func();
    f_time = omp_get_wtime();
    printf("Tiempo: %f\n", f_time - i_time);

    return 0;
}