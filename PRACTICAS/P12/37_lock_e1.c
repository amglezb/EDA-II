#include <stdio.h>
#include <stdlib.h>
#include <omp.h>
#define NUM_VALUES 20
int NUM_BUCKETS = 0;

int take_a_number(){
	return rand()%NUM_BUCKETS;
}

int main() {
	int i;
	double start_time, end_time;
	omp_set_dynamic(0);
	NUM_BUCKETS = omp_get_num_procs();
	omp_set_num_threads(NUM_BUCKETS);
	printf("Buckets number = %d\n", NUM_BUCKETS);
	omp_lock_t hist_locks[NUM_BUCKETS];
	int hist[NUM_BUCKETS];
	start_time = omp_get_wtime();
	#pragma omp parallel for
	for (i=0; i<NUM_BUCKETS; i++){
		omp_init_lock(&hist_locks[i]);
		hist[i] = 0;
	}
	#pragma omp parallel for
	for (i=0; i<NUM_VALUES; i++){
		int id = omp_get_thread_num();
		printf("Thread %d\n", id);
		int val = take_a_number();
		omp_set_lock(&hist_locks[val]);
		hist[val]++;
		omp_unset_lock(&hist_locks[val]);
	}
	end_time = omp_get_wtime();
	for (i=0; i<NUM_BUCKETS; i++){
		printf("hist[%d] = %d\n", i, hist[i]);
		omp_destroy_lock(&hist_locks[i]);
	}
	printf("Total execution time: %f seconds\n", end_time - start_time);
	
	return 0;
}