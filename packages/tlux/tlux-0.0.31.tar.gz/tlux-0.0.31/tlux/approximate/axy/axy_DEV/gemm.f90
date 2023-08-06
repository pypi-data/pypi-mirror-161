SUBROUTINE SGEMM(OP_A, OP_B, OUT_ROWS, OUT_COLS, INNER_DIM, &
     AB_MULT, A, A_ROWS, B, B_ROWS, C_MULT, C, C_ROWS) BIND(C)
  CHARACTER :: OP_A, OP_B
  INTEGER :: OUT_ROWS, OUT_COLS, INNER_DIM, A_ROWS, B_ROWS, C_ROWS
  REAL :: AB_MULT, C_MULT
  REAL, DIMENSION(*) :: A
  REAL, DIMENSION(*) :: B
  REAL, DIMENSION(*) :: C
  ! Fortran intrinsic version of general matrix multiplication routine,
  !   first compute the initial values in the output matrix,
  C(:,:) = C_MULT * C(:,:)
  !   then compute the matrix multiplication.
  IF (OP_A .EQ. 'N') THEN
     IF (OP_B .EQ. 'N') THEN
        C(:,:) = C(:,:) + AB_MULT * MATMUL(A(:,:), B(:,:))
     ELSE
        C(:,:) = C(:,:) + AB_MULT * MATMUL(A(:,:), TRANSPOSE(B(:,:)))
     END IF
  ELSE
     IF (OP_B .EQ. 'N') THEN
        C(:,:) = C(:,:) + AB_MULT * MATMUL(TRANSPOSE(A(:,:)), B(:,:))
     ELSE
        C(:,:) = C(:,:) + AB_MULT * MATMUL(TRANSPOSE(A(:,:)), TRANSPOSE(B(:,:)))
     END IF
  END IF
END SUBROUTINE SGEMM

