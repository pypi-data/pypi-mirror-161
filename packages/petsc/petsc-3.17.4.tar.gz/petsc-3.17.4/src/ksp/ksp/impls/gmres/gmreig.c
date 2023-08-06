
#include <../src/ksp/ksp/impls/gmres/gmresimpl.h>
#include <petscblaslapack.h>

PetscErrorCode KSPComputeExtremeSingularValues_GMRES(KSP ksp,PetscReal *emax,PetscReal *emin)
{
  KSP_GMRES      *gmres = (KSP_GMRES*)ksp->data;
  PetscInt       n = gmres->it + 1,i,N = gmres->max_k + 2;
  PetscBLASInt   bn, bN,lwork, idummy,lierr;
  PetscScalar    *R        = gmres->Rsvd,*work = R + N*N,sdummy = 0;
  PetscReal      *realpart = gmres->Dsvd;

  PetscFunctionBegin;
  PetscCall(PetscBLASIntCast(n,&bn));
  PetscCall(PetscBLASIntCast(N,&bN));
  PetscCall(PetscBLASIntCast(5*N,&lwork));
  PetscCall(PetscBLASIntCast(N,&idummy));
  if (n <= 0) {
    *emax = *emin = 1.0;
    PetscFunctionReturn(0);
  }
  /* copy R matrix to work space */
  PetscCall(PetscArraycpy(R,gmres->hh_origin,(gmres->max_k+2)*(gmres->max_k+1)));

  /* zero below diagonal garbage */
  for (i=0; i<n; i++) R[i*N+i+1] = 0.0;

  /* compute Singular Values */
  PetscCall(PetscFPTrapPush(PETSC_FP_TRAP_OFF));
#if !defined(PETSC_USE_COMPLEX)
  PetscStackCallBLAS("LAPACKgesvd",LAPACKgesvd_("N","N",&bn,&bn,R,&bN,realpart,&sdummy,&idummy,&sdummy,&idummy,work,&lwork,&lierr));
#else
  PetscStackCallBLAS("LAPACKgesvd",LAPACKgesvd_("N","N",&bn,&bn,R,&bN,realpart,&sdummy,&idummy,&sdummy,&idummy,work,&lwork,realpart+N,&lierr));
#endif
  PetscCheck(!lierr,PETSC_COMM_SELF,PETSC_ERR_LIB,"Error in SVD Lapack routine %d",(int)lierr);
  PetscCall(PetscFPTrapPop());

  *emin = realpart[n-1];
  *emax = realpart[0];
  PetscFunctionReturn(0);
}

PetscErrorCode KSPComputeEigenvalues_GMRES(KSP ksp,PetscInt nmax,PetscReal *r,PetscReal *c,PetscInt *neig)
{
#if !defined(PETSC_USE_COMPLEX)
  KSP_GMRES      *gmres = (KSP_GMRES*)ksp->data;
  PetscInt       n = gmres->it + 1,N = gmres->max_k + 1,i,*perm;
  PetscBLASInt   bn, bN, lwork, idummy, lierr = -1;
  PetscScalar    *R        = gmres->Rsvd,*work = R + N*N;
  PetscScalar    *realpart = gmres->Dsvd,*imagpart = realpart + N,sdummy = 0;

  PetscFunctionBegin;
  PetscCall(PetscBLASIntCast(n,&bn));
  PetscCall(PetscBLASIntCast(N,&bN));
  PetscCall(PetscBLASIntCast(5*N,&lwork));
  PetscCall(PetscBLASIntCast(N,&idummy));
  PetscCheckFalse(nmax < n,PetscObjectComm((PetscObject)ksp),PETSC_ERR_ARG_SIZ,"Not enough room in work space r and c for eigenvalues");
  *neig = n;

  if (!n) PetscFunctionReturn(0);

  /* copy R matrix to work space */
  PetscCall(PetscArraycpy(R,gmres->hes_origin,N*N));

  /* compute eigenvalues */
  PetscCall(PetscFPTrapPush(PETSC_FP_TRAP_OFF));
  PetscStackCallBLAS("LAPACKgeev",LAPACKgeev_("N","N",&bn,R,&bN,realpart,imagpart,&sdummy,&idummy,&sdummy,&idummy,work,&lwork,&lierr));
  PetscCheck(!lierr,PETSC_COMM_SELF,PETSC_ERR_LIB,"Error in LAPACK routine %d",(int)lierr);
  PetscCall(PetscFPTrapPop());
  PetscCall(PetscMalloc1(n,&perm));
  for (i=0; i<n; i++) perm[i] = i;
  PetscCall(PetscSortRealWithPermutation(n,realpart,perm));
  for (i=0; i<n; i++) {
    r[i] = realpart[perm[i]];
    c[i] = imagpart[perm[i]];
  }
  PetscCall(PetscFree(perm));
#else
  KSP_GMRES      *gmres = (KSP_GMRES*)ksp->data;
  PetscInt       n  = gmres->it + 1,N = gmres->max_k + 1,i,*perm;
  PetscScalar    *R = gmres->Rsvd,*work = R + N*N,*eigs = work + 5*N,sdummy;
  PetscBLASInt   bn,bN,lwork,idummy,lierr = -1;

  PetscFunctionBegin;
  PetscCall(PetscBLASIntCast(n,&bn));
  PetscCall(PetscBLASIntCast(N,&bN));
  PetscCall(PetscBLASIntCast(5*N,&lwork));
  PetscCall(PetscBLASIntCast(N,&idummy));
  PetscCheck(nmax >= n,PetscObjectComm((PetscObject)ksp),PETSC_ERR_ARG_SIZ,"Not enough room in work space r and c for eigenvalues");
  *neig = n;

  if (!n) PetscFunctionReturn(0);

  /* copy R matrix to work space */
  PetscCall(PetscArraycpy(R,gmres->hes_origin,N*N));

  /* compute eigenvalues */
  PetscCall(PetscFPTrapPush(PETSC_FP_TRAP_OFF));
  PetscStackCallBLAS("LAPACKgeev",LAPACKgeev_("N","N",&bn,R,&bN,eigs,&sdummy,&idummy,&sdummy,&idummy,work,&lwork,gmres->Dsvd,&lierr));
  PetscCheck(!lierr,PETSC_COMM_SELF,PETSC_ERR_LIB,"Error in LAPACK routine");
  PetscCall(PetscFPTrapPop());
  PetscCall(PetscMalloc1(n,&perm));
  for (i=0; i<n; i++) perm[i] = i;
  for (i=0; i<n; i++) r[i] = PetscRealPart(eigs[i]);
  PetscCall(PetscSortRealWithPermutation(n,r,perm));
  for (i=0; i<n; i++) {
    r[i] = PetscRealPart(eigs[perm[i]]);
    c[i] = PetscImaginaryPart(eigs[perm[i]]);
  }
  PetscCall(PetscFree(perm));
#endif
  PetscFunctionReturn(0);
}

#if !defined(PETSC_USE_COMPLEX)
PetscErrorCode KSPComputeRitz_GMRES(KSP ksp,PetscBool ritz,PetscBool small,PetscInt *nrit,Vec S[],PetscReal *tetar,PetscReal *tetai)
{
  KSP_GMRES      *gmres = (KSP_GMRES*)ksp->data;
  PetscInt       n = gmres->it + 1,N = gmres->max_k + 1,NbrRitz,nb=0;
  PetscInt       i,j,*perm;
  PetscReal      *H,*Q,*Ht;              /* H Hessenberg Matrix and Q matrix of eigenvectors of H*/
  PetscReal      *wr,*wi,*modul;       /* Real and imaginary part and modul of the Ritz values*/
  PetscReal      *SR,*work;
  PetscBLASInt   bn,bN,lwork,idummy;
  PetscScalar    *t,sdummy = 0;

  PetscFunctionBegin;
  /* n: size of the Hessenberg matrix */
  if (gmres->fullcycle) n = N-1;
  /* NbrRitz: number of (harmonic) Ritz pairs to extract */
  NbrRitz = PetscMin(*nrit,n);

  /* Definition of PetscBLASInt for lapack routines*/
  PetscCall(PetscBLASIntCast(n,&bn));
  PetscCall(PetscBLASIntCast(N,&bN));
  PetscCall(PetscBLASIntCast(N,&idummy));
  PetscCall(PetscBLASIntCast(5*N,&lwork));
  /* Memory allocation */
  PetscCall(PetscMalloc1(bN*bN,&H));
  PetscCall(PetscMalloc1(bn*bn,&Q));
  PetscCall(PetscMalloc1(lwork,&work));
  PetscCall(PetscMalloc1(n,&wr));
  PetscCall(PetscMalloc1(n,&wi));

  /* copy H matrix to work space */
  if (gmres->fullcycle) {
    PetscCall(PetscArraycpy(H,gmres->hes_ritz,bN*bN));
  } else {
    PetscCall(PetscArraycpy(H,gmres->hes_origin,bN*bN));
  }

  /* Modify H to compute Harmonic Ritz pairs H = H + H^{-T}*h^2_{m+1,m}e_m*e_m^T */
  if (!ritz) {
    /* Transpose the Hessenberg matrix => Ht */
    PetscCall(PetscMalloc1(bn*bn,&Ht));
    for (i=0; i<bn; i++) {
      for (j=0; j<bn; j++) {
        Ht[i*bn+j] = H[j*bN+i];
      }
    }
    /* Solve the system H^T*t = h^2_{m+1,m}e_m */
    PetscCall(PetscCalloc1(bn,&t));
    /* t = h^2_{m+1,m}e_m */
    if (gmres->fullcycle) {
      t[bn-1] = PetscSqr(gmres->hes_ritz[(bn-1)*bN+bn]);
    } else {
      t[bn-1] = PetscSqr(gmres->hes_origin[(bn-1)*bN+bn]);
    }
    /* Call the LAPACK routine dgesv to compute t = H^{-T}*t */
    {
      PetscBLASInt info;
      PetscBLASInt nrhs = 1;
      PetscBLASInt *ipiv;
      PetscCall(PetscMalloc1(bn,&ipiv));
      PetscStackCallBLAS("LAPACKgesv",LAPACKgesv_(&bn,&nrhs,Ht,&bn,ipiv,t,&bn,&info));
      PetscCheck(!info,PetscObjectComm((PetscObject)ksp),PETSC_ERR_PLIB,"Error while calling the Lapack routine DGESV");
      PetscCall(PetscFree(ipiv));
      PetscCall(PetscFree(Ht));
    }
    /* Now form H + H^{-T}*h^2_{m+1,m}e_m*e_m^T */
    for (i=0; i<bn; i++) H[(bn-1)*bn+i] += t[i];
    PetscCall(PetscFree(t));
  }

  /* Compute (harmonic) Ritz pairs */
  {
    PetscBLASInt info;
    PetscCall(PetscFPTrapPush(PETSC_FP_TRAP_OFF));
    PetscStackCallBLAS("LAPACKgeev",LAPACKgeev_("N","V",&bn,H,&bN,wr,wi,&sdummy,&idummy,Q,&bn,work,&lwork,&info));
    PetscCheck(!info,PETSC_COMM_SELF,PETSC_ERR_LIB,"Error in LAPACK routine");
  }
  /* sort the (harmonic) Ritz values */
  PetscCall(PetscMalloc1(n,&modul));
  PetscCall(PetscMalloc1(n,&perm));
  for (i=0; i<n; i++) modul[i] = PetscSqrtReal(wr[i]*wr[i]+wi[i]*wi[i]);
  for (i=0; i<n; i++) perm[i] = i;
  PetscCall(PetscSortRealWithPermutation(n,modul,perm));
  /* count the number of extracted Ritz or Harmonic Ritz pairs (with complex conjugates) */
  if (small) {
    while (nb < NbrRitz) {
      if (!wi[perm[nb]]) nb += 1;
      else nb += 2;
    }
    PetscCall(PetscMalloc1(nb*n,&SR));
    for (i=0; i<nb; i++) {
      tetar[i] = wr[perm[i]];
      tetai[i] = wi[perm[i]];
      PetscCall(PetscArraycpy(&SR[i*n],&(Q[perm[i]*bn]),n));
    }
  } else {
    while (nb < NbrRitz) {
      if (wi[perm[n-nb-1]] == 0) nb += 1;
      else nb += 2;
    }
    PetscCall(PetscMalloc1(nb*n,&SR));
    for (i=0; i<nb; i++) {
      tetar[i] = wr[perm[n-nb+i]];
      tetai[i] = wi[perm[n-nb+i]];
      PetscCall(PetscArraycpy(&SR[i*n], &(Q[perm[n-nb+i]*bn]), n));
    }
  }
  PetscCall(PetscFree(modul));
  PetscCall(PetscFree(perm));

  /* Form the Ritz or Harmonic Ritz vectors S=VV*Sr,
    where the columns of VV correspond to the basis of the Krylov subspace */
  if (gmres->fullcycle) {
    for (j=0; j<nb; j++) {
      PetscCall(VecZeroEntries(S[j]));
      PetscCall(VecMAXPY(S[j],n,&SR[j*n],gmres->vecb));
    }
  } else {
    for (j=0; j<nb; j++) {
      PetscCall(VecZeroEntries(S[j]));
      PetscCall(VecMAXPY(S[j],n,&SR[j*n],&VEC_VV(0)));
    }
  }
  *nrit = nb;
  PetscCall(PetscFree(H));
  PetscCall(PetscFree(Q));
  PetscCall(PetscFree(SR));
  PetscCall(PetscFree(wr));
  PetscCall(PetscFree(wi));
  PetscFunctionReturn(0);
}
#endif
