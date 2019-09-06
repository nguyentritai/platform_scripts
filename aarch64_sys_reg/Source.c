#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <sys/time.h>

/* TODO: Define macro for these system register read */

/* D-Cache flush */
static inline void dccivac(uint64_t v)
{                                    
       __asm__ ("isb");
       __asm__ ("dsb sy");
       __asm__ ("dc civac, %0" : : "r" (v));
       __asm__ ("dsb sy");
       __asm__ ("isb");
}                                                                       

static inline uint64_t cntvct_el0_rd(void)
{
       uint64_t cval;

       __asm__ ("isb");
       __asm__ ("dsb sy");
       __asm__ volatile("mrs %0, cntvct_el0" : "=r" (cval));
       __asm__ ("dsb sy");
       __asm__ ("isb");

       return cval;
}

static inline uint64_t cntfrq_el0_rd(void)
{
       uint64_t cval;

       __asm__ ("isb");
       __asm__ ("dsb sy");
       __asm__ volatile("mrs %0, cntfrq_el0" : "=r" (cval));
       __asm__ ("dsb sy");
       __asm__ ("isb");

       return cval;
}

static inline uint64_t mdir_el1_rd(void)
{
       uint64_t cval;

       __asm__ ("isb");
       __asm__ ("dsb sy");
       __asm__ volatile("mrs %0, midr_el1" : "=r" (cval));
       __asm__ ("dsb sy");
       __asm__ ("isb");

       return cval;
}

static inline uint64_t mpidr_el1_rd(void)
{
       uint64_t cval;

       __asm__ ("isb");
       __asm__ ("dsb sy");
       __asm__ volatile("mrs %0, mpidr_el1" : "=r" (cval));
       __asm__ ("dsb sy");
       __asm__ ("isb");

       return cval;
}

int main(int argc, const char* * argv)
{
	/* Counter-timer Frequency register */
	printf("cntfrq_el0 0x%llx\n", cntfrq_el0_rd());
	/* Counter-timer Virtual Count register */
	printf("cntvct_el0 0x%llx\n", cntvct_el0_rd());
	/* Main ID Register */
	printf("mdir_el1 0x%llx\n", mdir_el1_rd());
	/* Multiprocessor Affinity Register */
	printf("mpidr_el1 0x%llx\n", mpidr_el1_rd());
	return 0;
}
