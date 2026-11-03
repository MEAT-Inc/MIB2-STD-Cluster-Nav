#include <time.h>
int main(void){struct timespec t={1,0};for(;;)nanosleep(&t,0);}
