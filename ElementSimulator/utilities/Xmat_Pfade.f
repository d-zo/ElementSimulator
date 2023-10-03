program Stresspath_test
   implicit none

   ! IMPORTANT: XMAT allows to set precision in routine but uses double precision as default
   integer, parameter :: dp = selected_real_kind(15)
   character(len=80) :: materialname
   real(dp), dimension(--numparameter--) :: materialparameters
   real(dp), dimension(20) :: statevariables, inpstate, outstate
   real(dp), dimension(6) :: pressure_origin, inpstress, outstress
   real(dp), dimension(6) :: inpstrain
   real(dp), dimension(2) :: minmax_stress
   real(dp) :: dt, totaltime, initial_voidratio, angle
   integer :: idx, filenr, stat, iangle
   integer, parameter :: maxiter = --maxiter--
   integer, parameter :: num_angles = --spider_numangles--
   real(dp), parameter :: refstrain = --spider_refstrain--
   real(dp), parameter :: pi = 4.0_dp*atan(1.0_dp)
   real(dp), parameter :: isocomp_offset = atan(sqrt(2.0_dp))
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

   ! Define initial state variables
   statevariables = 0.0_dp
   statevariables(1) = initial_voidratio

   ! State loads
   pressure_origin = [&
   --spider_refstress--]
   outstress = pressure_origin

   minmax_stress = [--spider_maxstress--]

   filenr = 20
   open(filenr, file="--outfilename--.csv", iostat=stat)
   if (stat /= 0) then
      write(*, *) "Access problem during write attempt"
      close(filenr)
      stop
   end if


   breakall = .False.

   call cpu_time(starttime)
   stress_path: &
   do iangle = 1, num_angles
      inpstress = pressure_origin
      outstress = pressure_origin
      inpstate = statevariables
      outstate = statevariables

      angle = (real(iangle, dp) - 1.0_dp)/real(num_angles, dp)*2.0_dp*pi

      ! Add offset to start with isotropic compression
      inpstrain = refstrain*[ &
         cos(angle+isocomp_offset), sin(angle+isocomp_offset)/sqrt(2.0_dp), sin(angle+isocomp_offset)/sqrt(2.0_dp), &
         0.0_dp, 0.0_dp, 0.0_dp]*dt
      totaltime = --starttime--
      idx = 1

      ! Also save the first (starting) point each time
      write(filenr, '(i4, a, f13.6, a, f13.6, a, f13.6)') nint(angle*180.0_dp/pi), '   ', &
         -outstress(1), '   ', -outstress(2), '   ', outstate(1)

      loading_loop: &
      do
         if (any(outstress(1:3) < minmax_stress(1)) .or. any(outstress(1:3) > minmax_stress(2))) then
            exit loading_loop
         end if
         call xmat_console(materialname, size(materialparameters), materialparameters, size(inpstate), &
                           inpstate, size(inpstrain), inpstress, inpstrain, dt, totaltime, outstress, outstate)

         write(filenr, '(i4, a, f13.6, a, f13.6, a, f13.6)') nint(angle*180.0_dp/pi), '   ', &
            -outstress(1), '   ', -outstress(2), '   ', outstate(1)

         inpstress = outstress
         inpstate = outstate
         totaltime = totaltime + dt
         idx = idx + 1
         if (idx > maxiter) then
            write(*, *) 'Maximum number of specified iterations reached'
            breakall = .True.
            exit loading_loop
         end if
      end do loading_loop
      if (breakall) then
         exit stress_path
      end if
   end do stress_path
   call cpu_time(endtime)
   print '("--outfilename--: ",f6.3,"s")', endtime - starttime
   close(filenr)
end program Stresspath_test
