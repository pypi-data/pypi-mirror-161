
#requiresdefine   'PETSC_HAVE_FORTRAN'
ALL: lib

CFLAGS   =
FFLAGS   =
SOURCEC  = taosolverf.c taosolver_boundsf.c taosolver_fgf.c taosolver_hjf.c
SOURCEF  =
SOURCEH  = 
DIRS     =
LIBBASE  = libpetsctao
LOCDIR   = src/tao/interface/ftn-auto/
include ${PETSC_DIR}/lib/petsc/conf/variables
include ${PETSC_DIR}/lib/petsc/conf/rules
include ${PETSC_DIR}/lib/petsc/conf/test
