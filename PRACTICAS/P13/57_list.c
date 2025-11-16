#include <stdio.h>
#include <stdlib.h>
#include <omp.h>
typedef struct item {
    int id;
    struct item *next;
} item;
item* create_item(int id, item *next_item) {
    item *new_item = (item *)malloc(sizeof(item));
    new_item->id = id;
    new_item->next = next_item;
    return new_item;
}
int main() {
    item *list = NULL;
    for (int i = 1; i <= 5; i++) {
        list = create_item(i, list);
    }
    omp_set_num_threads(4);
    #pragma omp parallel
    {
        #pragma omp single
        {
            struct item *p = list;

            while (p != NULL) {
                #pragma omp task firstprivate(p)
                {
                    int next_id = (p->next != NULL) ? p->next->id : -1;
                    
                    printf("Hilo ID: %d | Nodo ID: %d -> Siguiente ID: %d\n", 
                           omp_get_thread_num(), p->id, next_id);
                }
                p = (*p).next;
            }
        }
        #pragma omp taskwait
    }
    item *current = list;
    item *next;
    while (current != NULL) {
        next = current->next;
        free(current);
        current = next;
    }
    return 0;
}