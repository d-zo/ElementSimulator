program Response_envelopes_test
   implicit none

   ! IMPORTANT: XMAT allows to set precision in routine but uses double precision as default
   integer, parameter :: dp = selected_real_kind(15)
   character(len=80) :: materialname
   real(dp), dimension(--numparameter--) :: materialparameters
   real(dp), dimension(20) :: statevariables, inpstate, outstate
   real(dp), dimension(6) :: inpstress, outstress
   real(dp), dimension(6) :: inpstrain
   integer, parameter :: num_centeres = --envelopes_numstresses--
   real(dp), dimension(6*num_centeres) :: stresscenters
   real(dp) :: dt, totaltime, initial_voidratio, angle
   integer :: filenr, stat, icenter, iangle
   integer, parameter :: num_angles = --envelopes_numangles--
   real(dp), parameter :: refstrain = --envelopes_refstrain--
   real(dp), parameter :: pi = 4.0_dp*atan(1.0_dp)
   real(dp), parameter :: isocomp_offset = atan(sqrt(2.0_dp))
   real(dp) :: starttime, endtime

   ! Decide which constitutive model to use by materialname
   materialname = '--materialname--'

   ! List material parameters to be used
   initial_voidratio = --initialvoidratio--
   materialparameters = [ &
   --materialparameters--]

   ! Define initial state variables
   statevariables = 0.0_dp
   statevariables(1) = initial_voidratio

   ! Time increment to be used
   dt = --timeincrement--

   ! State loads
   stresscenters = [&
   --envelopes_stresses--]


   inpstate = statevariables

   filenr = 20
   open(filenr, file="--outfilename--.csv", iostat=stat)
   if (stat /= 0) then
      write(*, *) "Access problem during write attempt"
      close(filenr)
      stop
   end if

   call cpu_time(starttime)
   do icenter = 1, num_centeres
      inpstress = stresscenters(1+(icenter-1)*6:icenter*6)
      totaltime = --starttime--

      ! Also save the first (starting) point each time
      write(filenr, '(i4, a, f13.6, a, f13.6, a, f13.6)') icenter, '   ', &
         -inpstress(1), '   ', -inpstress(2), '   ', inpstate(1)

      envelope_path: &
      do iangle = 1, num_angles
         angle = (real(iangle, dp) - 1.0_dp)/real(num_angles, dp)*2.0_dp*pi

         ! Add offset to start with isotropic compression
         inpstrain = refstrain*[ &
            cos(angle+isocomp_offset), sin(angle+isocomp_offset)/sqrt(2.0_dp), sin(angle+isocomp_offset)/2.0_dp, &
            0.0_dp, 0.0_dp, 0.0_dp]*dt

         call xmat_console(materialname, size(materialparameters), materialparameters, size(inpstate), &
                           inpstate, size(inpstrain), inpstress, inpstrain, dt, totaltime, outstress, outstate)

         write(filenr, '(i4, a, f13.6, a, f13.6, a, f13.6)') icenter, '   ', &
            -outstress(1), '   ', -outstress(2), '   ', outstate(1)
      end do envelope_path
   end do
   call cpu_time(endtime)
   print '("--outfilename--: ",f6.3,"s")', endtime - starttime
   close(filenr)
end program Response_envelopes_test
