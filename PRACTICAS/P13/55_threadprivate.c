#include <stdio.h>
#include <omp.h>
int counter = 0;
#pragma omp threadprivate(counter)
int getIdthread() {
    return omp_get_thread_num();
}
int increment_counter(){
    return ++counter + getIdthread();
}
int main() {
    int num_threads = 4;
    omp_set_num_threads(num_threads);
    printf("Region paralela con %d hilos.\n", num_threads);
    #pragma omp parallel
    {
        int result1 = increment_counter();
        int result2 = increment_counter();
        int result3 = increment_counter();
        int thread_id = omp_get_thread_num();
        printf("Hilo %d: counter antes de incrementar: %d\n", thread_id, counter);
        printf("Hilo %d: Resultado 1: %d, Resultado 2: %d, Resultado 3: %d\n", thread_id, result1, result2, result3);
        printf("Hilo %d: Valor final de 'counter' privado: %d\n", thread_id, counter);
    }
    return 0;
}