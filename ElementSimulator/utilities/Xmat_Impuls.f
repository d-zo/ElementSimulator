program Singleresponse_test
   implicit none

   ! IMPORTANT: XMAT allows to set precision in routine but uses double precision as default
   integer, parameter :: dp = selected_real_kind(15)
   character(len=80) :: materialname
   real(dp), dimension(--numparameter--) :: materialparameters
   real(dp), dimension(20) :: statevariables, inpstate, outstate
   real(dp), dimension(6) :: stress, inpstress, outstress
   real(dp), dimension(6) :: strain, inpstrain
   real(dp) :: dt, totaltime, initial_voidratio
   integer :: filenr, stat
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

   ! Give initial stress and strain matrices (in vector form)
   stress = [--impuls_stress--]
   strain = [--impuls_strain--]*dt


   inpstress = stress
   outstress = stress
   inpstate = statevariables
   inpstrain = strain

   filenr = 20
   open(filenr, file="--outfilename--.csv", iostat=stat)
   if (stat /= 0) then
      write(*, *) "Access problem during write attempt"
      close(filenr)
      stop
   end if

   call cpu_time(starttime)
   write(filenr, '(f13.6, a, f13.6, a, f13.6, a, f13.6, a, f13.6, a, f13.6, a, f13.6)') &
      -inpstress(1), '   ', -inpstress(2), '   ', -inpstress(3), '   ', &
      -inpstress(4), '   ', -inpstress(5), '   ', -inpstress(6), '   ', inpstate(1)
   call xmat_console(materialname, size(materialparameters), materialparameters, size(inpstate), &
                     inpstate, size(inpstrain), inpstress, inpstrain, dt, totaltime, outstress, outstate)
   write(filenr, '(f13.6, a, f13.6, a, f13.6, a, f13.6, a, f13.6, a, f13.6, a, f13.6)') &
      -outstress(1), '   ', -outstress(2), '   ', -outstress(3), '   ', &
      -outstress(4), '   ', -outstress(5), '   ', -outstress(6), '   ', outstate(1)
   call cpu_time(endtime)
   print '("--outfilename--: ",f6.3,"s")', endtime - starttime
   close(filenr)
end program Singleresponse_test
