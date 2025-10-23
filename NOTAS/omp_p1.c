#include <stdio.h>
#include <omp.h>

int main(){
	#pragma omp parallel
	{
		int id_hilo = omp_get_thread_num();
		int total_hilos = omp_get_num_threads();
		#pragma omp critical
		{
			printf("Hola Mundo desde el hilo %d de %d\n", id_hilo, total_hilos);
		}
	}
	return 0;
}
