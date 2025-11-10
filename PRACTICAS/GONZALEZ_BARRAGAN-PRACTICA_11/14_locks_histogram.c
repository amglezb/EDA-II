#include <stdio.h>
#include <stdlib.h>
#include <omp.h>
#define NUM_VALUES 200
int NUM_BUCKETS = 0;
int take_a_number(){
    return rand()%NUM_BUCKETS;
}
int main() {
    double t0 = omp_get_wtime();
    int i;
    omp_set_dynamic(0);
    NUM_BUCKETS = omp_get_num_procs();
    omp_set_num_threads(NUM_BUCKETS);
    printf("Buckets number = %d\n", NUM_BUCKETS);
    omp_lock_t *hist_locks = malloc(sizeof(omp_lock_t)*NUM_BUCKETS);
    int *hist = malloc(sizeof(int)*NUM_BUCKETS);
    #pragma omp parallel for
    for (i=0; i<NUM_BUCKETS; i++){
        omp_init_lock(&hist_locks[i]);
        hist[i] = 0;
    }
    #pragma omp parallel for
    for (i=0; i<NUM_VALUES; i++){
        int val = take_a_number();
        omp_set_lock(&hist_locks[val]);
        hist[val]++;
        omp_unset_lock(&hist_locks[val]);
    }
    for (i=0; i<NUM_BUCKETS; i++){
        printf("hist[%d] = %d\n", i, hist[i]);
        omp_destroy_lock(&hist_locks[i]);
    }
    free(hist_locks);
    free(hist);
    double t1 = omp_get_wtime();
    printf("Tiempo = %.3f ms\n", (t1-t0)*1000.0);
    return 0;
}
