program Oedometric_test
   implicit none

   ! IMPORTANT: XMAT allows to set precision in routine but uses double precision as default
   integer, parameter :: dp = selected_real_kind(15)
   character(len=80) :: materialname
   real(dp), dimension(--numparameter--) :: materialparameters
   real(dp), dimension(20) :: statevariables, inpstate, outstate
   real(dp), dimension(6) :: stress, inpstress, outstress
   real(dp), dimension(6) :: strain, inpstrain
   real(dp), dimension(--pressure_entries--) :: oedo_pressure
   real(dp) :: dt, totaltime, sigma1, voidratio, numbersign
   integer :: istep, idx, filenr, stat
   integer, parameter :: maxiter = --maxiter--
   logical :: breakall
   real(dp) :: starttime, endtime

   ! Decide which constitutive model to use by materialname
   materialname = '--materialname--'

   ! List material parameters to be used
   voidratio = --initialvoidratio--
   materialparameters = [ &
   --materialparameters--]

   ! Time increment to be used
   dt = --timeincrement--
   totaltime = --starttime--

   ! Define initial state variables
   statevariables = 0.0_dp
   statevariables(1) = voidratio

   ! State loads
   oedo_pressure = [ &
   --oedo_pressure--]

   ! Give initial stress and strain matrices (in vector form)
   sigma1 = oedo_pressure(1)
   stress = [sigma1/2.0_dp, sigma1, sigma1/2.0_dp, 0.0_dp, 0.0_dp, 0.0_dp]
   strain = [0.0_dp, -0.05_dp, 0.0_dp, 0.0_dp, 0.0_dp, 0.0_dp]*dt


   inpstress = stress
   outstress = stress
   inpstate = statevariables

   filenr = 20
   open(filenr, file="--outfilename--.csv", iostat=stat)
   if (stat /= 0) then
      write(*, *) "Access problem during write attempt"
      close(filenr)
      stop
   end if

   ! Write output for start point as well
   write(filenr, '(f13.6, a, f13.6)') -stress(2), '   ', voidratio

   idx = 1
   breakall = .False.

   call cpu_time(starttime)
   loading_cycle: &
   do istep = 2, size(oedo_pressure)
      numbersign = (-1.0_dp)**istep
      inpstrain = numbersign*strain
      loading_loop: &
      do
         if (numbersign*outstress(2) < numbersign*oedo_pressure(istep)) then
            exit loading_loop
         end if
         call xmat_console(materialname, size(materialparameters), materialparameters, size(inpstate), &
                           inpstate, size(inpstrain), inpstress, inpstrain, dt, totaltime, outstress, outstate)
         ! FIXME: Check if any stress is complex or nan

         write(filenr, '(f13.6, a, f13.6)') -outstress(2), '   ', outstate(1)

         inpstress = outstress
         inpstate = outstate
         idx = idx + 1
         if (idx > maxiter) then
            write(*, *) 'Maximum number of specified iterations reached'
            breakall = .True.
            exit loading_loop
         end if
      end do loading_loop
      if (breakall) then
         exit loading_cycle
      end if
   end do loading_cycle
   call cpu_time(endtime)
   print '("--outfilename--: ",f6.3,"s")', endtime - starttime
   close(filenr)
end program Oedometric_test
