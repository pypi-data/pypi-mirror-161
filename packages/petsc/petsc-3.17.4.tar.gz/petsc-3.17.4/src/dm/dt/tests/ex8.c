const char help[] = "Tests PetscDTBaryToIndex(), PetscDTIndexToBary(), PetscDTIndexToGradedOrder() and PetscDTGradedOrderToIndex()";

#include <petsc/private/petscimpl.h>
#include <petsc/private/dtimpl.h>
#include <petsc/private/petscfeimpl.h>

int main(int argc, char **argv)
{
  PetscInt       d, n, maxdim = 4;
  PetscInt       *btupprev, *btup;
  PetscInt       *gtup;

  PetscCall(PetscInitialize(&argc, &argv, NULL, help));
  PetscCall(PetscMalloc3(maxdim + 1, &btup, maxdim + 1, &btupprev, maxdim, &gtup));
  for (d = 0; d <= maxdim; d++) {
    for (n = 0; n <= d + 2; n++) {
      PetscInt j, k, Nk, kchk;

      PetscCall(PetscDTBinomialInt(d + n, d, &Nk));
      for (k = 0; k < Nk; k++) {
        PetscInt sum;

        PetscCall(PetscDTIndexToBary(d + 1, n, k, btup));
        for (j = 0, sum = 0; j < d + 1; j++) {
          PetscCheckFalse(btup[j] < 0,PETSC_COMM_SELF, PETSC_ERR_PLIB, "PetscDTIndexToBary, d = %D, n = %D, k = %D negative entry", d, n, k);
          sum += btup[j];
        }
        PetscCheckFalse(sum != n,PETSC_COMM_SELF, PETSC_ERR_PLIB, "PetscDTIndexToBary, d = %D, n = %D, k = %D incorrect sum", d, n, k);
        PetscCall(PetscDTBaryToIndex(d + 1, n, btup, &kchk));
        PetscCheckFalse(kchk != k,PETSC_COMM_SELF, PETSC_ERR_PLIB, "PetscDTBaryToIndex, d = %D, n = %D, k = %D mismatch", d, n, k);
        if (k) {
          j = d;
          while (j >= 0 && btup[j] == btupprev[j]) j--;
          PetscCheckFalse(j < 0,PETSC_COMM_SELF, PETSC_ERR_PLIB, "PetscDTIndexToBary, d = %D, n = %D, k = %D equal to previous", d, n, k);
          PetscCheckFalse(btup[j] < btupprev[j],PETSC_COMM_SELF, PETSC_ERR_PLIB, "PetscDTIndexToBary, d = %D, n = %D, k = %D less to previous", d, n, k);
        } else {
          PetscCall(PetscArraycpy(btupprev, btup, d + 1));
        }
        PetscCall(PetscDTIndexToGradedOrder(d, Nk - 1 - k, gtup));
        PetscCall(PetscDTGradedOrderToIndex(d, gtup, &kchk));
        PetscCheckFalse(kchk != Nk - 1 - k,PETSC_COMM_SELF, PETSC_ERR_PLIB, "PetscDTGradedOrderToIndex, d = %D, n = %D, k = %D mismatch", d, n, Nk - 1 - k);
        for (j = 0; j < d; j++) {
          PetscCheckFalse(gtup[j] != btup[d - 1 - j],PETSC_COMM_SELF, PETSC_ERR_PLIB, "PetscDTIndexToGradedOrder, d = %D, n = %D, k = %D incorrect", d, n, Nk - 1 - k);
        }
      }
    }
  }
  PetscCall(PetscFree3(btup, btupprev, gtup));
  PetscCall(PetscFinalize());
  return 0;
}

/*TEST

  test:

TEST*/
