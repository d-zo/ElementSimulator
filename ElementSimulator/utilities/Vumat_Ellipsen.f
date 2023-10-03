program Response_envelopes_test
   implicit none

   ! IMPORTANT: VUMAT allows single AND double precision
   integer, parameter :: dp = selected_real_kind(15)
   !
   integer, parameter :: nblock = 1
   integer, parameter :: ndir = 3
   integer, parameter :: nshr = 3
   integer, parameter :: nstatev = 20
   integer, parameter :: nfieldv = 1
   integer, parameter :: nprops = --numparameter--
   integer :: lanneal
   real(dp) :: stepTime, totalTime
   real(dp), dimension(1) :: charLength, density, tempOld, enerInternOld, enerInelasOld, tempNew, &
                             enerInternNew, enerInelasNew
   real(dp), dimension(1, 6) :: stretchOld, stretchNew
   real(dp), dimension(1, 3) :: relSpinInc
   real(dp), dimension(1, 9) :: defgradOld, defgradNew
   real(dp), dimension(1, 1) :: fieldOld, fieldNew
   real(dp), dimension(1, 1) :: coordMp
   !
   character(len=80) :: materialname
   real(dp), dimension(nprops) :: materialparameters
   real(dp), dimension(nstatev) :: statevariables
   real(dp), dimension(1, nstatev) :: inpstate, outstate
   real(dp), dimension(1, ndir + nshr) :: inpstress, outstress
   real(dp), dimension(1, ndir + nshr) :: inpstrain
   integer, parameter :: num_centeres = --envelopes_numstresses--
   real(dp), dimension(6*num_centeres) :: stresscenters
   integer, parameter :: num_angles = --envelopes_numangles--
   real(dp), parameter :: refstrain = --envelopes_refstrain--
   real(dp) :: dt, initial_voidratio, angle
   integer :: filenr, stat, icenter, iangle
   real(dp), parameter :: pi = 4.0_dp*atan(1.0_dp)
   real(dp), parameter :: isocomp_offset = atan(sqrt(2.0_dp))
   real(dp) :: starttime, endtime

   lanneal = 0
   stepTime = --starttime--
   totalTime = --starttime--

   coordMp = 0.0_dp
   charLength = 0.0_dp
   density = 0.0_dp
   relSpinInc = 0.0_dp
   tempOld = 0.0_dp
   stretchOld = 0.0_dp
   defgradOld = 0.0_dp
   fieldOld = 0.0_dp
   enerInternOld = 0.0_dp
   enerInelasOld = 0.0_dp
   tempNew = 0.0_dp
   stretchNew = 0.0_dp
   defgradNew = 0.0_dp
   fieldNew = 0.0_dp
   enerInternNew = 0.0_dp
   enerInelasNew = 0.0_dp

   ! Decide which constitutive model to use by materialname
   materialname = '--materialname--'

   ! List material parameters to be used
   initial_voidratio = --initialvoidratio--
   materialparameters = [ &
   --materialparameters--]

   ! Define initial state variables
   statevariables = 0.0_dp
   statevariables(1) = initial_voidratio

   ! State loads
   stresscenters = [&
   --envelopes_stresses--]

   ! Time increment to be used
   dt = --timeincrement--

   inpstate(1, :) = statevariables

   filenr = 20
   open(filenr, file="--outfilename--.csv", iostat=stat)
   if (stat /= 0) then
      write(*, *) "Access problem during write attempt"
      close(filenr)
      stop
   end if

   call cpu_time(starttime)
   do icenter = 1, num_centeres
      inpstress(1, :) = stresscenters(1+(icenter-1)*6:icenter*6)
      totaltime = --timeincrement--

      ! Also save the first (starting) point each time
      write(filenr, '(i4, a, f13.6, a, f13.6, a, f13.6)') icenter, '   ', &
         -inpstress(1, 1), '   ', -inpstress(1, 2), '   ', inpstate(1, 1)

      envelope_path: &
      do iangle = 1, num_angles
         angle = (real(iangle, dp) - 1.0_dp)/real(num_angles, dp)*2.0_dp*pi

         ! Add offset to start with isotropic compression
         inpstrain(1, :) = refstrain*[ &
            cos(angle+isocomp_offset), sin(angle+isocomp_offset)/sqrt(2.0_dp), sin(angle+isocomp_offset)/sqrt(2.0_dp), &
            0.0_dp, 0.0_dp, 0.0_dp]*dt

         call VUMAT(nblock, ndir, nshr, nstatev, nfieldv, nprops, lanneal, stepTime, totalTime, dt, &
                    materialname, coordMp, charLength, materialparameters, density, inpstrain, &
                    relSpinInc, tempOld, stretchOld, defgradOld, fieldOld, inpstress, inpstate, &
                    enerInternOld, enerInelasOld, tempNew, stretchNew, defgradNew, fieldNew, &
                    outstress, outstate, enerInternNew, enerInelasNew)

         write(filenr, '(i4, a, f13.6, a, f13.6, a, f13.6)') icenter, '   ', &
            -outstress(1, 1), '   ', -outstress(1, 2), '   ', outstate(1, 1)
      end do envelope_path
   end do
   call cpu_time(endtime)
   print '("--outfilename--: ",f6.3,"s")', endtime - starttime
   close(filenr)
end program Response_envelopes_test
