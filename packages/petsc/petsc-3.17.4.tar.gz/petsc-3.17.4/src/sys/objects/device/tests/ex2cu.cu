static char help[] = "Benchmarking cudaPointerGetAttributes() time\n";
/*
  Running example on Summit at OLCF:
  # run with total 1 resource set (RS) (-n1), 1 RS per node (-r1), 1 MPI rank (-a1), 7 cores (-c7) and 1 GPU (-g1) per RS
  $ jsrun -n1 -a1 -c7 -g1 -r1  ./ex2cu
    Average cudaPointerGetAttributes() time = 0.29 microseconds
*/
#include <petscsys.h>
#include <petscdevice.h>

int main(int argc,char **argv)
{
  PetscInt                     i,n=2000;
  cudaError_t                  cerr;
  PetscScalar                  **ptrs;
  PetscLogDouble               tstart,tend,time;
  struct cudaPointerAttributes attr;

  PetscCall(PetscInitialize(&argc,&argv,(char*)0,help));
  PetscCall(PetscOptionsGetInt(NULL,NULL,"-n",&n,NULL));

  PetscCall(PetscMalloc1(n,&ptrs));
  for (i=0; i<n; i++) {
    if (i%2) PetscCall(PetscMalloc1(i+16,&ptrs[i]));
    else PetscCallCUDA(cudaMalloc((void**)&ptrs[i],(i+16)*sizeof(PetscScalar)));
  }

  PetscCall(PetscTime(&tstart));
  for (i=0; i<n; i++) {
    cerr = cudaPointerGetAttributes(&attr,ptrs[i]);
    if (cerr) cudaGetLastError();
  }
  PetscCall(PetscTime(&tend));
  time = (tend-tstart)*1e6/n;

  PetscCall(PetscPrintf(PETSC_COMM_WORLD,"Average cudaPointerGetAttributes() time = %.2f microseconds\n",time));

  for (i=0; i<n; i++) {
    if (i%2) PetscCall(PetscFree(ptrs[i]));
    else PetscCallCUDA(cudaFree(ptrs[i]));
  }
  PetscCall(PetscFree(ptrs));

  PetscCall(PetscFinalize());
  return 0;
}

/*TEST
  build:
    requires: cuda

  test:
    requires: cuda
    args: -n 2
    output_file: output/empty.out
    filter: grep "DOES_NOT_EXIST"

TEST*/
