program Triaxial_test
   implicit none

   ! IMPORTANT: XMAT allows to set precision in routine but uses double precision as default
   integer, parameter :: dp = selected_real_kind(15)
   character(len=80) :: materialname
   real(dp), dimension(--numparameter--) :: materialparameters
   real(dp), dimension(20) :: statevariables, inpstate, outstate
   real(dp), dimension(6) :: stress, inpstress, outstress1, outstress2
   real(dp), dimension(6) :: strain, inpstrain1, inpstrain2, refstrain
   real(dp) :: dt, totaltime, initial_voidratio, triax_pressure, modstrain
   real(dp) :: diff1, diff2
   real(dp) :: contraction, fak2, pressure_deviation, compared_strain
   real(dp), parameter :: tolerable_pressure_deviation = 0.000001_dp
   integer, parameter :: maxiter = --maxiter--
   real(dp), dimension(6, maxiter) :: sim_strains
   integer :: idx, innercounter, strainidx, filenr, stat
   logical :: breakall
   real(dp) :: starttime, endtime

   ! Decide which constitutive model to use by materialname
   materialname = '--materialname--'

   ! List material parameters to be used
   initial_voidratio = --initialvoidratio--
   materialparameters = [ &
   --materialparameters--]

   ! Time increment to be used
   dt = --timeincrement--
   totaltime = --starttime--

   ! Define initial state variables
   statevariables = 0.0_dp
   statevariables(1) = initial_voidratio

   ! After which height fraction shall the triaxial simulation end
   contraction = --triax_maxcontraction--

   ! Give initial stress and strain matrices (in vector form)
   triax_pressure = --triax_pressure--
   stress = [triax_pressure, triax_pressure, triax_pressure, 0.0_dp, 0.0_dp, 0.0_dp]
   strain = [-1.0_dp, 0.0_dp, 0.0_dp, 0.0_dp, 0.0_dp, 0.0_dp]*dt

   pressure_deviation = abs(tolerable_pressure_deviation*triax_pressure)
   fak2 = 0.0001_dp
   compared_strain = 0.0_dp
   inpstress = stress
   inpstate = statevariables


   filenr = 20
   open(filenr, file="--outfilename--.csv", iostat=stat)
   if (stat /= 0) then
      write(*, *) "Access problem during write attempt"
      close(filenr)
      stop
   end if

   ! Write output for start point as well
   write(filenr, '(f12.5, a, f12.5, a, f12.5)') 0.0, '   ', 0.0, '   ', 0.0

   idx = 1
   strainidx = 0
   sim_strains = 0.0_dp
   breakall = .False.

   call cpu_time(starttime)
   triax_compression : &
   do
      if (compared_strain > contraction) then
         exit triax_compression
      end if
      refstrain = strain
      inpstrain1 = [refstrain(1), 0.0_dp, 0.0_dp, refstrain(4), refstrain(5), refstrain(6)]
      call xmat_console(materialname, size(materialparameters), materialparameters, size(inpstate), &
                        inpstate, size(inpstrain1), inpstress, inpstrain1, dt, totaltime, outstress1, outstate)

      diff1 = outstress1(2) - inpstress(2)

      inpstrain2 = [refstrain(1), fak2*refstrain(1), fak2*refstrain(1), &
                    refstrain(4), refstrain(5), refstrain(6)]
      call xmat_console(materialname, size(materialparameters), materialparameters, size(inpstate), &
                        inpstate, size(inpstrain2), inpstress, inpstrain2, dt, totaltime, outstress2, outstate)
      diff2 = outstress2(2) - inpstress(2)
      !write(*, *) idx, ': ', diff1, ' und ', diff2

      innercounter = 0
      minimize_difference : &
      do
         if (abs(diff2) < pressure_deviation) then
            exit minimize_difference
         end if

         if (innercounter > 10) then
            write(*, *) 'Strain increment halved'
            refstrain = refstrain/2.0_dp

            inpstrain1 = [refstrain(1), 0.0_dp, 0.0_dp, &
                           refstrain(4), refstrain(5), refstrain(6)]
            call xmat_console(materialname, size(materialparameters), materialparameters, size(inpstate), &
                              inpstate, size(inpstrain1), inpstress, inpstrain1, dt, totaltime, outstress1, outstate)
            diff1 = outstress1(2) - inpstress(2)

            inpstrain2 = [refstrain(1), fak2*refstrain(1), fak2*refstrain(1), &
                           refstrain(4), refstrain(5), refstrain(6)]
            call xmat_console(materialname, size(materialparameters), materialparameters, size(inpstate), &
                              inpstate, size(inpstrain2), inpstress, inpstrain2, dt, totaltime, outstress2, outstate)
            diff2 = outstress2(2) - inpstress(2)
            innercounter = 0
         end if

         modstrain = (diff2*inpstrain1(2) - diff1*inpstrain2(2))/(diff2 - diff1)
         inpstrain1 = inpstrain2
         diff1 = diff2
         inpstrain2(2) = modstrain
         inpstrain2(3) = modstrain

         call xmat_console(materialname, size(materialparameters), materialparameters, size(inpstate), &
                           inpstate, size(inpstrain2), inpstress, inpstrain2, dt, totaltime, outstress1, outstate)
         diff2 = outstress1(2) - inpstress(2)

         refstrain = inpstrain2
         innercounter = innercounter + 1
         strainidx = strainidx + 1

         ! Check for NaN entries
         if (diff2 /= diff2) then
            write(*, *) 'Error: NaN entries found'
            breakall = .True.
            exit minimize_difference
         end if
         if (strainidx > maxiter) then
            write(*, *) 'Error: Problem in triax loop'
            breakall = .True.
            exit minimize_difference
         end if
      end do minimize_difference
      if (breakall) then
         exit triax_compression
      end if

      strainidx = 0

      inpstress = outstress1
      inpstate = outstate

      sim_strains(:, idx + 1) = sim_strains(:, idx) + refstrain
      compared_strain = abs(sim_strains(1, idx))

      ! Writing: eps1 in %, eps_v in %, q in kPa
      write(filenr, '(f12.5, a, f12.5, a, f12.5)') 100.0_dp*sim_strains(1, idx), '   ', &
            100.0_dp*sum(sim_strains(1:3, idx)), '   ', -(outstress1(1) - outstress1(2))

      idx = idx + 1
      if (idx > maxiter) then
         write(*, *) 'Error: Maximum number of specified iterations reached'
         exit triax_compression
      end if
   end do triax_compression
   call cpu_time(endtime)
   print '("--outfilename--: ",f6.3,"s")', endtime - starttime
   close(filenr)
end program Triaxial_test
